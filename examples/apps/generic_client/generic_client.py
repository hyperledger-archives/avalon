#! /usr/bin/env python3

# Copyright 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import json
import argparse
import logging
import secrets

import config.config as pconfig
import utility.logger as plogger
import utility.utility as utility
from utility.tcf_types import WorkerType
import worker.worker_details as worker_details
from work_order.work_order_params import WorkOrderParams
from connectors.direct.direct_json_rpc_api_connector \
    import DirectJsonRpcApiConnector
from error_code.error_status import WorkOrderStatus, ReceiptCreateStatus
import utility.signature as signature
from error_code.error_status import SignatureStatus
from work_order_receipt.work_order_receipt_request import WorkOrderReceiptRequest

# Remove duplicate loggers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logger = logging.getLogger(__name__)
TCFHOME = os.environ.get("TCF_HOME", "../../")


def ParseCommandLine(args):

    global worker_obj
    global worker_id
    global workload_id
    global in_data
    global config
    global mode
    global uri
    global address
    global show_receipt
    global show_decrypted_output
    global requester_signature

    parser = argparse.ArgumentParser()
    mutually_excl_group = parser.add_mutually_exclusive_group()
    parser.add_argument("-c", "--config",
        help="The config file containing the Ethereum contract information",
        type=str)
    mutually_excl_group.add_argument("-u", "--uri",
        help="Direct API listener endpoint, default is http://localhost:1947",
        default="http://localhost:1947",
        type=str)
    mutually_excl_group.add_argument("-a", "--address",
        help="an address (hex string) of the smart contract (e.g. Worker registry listing)",
        type=str)
    parser.add_argument("-m", "--mode",
        help="should be one of listing or registry (default)",
        default="registry",
        choices={"registry", "listing"},
        type=str)
    parser.add_argument("-w", "--worker_id",
        help="worker id (hex string) to use to submit a work order",
        type=str)
    parser.add_argument("-l", "--workload_id",
        help='workload id (hex string) for a given worker',
        type=str)
    parser.add_argument("-i", "--in_data",
        help='Input data',
        nargs="+",
        type=str)
    parser.add_argument("-r", "--receipt",
        help="If present, retrieve and display work order receipt",
        action='store_true')
    parser.add_argument("-o", "--decrypted_output",
        help="If present, display decrypted output as JSON",
        action='store_true')
    parser.add_argument("-rs", "--requester_signature",
        help="Enable requester signature for work order requests",
        action="store_true")
    options = parser.parse_args(args)

    if options.config:
        conf_files = [options.config]
    else:
        conf_files = [TCFHOME +
            "/examples/common/python/connectors/tcf_connector.toml"]
    confpaths = ["."]
    try:
        config = pconfig.parse_configuration_files(conf_files, confpaths)
        json.dumps(config)
    except pconfig.ConfigurationException as e:
        logger.error(str(e))
        sys.exit(-1)

    mode = options.mode

    uri = options.uri
    if uri:
        config["tcf"]["json_rpc_uri"] = uri

    address = options.address
    if address:
        if mode == "listing":
            config["ethereum"]["direct_registry_contract_address"] = \
                address
        elif mode == "registry":
            logger.error(
                "\n Only Worker registry listing address is supported." +
                "Worker registry address is unsupported \n")
            sys.exit(-1)

    worker_id = options.worker_id

    workload_id = options.workload_id
    if not workload_id:
        logger.error("\nWorkload id is mandatory\n")
        sys.exit(-1)

    in_data = options.in_data
    show_receipt = options.receipt
    show_decrypted_output = options.decrypted_output
    requester_signature = options.requester_signature


def Main(args=None):
    ParseCommandLine(args)

    config["Logging"] = {
        "LogFile": "__screen__",
        "LogLevel": "INFO"
    }

    plogger.setup_loggers(config.get("Logging", {}))
    sys.stdout = plogger.stream_to_logger(
        logging.getLogger("STDOUT"), logging.DEBUG)
    sys.stderr = plogger.stream_to_logger(
        logging.getLogger("STDERR"), logging.WARN)

    logger.info("***************** TRUSTED COMPUTE FRAMEWORK (TCF)" +
        " *****************")

    global direct_jrpc
    direct_jrpc = DirectJsonRpcApiConnector(config_file=None, config=config)

    global address
    if mode == "registry" and address:
        logger.error("\n Worker registry contract address is unsupported \n")
        sys.exit(-1)

    # Connect to registry list and retrieve registry
    global uri
    if not uri and mode == "listing":
        registry_list_instance = direct_jrpc.create_worker_registry_list(
            config
        )
        # Lookup returns tuple, first element is number of registries and
        # second is element is lookup tag and third is list of organization ids.
        registry_count, lookup_tag, registry_list = registry_list_instance.registry_lookup()
        logger.info("\n Registry lookup response: registry count: {} lookup tag: {} registry list: {}\n".format(
            registry_count, lookup_tag, registry_list
        ))
        if (registry_count == 0):
            logger.error("No registries found")
            sys.exit(1)
        # Retrieve the fist registry details.
        registry_retrieve_result = registry_list_instance.registry_retrieve(registry_list[0])
        logger.info("\n Registry retrieve response: {}\n".format(
            registry_retrieve_result
        ))
        config["tcf"]["json_rpc_uri"] = registry_retrieve_result[0]

    # Prepare worker
    req_id = 31
    global worker_id
    if not worker_id:
        worker_registry_instance = direct_jrpc.create_worker_registry(
            config
        )
        worker_lookup_result = worker_registry_instance.worker_lookup(
            worker_type=WorkerType.TEE_SGX, id=req_id
        )
        logger.info("\n Worker lookup response: {}\n".format(
            json.dumps(worker_lookup_result, indent=4)
        ))
        if "result" in worker_lookup_result and \
                "ids" in worker_lookup_result["result"].keys():
            if worker_lookup_result["result"]["totalCount"] != 0:
                worker_id = worker_lookup_result["result"]["ids"][0]
            else:
                logger.error("ERROR: No workers found")
                sys.exit(1)
        else:
            logger.error("ERROR: Failed to lookup worker")
            sys.exit(1)

    req_id += 1
    worker_retrieve_result = worker_registry_instance.worker_retrieve(
        worker_id, req_id
    )
    logger.info("\n Worker retrieve response: {}\n".format(
        json.dumps(worker_retrieve_result, indent=4)
    ))

    if "error" in worker_retrieve_result:
        logger.error("Unable to retrieve worker details\n")
        sys.exit(1)

    # Initializing Worker Object
    worker_obj = worker_details.SGXWorkerDetails()
    worker_obj.load_worker(worker_retrieve_result)

    logger.info("**********Worker details Updated with Worker ID" +
        "*********\n%s\n", worker_id)

    # Convert workloadId to hex
    global workload_id
    workload_id = workload_id.encode("UTF-8").hex()
    work_order_id = secrets.token_hex(32)
    requester_id = secrets.token_hex(32)
    session_iv = utility.generate_iv()
    session_key = utility.generate_key()
    requester_nonce = secrets.token_hex(16)
    # Create work order
    wo_params = WorkOrderParams(
        work_order_id, worker_id, workload_id, requester_id,
        session_key, session_iv, requester_nonce,
        result_uri=" ", notify_uri=" ",
        worker_encryption_key=worker_obj.encryption_key,
        data_encryption_algorithm="AES-GCM-256"
    )
    # Add worker input data
    global in_data

    for value in in_data:
        wo_params.add_in_data(value)

    # Encrypt work order request hash
    wo_params.add_encrypted_request_hash()

    private_key = utility.generate_signing_keys()
    if requester_signature:
        # Add requester signature and requester verifying_key
        if wo_params.add_requester_signature(private_key) is False:
            logger.info("Work order request signing failed")
            exit(1)
    # Submit work order
    logger.info("Work order submit request : %s, \n \n ",
        wo_params.to_string(req_id))
    work_order_instance = direct_jrpc.create_work_order(
        config
    )
    req_id += 1
    response = work_order_instance.work_order_submit(
        wo_params.get_params(),
        wo_params.get_in_data(),
        wo_params.get_out_data(),
        id=req_id
    )
    logger.info("Work order submit response : {}\n ".format(
        json.dumps(response, indent=4)
    ))

    if "error" in response and response["error"]["code"] != WorkOrderStatus.PENDING:
        sys.exit(1)

    wo_receipt_instance = direct_jrpc.create_work_order_receipt(
        config
    )
    # Create receipt
    if show_receipt:
        req_id += 1
        # Create work order receipt object using WorkOrderReceiptRequest class
        wo_request = json.loads(wo_params.to_string(req_id))
        wo_receipt_obj = WorkOrderReceiptRequest()
        wo_create_receipt = wo_receipt_obj.create_receipt(
            wo_request,
            ReceiptCreateStatus.PENDING.value,
            private_key
        )
        logger.info("Work order create receipt request : {} \n \n ".format(
            json.dumps(wo_create_receipt, indent=4)
        ))
        # Submit work order create receipt jrpc request
        wo_receipt_resp = wo_receipt_instance.work_order_receipt_create(
            wo_create_receipt["workOrderId"],
            wo_create_receipt["workerServiceId"],
            wo_create_receipt["workerId"],
            wo_create_receipt["requesterId"],
            wo_create_receipt["receiptCreateStatus"],
            wo_create_receipt["workOrderRequestHash"],
            wo_create_receipt["requesterGeneratedNonce"],
            wo_create_receipt["requesterSignature"],
            wo_create_receipt["signatureRules"],
            wo_create_receipt["receiptVerificationKey"],
            req_id
        )
        logger.info("Work order create receipt response : {} \n \n ".format(
            wo_receipt_resp
        ))

    # Retrieve result
    req_id += 1
    res = work_order_instance.work_order_get_result(
        work_order_id,
        req_id
    )

    logger.info("Work order get result : {}\n ".format(
        json.dumps(res, indent=4)
    ))
    sig_obj = signature.ClientSignature()
    if "result" in res:
        status = sig_obj.verify_signature(res, worker_obj.verification_key)
        try:
            if status == SignatureStatus.PASSED:
                logger.info("Signature verification Successful")
                decrypted_res = utility.decrypted_response(
                    res, session_key, session_iv)
                if show_decrypted_output:
                    logger.info("\nDecrypted response:\n {}"
                        .format(decrypted_res))
            else:
                logger.error("Signature verification Failed")
                sys.exit(1)
        except:
            logger.error("ERROR: Failed to decrypt response")
            sys.exit(1)
    else:
        logger.error("\n Work order get result failed {}\n".format(
            res
        ))
        sys.exit(1)

    if show_receipt:
        # Retrieve receipt
        req_id += 1
        receipt_res = wo_receipt_instance.work_order_receipt_retrieve(
            work_order_id,
            id=req_id
        )
        logger.info("\n Retrieve receipt response:\n {}".format(
            json.dumps(receipt_res, indent=4)
        ))
        # Retrieve last update to receipt by passing 0xFFFFFFFF
        req_id += 1
        receipt_update_retrieve = wo_receipt_instance.work_order_receipt_update_retrieve(
            work_order_id,
            None,
            1 << 32,
            id=req_id
        )
        logger.info("\n Last update to receipt receipt is:\n {}".format(
            json.dumps(receipt_update_retrieve, indent=4)
        ))
        status = sig_obj.verify_update_receipt_signature(receipt_update_retrieve)
        if status == SignatureStatus.PASSED:
            logger.info("Work order receipt retrieve signature verification Successful")
        else:
            logger.info("Work order receipt retrieve signature verification failed!!")
            sys.exit(1)


# -----------------------------------------------------------------------------
Main()
