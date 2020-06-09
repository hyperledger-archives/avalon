#! /usr/bin/env python3

# Copyright 2020 Intel Corporation
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
import random
import argparse
import logging
import secrets
import asyncio

import config.config as pconfig
import utility.logger as plogger
import avalon_crypto_utils.crypto_utility as crypto_utility
from avalon_sdk.worker.worker_details import WorkerType, WorkerStatus
import avalon_sdk.worker.worker_details as worker_details
from avalon_sdk.work_order.work_order_params import WorkOrderParams
from avalon_sdk.connector.blockchains.ethereum.ethereum_worker_registry_list \
    import EthereumWorkerRegistryListImpl
from avalon_sdk.connector.direct.jrpc.jrpc_worker_registry import \
    JRPCWorkerRegistryImpl
from avalon_sdk.connector.direct.jrpc.jrpc_work_order import \
    JRPCWorkOrderImpl
from avalon_sdk.connector.direct.jrpc.jrpc_work_order_receipt \
    import JRPCWorkOrderReceiptImpl
from error_code.error_status import WorkOrderStatus, ReceiptCreateStatus
import avalon_crypto_utils.signature as signature
from error_code.error_status import SignatureStatus
from avalon_sdk.work_order_receipt.work_order_receipt \
    import WorkOrderReceiptRequest
from avalon_sdk.connector.blockchains.ethereum.ethereum_worker_registry \
    import EthereumWorkerRegistryImpl
from avalon_sdk.connector.blockchains.ethereum.ethereum_work_order \
    import EthereumWorkOrderProxyImpl


# Remove duplicate loggers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logger = logging.getLogger(__name__)
TCFHOME = os.environ.get("TCF_HOME", "../../")
WAIT_TIME = 31536000
verification_key = None
s_key = None
s_iv = None
wo_id = ''


def _parse_command_line(args):

    parser = argparse.ArgumentParser()
    mutually_excl_group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument(
        "-c", "--config",
        help="The config file containing the Ethereum contract information",
        type=str)
    mutually_excl_group.add_argument(
        "-u", "--uri",
        help="Direct API listener endpoint, default is http://localhost:1947",
        type=str,
        default="http://avalon-listener:1947")
    mutually_excl_group.add_argument(
        "-b", "--blockchain",
        help="Blockchain type to use in proxy model",
        choices={"fabric", "ethereum"},
        type=str
    )
    parser.add_argument(
        "-a", "--address",
        help="an address (hex string) of the smart contract " +
        "(e.g. Worker registry listing)",
        type=str)
    parser.add_argument(
        "-m", "--mode",
        help="should be one of listing or registry (default)",
        default="registry",
        choices={"registry", "listing"},
        type=str)
    parser.add_argument(
        "-w", "--worker_id",
        help="worker id (hex string) to use to submit a work order",
        type=str)
    parser.add_argument(
        "-l", "--workload_id",
        help='workload id (hex string) for a given worker',
        type=str)
    parser.add_argument(
        "-i", "--in_data",
        help='Input data',
        nargs="+",
        type=str)
    parser.add_argument(
        "-r", "--receipt",
        help="If present, retrieve and display work order receipt",
        action='store_true')
    parser.add_argument(
        "-o", "--decrypted_output",
        help="If present, display decrypted output as JSON",
        action='store_true')
    parser.add_argument(
        "-rs", "--requester_signature",
        help="Enable requester signature for work order requests",
        action="store_true")
    options = parser.parse_args(args)

    return options


def _parse_config_file(config_file):
    # Parse config file and return a config dictionary.
    if config_file:
        conf_files = [config_file]
    else:
        conf_files = [TCFHOME +
                      "/sdk/avalon_sdk/tcf_connector.toml"]
    confpaths = ["."]
    try:
        config = pconfig.parse_configuration_files(conf_files, confpaths)
        json.dumps(config)
    except pconfig.ConfigurationException as e:
        logger.error(str(e))
        config = None

    return config


def _retrieve_uri_from_registry_list(config):
    # Retrieve Http JSON RPC listener uri from registry
    logger.info("\n Retrieve Http JSON RPC listener uri from registry \n")
    # Get block chain type
    blockchain_type = config['blockchain']['type']
    if blockchain_type == "ethereum":
        worker_registry_list = EthereumWorkerRegistryListImpl(
            config)
    else:
        worker_registry_list = None
        logger.error("\n Worker registry list is currently supported only for "
                     "ethereum block chain \n")
        return None

    # Lookup returns tuple, first element is number of registries and
    # second is element is lookup tag and
    # third is list of organization ids.
    registry_count, lookup_tag, registry_list = \
        worker_registry_list.registry_lookup()
    logger.info("\n Registry lookup response: registry count: {} "
                "lookup tag: {} registry list: {}\n".format(
                    registry_count, lookup_tag, registry_list))
    if (registry_count == 0):
        logger.error("No registries found")
        return None
    # Retrieve the fist registry details.
    registry_retrieve_result = worker_registry_list.registry_retrieve(
        registry_list[0])
    logger.info("\n Registry retrieve response: {}\n".format(
        registry_retrieve_result
    ))

    return registry_retrieve_result[0]


def _create_work_order_params(worker_id, workload_id, in_data,
                              worker_encrypt_key, session_key, session_iv):
    # Convert workloadId to hex
    workload_id = workload_id.encode("UTF-8").hex()
    work_order_id = secrets.token_hex(32)
    requester_id = secrets.token_hex(32)
    requester_nonce = secrets.token_hex(16)
    # Create work order params
    wo_params = WorkOrderParams(
        work_order_id, worker_id, workload_id, requester_id,
        session_key, session_iv, requester_nonce,
        result_uri=" ", notify_uri=" ",
        worker_encryption_key=worker_encrypt_key,
        data_encryption_algorithm="AES-GCM-256"
    )
    # Add worker input data
    for value in in_data:
        wo_params.add_in_data(value)

    # Encrypt work order request hash
    wo_params.add_encrypted_request_hash()

    return wo_params


def _create_work_order_receipt(wo_receipt, wo_params,
                               client_private_key, jrpc_req_id):
    # Create work order receipt object using WorkOrderReceiptRequest class
    # This will send WorkOrderReceiptCreate json rpc request
    wo_request = json.loads(wo_params.to_jrpc_string(jrpc_req_id))
    wo_receipt_request_obj = WorkOrderReceiptRequest()
    wo_create_receipt = wo_receipt_request_obj.create_receipt(
        wo_request,
        ReceiptCreateStatus.PENDING.value,
        client_private_key
    )
    logger.info("Work order create receipt request : {} \n \n ".format(
        json.dumps(wo_create_receipt, indent=4)
    ))
    # Submit work order create receipt jrpc request
    wo_receipt_resp = wo_receipt.work_order_receipt_create(
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
        jrpc_req_id
    )
    logger.info("Work order create receipt response : {} \n \n ".format(
        wo_receipt_resp
    ))


def _retrieve_work_order_receipt(wo_receipt, wo_params, jrpc_req_id):
    # Retrieve work order receipt
    receipt_res = wo_receipt.work_order_receipt_retrieve(
        wo_params.get_work_order_id(),
        id=jrpc_req_id
    )
    logger.info("\n Retrieve receipt response:\n {}".format(
        json.dumps(receipt_res, indent=4)
    ))
    # Retrieve last update to receipt by passing 0xFFFFFFFF
    jrpc_req_id += 1
    receipt_update_retrieve = \
        wo_receipt.work_order_receipt_update_retrieve(
            wo_params.get_work_order_id(),
            None,
            1 << 32,
            id=jrpc_req_id)
    logger.info("\n Last update to receipt receipt is:\n {}".format(
        json.dumps(receipt_update_retrieve, indent=4)
    ))

    return receipt_update_retrieve


def _verify_receipt_signature(receipt_update_retrieve):
    # Verify receipt signature
    sig_obj = signature.ClientSignature()
    status = sig_obj.verify_update_receipt_signature(
        receipt_update_retrieve)
    if status == SignatureStatus.PASSED:
        logger.info(
            "Work order receipt retrieve signature verification " +
            "successful")
    else:
        logger.error(
            "Work order receipt retrieve signature verification failed!!")
        return False

    return True


def _verify_wo_res_signature(work_order_res,
                             worker_verification_key,
                             requester_nonce):
    # Verify work order result signature
    sig_obj = signature.ClientSignature()
    status = sig_obj.verify_signature(work_order_res,
                                      worker_verification_key,
                                      requester_nonce)
    if status == SignatureStatus.PASSED:
        logger.info("Signature verification Successful")
    else:
        logger.error("Signature verification Failed")
        return False

    return True


def _create_worker_registry_instance(blockchain_type, config):
    # create worker registry instance for direct/proxy model
    if blockchain_type == 'ethereum':
        return EthereumWorkerRegistryImpl(config)
    else:
        return JRPCWorkerRegistryImpl(config)


def _create_work_order_instance(blockchain_type, config):
    # create work order instance for direct/proxy model
    if blockchain_type == 'ethereum':
        return EthereumWorkOrderProxyImpl(config)
    else:
        return JRPCWorkOrderImpl(config)


def _create_work_order_receipt_instance(blockchain_type, config):
    # create work order receipt instance for direct/proxy model
    if blockchain_type == 'ethereum':
        # TODO need to implement
        return None
    else:
        return JRPCWorkOrderReceiptImpl(config)


def _get_work_order_result(work_order, work_order_id,
                           jrpc_req_id):
    # Get the work order result for direct/proxy model

    res = work_order.work_order_get_result(
        work_order_id, jrpc_req_id
    )
    return res


def _get_first_active_worker(worker_registry, worker_id, config):
    """
    This function looks up all the workers registered. It then filters
    this data to get the first worker that has Active status.
    """
    jrpc_req_id = random.randint(0, 100000)
    worker_retrieve_result = None
    if not worker_id:
        # Lookup all worker id present on  blockchain
        worker_lookup_result = worker_registry.worker_lookup(
            WorkerType.TEE_SGX,
            config["WorkerConfig"]["OrganizationId"],
            config["WorkerConfig"]["ApplicationTypeId"],
            jrpc_req_id
        )
        logger.info("\n Worker lookup response: {}\n".format(
            json.dumps(worker_lookup_result, indent=4)
        ))
        if "result" in worker_lookup_result and \
                "ids" in worker_lookup_result["result"].keys():
            if worker_lookup_result["result"]["totalCount"] != 0:
                worker_ids = worker_lookup_result["result"]["ids"]
                # Filter workers by status(active) field
                # Return first worker whose status is active
                for w_id in worker_ids:
                    jrpc_req_id += 1
                    worker = worker_registry\
                        .worker_retrieve(w_id, jrpc_req_id)
                    if worker["result"]["status"] == WorkerStatus.ACTIVE.value:
                        worker_retrieve_result = worker
                        worker_id = w_id
                        break
            else:
                logger.error("No workers found")
        else:
            logger.error("Failed to lookup worker")
    else:
        worker_retrieve_result = worker_registry\
            .worker_retrieve(worker_id, jrpc_req_id)

    if worker_retrieve_result is None:
        logger.error("Failed to lookup worker")
        return None, None
    # Initializing Worker Object
    logger.info("\n Worker retrieve response: {}\n".format(
        json.dumps(worker_retrieve_result, indent=4)
    ))
    worker_obj = worker_details.SGXWorkerDetails()
    worker_obj.load_worker(worker_retrieve_result["result"]["details"])

    return worker_obj, worker_id


def Main(args=None):
    options = _parse_command_line(args)

    config = _parse_config_file(options.config)
    if config is None:
        logger.error("\n Error in parsing config file: {}\n".format(
            options.config
        ))
        sys.exit(-1)

    # mode should be one of listing or registry (default)
    mode = options.mode

    # Http JSON RPC listener uri
    uri = options.uri
    if uri:
        config["tcf"]["json_rpc_uri"] = uri
    # Setting blockchain type
    # if blockchain parameter is not passed, set to None
    # and None implies direct mode.
    blockchain = options.blockchain
    if blockchain:
        config['blockchain']['type'] = blockchain

    # Address of smart contract
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

    # worker id
    worker_id = options.worker_id

    # work load id of worker
    workload_id = options.workload_id
    if not workload_id:
        logger.error("\nWorkload id is mandatory\n")
        sys.exit(-1)

    # work order input data
    in_data = options.in_data

    # show receipt in output
    show_receipt = options.receipt

    # show decrypted result in output
    show_decrypted_output = options.decrypted_output

    # requester signature for work order requests
    requester_signature = options.requester_signature

    # setup logging
    config["Logging"] = {
        "LogFile": "__screen__",
        "LogLevel": "INFO"
    }

    plogger.setup_loggers(config.get("Logging", {}))
    sys.stdout = plogger.stream_to_logger(
        logging.getLogger("STDOUT"), logging.DEBUG)
    sys.stderr = plogger.stream_to_logger(
        logging.getLogger("STDERR"), logging.WARN)

    logger.info("******* Hyperledger Avalon Generic client *******")

    if mode == "registry" and address:
        logger.error("\n Worker registry contract address is unsupported \n")
        sys.exit(-1)

    # Retrieve JSON RPC uri from registry list for direct mode.
    if not uri and mode == "listing":
        if not blockchain:
            uri = _retrieve_uri_from_registry_list(config)
            if uri is None:
                logger.error("\n Unable to get http JSON RPC uri \n")
                sys.exit(-1)

    # Prepare worker
    worker_registry = _create_worker_registry_instance(blockchain, config)
    worker_obj, worker_id = _get_first_active_worker(worker_registry,
                                                     worker_id, config)
    if worker_obj is None:
        logger.error("Cannot proceed without a valid worker")
        sys.exit(-1)
    # Create session key and iv to sign work order request
    session_key = crypto_utility.generate_key()
    session_iv = crypto_utility.generate_iv()

    s_key = session_key
    s_iv = session_iv
    logger.info("**********Worker details Updated with Worker ID" +
                "*********\n%s\n", worker_id)

    # Create work order
    verification_key = worker_obj.verification_key
    wo_params = _create_work_order_params(worker_id, workload_id,
                                          in_data, worker_obj.encryption_key,
                                          session_key, session_iv)

    client_private_key = crypto_utility.generate_signing_keys()
    if requester_signature:
        # Add requester signature and requester verifying_key
        if wo_params.add_requester_signature(client_private_key) is False:
            logger.info("Work order request signing failed")
            exit(1)

    # Submit work order
    jrpc_req_id = random.randint(0, 100000)
    logger.info("Work order submit request : %s, \n \n ",
                wo_params.to_jrpc_string(jrpc_req_id))
    work_order = _create_work_order_instance(blockchain, config)
    jrpc_req_id += 1
    wo_id = wo_params.get_worker_id()
    response = work_order.work_order_submit(
        wo_params.get_work_order_id(),
        wo_params.get_worker_id(),
        wo_params.get_requester_id(),
        wo_params.to_string(),
        id=jrpc_req_id
    )
    logger.info("Work order submit response : {}\n ".format(
        json.dumps(response, indent=4)
    ))

    if blockchain is None:
        if "error" in response and response["error"]["code"] != \
                WorkOrderStatus.PENDING:
            sys.exit(1)
    else:
        if response != 0:
            sys.exit(1)

    # Create receipt
    wo_receipt = _create_work_order_receipt_instance(blockchain, config)
    if show_receipt and wo_receipt:
        jrpc_req_id += 1
        _create_work_order_receipt(wo_receipt, wo_params,
                                   client_private_key, jrpc_req_id)

    # Retrieve work order result
    res = _get_work_order_result(work_order, wo_params.get_work_order_id(),
                                 jrpc_req_id+1)
    if res:
        logger.info("Work order get result : {}\n ".format(
            json.dumps(res, indent=4)
        ))

        # Check if result field is present in work order response
        if "result" in res:
            # Verify work order response signature
            if _verify_wo_res_signature(res['result'],
                                        worker_obj.verification_key,
                                        wo_params.get_requester_nonce()) \
                                            is False:
                logger.error(
                    "Work order response signature verification Failed")
                sys.exit(1)
            # Decrypt work order response
            if show_decrypted_output:
                decrypted_res = crypto_utility.decrypted_response(
                    res['result'], session_key, session_iv)
                logger.info("\nDecrypted response:\n {}"
                            .format(decrypted_res))
        else:
            logger.error("\n Work order get result failed {}\n".format(
                res
            ))
            sys.exit(1)

    if show_receipt and wo_receipt:
        # Retrieve receipt
        jrpc_req_id += 1
        retrieve_wo_receipt \
            = _retrieve_work_order_receipt(wo_receipt,
                                           wo_params, jrpc_req_id)
        # Verify receipt signature
        if _verify_receipt_signature(retrieve_wo_receipt) is False:
            logger.error("Receipt signature verification Failed")
            sys.exit(1)


# -----------------------------------------------------------------------------
Main()
