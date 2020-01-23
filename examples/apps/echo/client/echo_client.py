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
import base64
import secrets

import config.config as pconfig
import utility.logger as plogger
import crypto_utils.crypto_utility as utility
from avalon_sdk.worker.worker_details import WorkerType
import avalon_sdk.worker.worker_details as worker
from avalon_sdk.work_order.work_order_params import WorkOrderParams
from avalon_sdk.direct.avalon_direct_client \
    import AvalonDirectClient
import crypto_utils.crypto.crypto as crypto
from error_code.error_status import WorkOrderStatus, ReceiptCreateStatus
import crypto_utils.signature as signature
import utility.hex_utils as hex_utils
from error_code.error_status import SignatureStatus
from avalon_sdk.work_order_receipt.work_order_receipt \
    import WorkOrderReceiptRequest

# Remove duplicate loggers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logger = logging.getLogger(__name__)
TCFHOME = os.environ.get("TCF_HOME", "../../../../")


def ParseCommandLine(args):
    global worker_obj
    global worker_id
    global message
    global config
    global off_chain
    global requester_signature
    global input_data_hash

    parser = argparse.ArgumentParser()
    use_service = parser.add_mutually_exclusive_group()
    parser.add_argument(
        "-c", "--config",
        help="the config file containing the Ethereum contract information",
        type=str)
    use_service.add_argument(
        "-r", "--registry-list",
        help="the Ethereum address of the registry list",
        type=str)

    use_service.add_argument(
        "-s", "--service-uri",
        help="skip URI lookup and send to specified URI",
        type=str)

    use_service.add_argument(
        "-o", "--off-chain",
        help="skip URI lookup and use the registry in the config file",
        action="store_true")

    parser.add_argument(
        "-w", "--worker-id",
        help="skip worker lookup and retrieve specified worker",
        type=str)
    parser.add_argument(
        "-m", "--message",
        help='text message to be included in the JSON request payload',
        type=str)
    parser.add_argument(
        "-rs", "--requester-signature",
        help="Enable requester signature for work order requests",
        action="store_true")
    parser.add_argument(
        "-dh", "--data-hash",
        help="Enable input data hash for work order requests",
        action="store_true")

    options = parser.parse_args(args)
    if options.config:
        conf_files = [options.config]
    else:
        conf_files = [TCFHOME +
                      "/sdk/avalon_sdk/tcf_connector.toml"]
    confpaths = ["."]
    try:
        config = pconfig.parse_configuration_files(conf_files, confpaths)
        config_json_str = json.dumps(config)
    except pconfig.ConfigurationException as e:
        logger.error(str(e))
        sys.exit(-1)

    # Whether or not to connect to the registry list on the blockchain
    off_chain = False

    if options.registry_list:
        config["ethereum"]["direct_registry_contract_address"] = \
            options.registry_list

    if options.service_uri:
        config["tcf"]["json_rpc_uri"] = options.service_uri
        off_chain = True

    if options.off_chain:
        off_chain = True

    global direct_jrpc
    direct_jrpc = AvalonDirectClient(config=config)

    requester_signature = options.requester_signature
    input_data_hash = options.data_hash
    worker_id = options.worker_id
    message = options.message
    if options.message is None or options.message == "":
        message = "Test Message"

    # Initializing Worker Object
    worker_obj = worker.SGXWorkerDetails()


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

    logger.info("***************** AVALON *****************")

    # Connect to registry list and retrieve registry
    if not off_chain:
        registry_list_instance = direct_jrpc.get_worker_registry_list_instance(
        )

        # Lookup returns tuple, first element is number of registries and
        # second is element is lookup tag and
        # third is list of organization ids.
        registry_count, lookup_tag, registry_list = \
            registry_list_instance.registry_lookup()
        logger.info("\n Registry lookup response: registry count: {} " +
                    "lookup tag: {} registry list: {}\n".format(
                        registry_count, lookup_tag, registry_list))
        if (registry_count == 0):
            logger.warn("No registries found")
            sys.exit(1)

        # Retrieve the first registry details.
        registry_retrieve_result = registry_list_instance.registry_retrieve(
            registry_list[0])
        logger.info("\n Registry retrieve response: {}\n".format(
            registry_retrieve_result
        ))
        config["tcf"]["json_rpc_uri"] = registry_retrieve_result[0]

    # Prepare worker
    req_id = 31
    global worker_id
    worker_registry_instance = direct_jrpc.get_worker_registry_instance()
    if not worker_id:
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
    worker_obj.load_worker(worker_retrieve_result)

    logger.info("**********Worker details Updated with Worker ID" +
                "*********\n%s\n", worker_id)

    # Convert workloadId to hex
    workload_id = "echo-result".encode("UTF-8").hex()
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
    if input_data_hash:
        # Compute data hash for data params inData
        data_hash = utility.compute_data_hash(message)
        # Convert data_hash to hex
        data_hash = hex_utils.byte_array_to_hex_str(data_hash)
        wo_params.add_in_data(message, data_hash)
    else:
        wo_params.add_in_data(message)

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
                wo_params.to_jrpc_string(req_id))
    work_order_instance = direct_jrpc.get_work_order_instance()
    req_id += 1
    response = work_order_instance.work_order_submit(
        wo_params.get_work_order_id(),
        wo_params.get_worker_id(),
        wo_params.get_requester_id(),
        wo_params.to_string(),
        id=req_id
    )
    logger.info("Work order submit response : {}\n ".format(
        json.dumps(response, indent=4)
    ))

    if "error" in response and response["error"]["code"] != \
            WorkOrderStatus.PENDING:
        sys.exit(1)

    # Create receipt
    wo_receipt_instance = direct_jrpc.get_work_order_receipt_instance()
    req_id += 1
    # Create work order receipt object using WorkOrderReceiptRequest class
    wo_request = json.loads(wo_params.to_jrpc_string(req_id))
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
                logger.info(
                    "Work order response signature verification Successful")
                decrypted_res = utility.decrypted_response(
                    res, session_key, session_iv)
                logger.info("\nDecrypted response:\n {}".format(decrypted_res))
                if input_data_hash:
                    decrypted_data = decrypted_res[0]["data"]
                    data_hash_in_resp = (decrypted_res[0]["dataHash"]).upper()
                    # Verify data hash in response
                    if utility.verify_data_hash(
                            decrypted_data, data_hash_in_resp) is False:
                        sys.exit(1)
            else:
                logger.info("Signature verification Failed")
                sys.exit(1)
        except Exception as err:
            logger.error("ERROR: Failed to decrypt response: %s", str(err))
            sys.exit(1)
    else:
        logger.info("\n Work order get result failed {}\n".format(
            res
        ))
        sys.exit(1)

    # Retrieve receipt
    receipt_res = wo_receipt_instance.work_order_receipt_retrieve(
        work_order_id,
        id=req_id
    )

    logger.info("\n Retrieve receipt response:\n {}".format(
        json.dumps(receipt_res, indent=4)
    ))

    # Retrieve last update to receipt by passing 0xFFFFFFFF
    req_id += 1
    receipt_update_retrieve = \
        wo_receipt_instance.work_order_receipt_update_retrieve(
            work_order_id,
            None,
            1 << 32,
            id=req_id)
    logger.info("\n Last update to receipt receipt is:\n {}".format(
        json.dumps(receipt_update_retrieve, indent=4)
    ))
    status = sig_obj.verify_update_receipt_signature(receipt_update_retrieve)
    if status == SignatureStatus.PASSED:
        logger.info(
            "Work order receipt retrieve signature verification Successful")
    else:
        logger.info(
            "Work order receipt retrieve signature verification failed!!")
        sys.exit(1)
    # Receipt lookup based on requesterId
    req_id += 1
    receipt_lookup_res = wo_receipt_instance.work_order_receipt_lookup(
        requester_id=requester_id,
        id=req_id
    )
    logger.info("\n Work order receipt lookup response :\n {}".format(
        json.dumps(receipt_lookup_res, indent=4)
    ))


# ------------------------------------------------------------------------------
Main()
