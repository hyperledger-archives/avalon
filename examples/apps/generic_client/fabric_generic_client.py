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
from avalon_sdk.connector.blockchains.fabric.fabric_worker_registry \
    import FabricWorkerRegistryImpl
from avalon_sdk.connector.blockchains.fabric.fabric_work_order \
    import FabricWorkOrderImpl
from avalon_sdk.connector.blockchains.common.contract_response \
    import ContractResponse

# Remove duplicate loggers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logger = logging.getLogger(__name__)

TCF_HOME = os.environ.get("TCF_HOME", "../../")


class GenericClient():
    """
    Generic client class to test end to end test
    for direct and proxy model.
    """

    def parse_command_line(self, args):
        """
        Parse command line arguments
        """
        parser = argparse.ArgumentParser()
        mutually_excl_group = parser.add_mutually_exclusive_group(
            required=True)
        parser.add_argument(
            "-c", "--config",
            help="The config file containing the Ethereum \
                contract information",
            type=str)
        mutually_excl_group.add_argument(
            "-u", "--uri",
            help="Direct API listener endpoint, \
                default is http://localhost:1947",
            type=str,
            default="http://avalon-listener:1947")
        mutually_excl_group.add_argument(
            "-b", "--blockchain",
            help="Blockchain type to use in proxy model",
            choices={"fabric", "ethereum"},
            type=str,
            default="fabric"
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

    def parse_config_file(self, config_file):
        # Parse config file and return a config dictionary.
        if config_file:
            conf_files = [config_file]
        else:
            conf_files = [TCF_HOME +
                          "/sdk/avalon_sdk/tcf_connector.toml"]
        confpaths = ["."]
        try:
            config = pconfig.parse_configuration_files(conf_files, confpaths)
            json.dumps(config)
        except pconfig.ConfigurationException as e:
            logger.error(str(e))
            config = None

        return config

    def retrieve_uri_from_registry_list(self, config):
        # Retrieve Http JSON RPC listener uri from registry
        logger.info("\n Retrieve Http JSON RPC listener uri from registry \n")
        # Get block chain type
        blockchain_type = config['blockchain']['type']
        if blockchain_type == "ethereum":
            worker_registry_list = EthereumWorkerRegistryListImpl(
                config)
        else:
            worker_registry_list = None
            logger.error("\n Worker registry list is currently "
                         "supported only for "
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

    def lookup_first_worker(self, blockchain_type,
                            worker_registry, jrpc_req_id):
        # Get first worker id from worker registry
        worker_id = None
        worker_lookup_result = worker_registry.worker_lookup(
            worker_type=WorkerType.TEE_SGX,
            id=jrpc_req_id
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
                worker_id = None
        elif blockchain_type and worker_lookup_result[0] > 0:
            # Iterate through all workers and find get
            # first active worker.
            for wo_id in worker_lookup_result[2]:
                wo_ret_result = worker_registry.worker_retrieve(wo_id)
                # First argument indicates status of worker.
                if wo_ret_result[0] == WorkerStatus.ACTIVE.value:
                    worker_id = wo_id
                    break
            return worker_id
        else:
            logger.error("ERROR: Failed to lookup worker")
            worker_id = None

        return worker_id

    def create_work_order_params(self, worker_id, workload_id, in_data,
                                 worker_encrypt_key, session_key, session_iv,
                                 verification_key):
        # Convert workloadId to hex
        workload_id = workload_id.encode("UTF-8").hex()
        self.work_order_id = secrets.token_hex(32)
        self.session_key = session_key
        self.session_iv = session_iv
        self.verification_key = verification_key
        requester_id = secrets.token_hex(32)
        requester_nonce = secrets.token_hex(16)
        # Create work order params
        wo_params = WorkOrderParams(
            self.work_order_id, worker_id, workload_id, requester_id,
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

    def create_work_order_receipt(self, wo_receipt, wo_params,
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

    def retrieve_work_order_receipt(self, wo_receipt,
                                    wo_params, jrpc_req_id):
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

    def verify_receipt_signature(self, receipt_update_retrieve):
        # Verify receipt signature
        sig_obj = signature.ClientSignature()
        status = sig_obj.verify_update_receipt_signature(
            receipt_update_retrieve["result"])
        if status == SignatureStatus.PASSED:
            logger.info(
                "Work order receipt retrieve signature verification " +
                "successful")
        else:
            logger.error(
                "Work order receipt retrieve signature verification failed!!")
            return False

        return True

    def verify_wo_res_signature(self, work_order_res,
                                worker_verification_key,
                                requester_nonce):
        # Verify work order result signature
        sig_obj = signature.ClientSignature()
        status = sig_obj.verify_signature(
            work_order_res, worker_verification_key,
            requester_nonce)
        if status == SignatureStatus.PASSED:
            logger.info("Signature verification Successful")
        else:
            logger.error("Signature verification Failed")
            return False

        return True

    def create_worker_registry_instance(self, blockchain_type, config):
        # create worker registry instance for direct/proxy model
        if blockchain_type == 'fabric':
            return FabricWorkerRegistryImpl(config)
        elif blockchain_type == 'ethereum':
            return EthereumWorkerRegistryImpl(config)
        else:
            return JRPCWorkerRegistryImpl(config)

    def create_work_order_instance(self, blockchain_type, config):
        # create work order instance for direct/proxy model
        if blockchain_type == 'fabric':
            return FabricWorkOrderImpl(config)
        elif blockchain_type == 'ethereum':
            return EthereumWorkOrderImpl(config)
        else:
            return JRPCWorkOrderImpl(config)

    def create_work_order_receipt_instance(self, blockchain_type, config):
        # create work order receipt instance for direct/proxy model
        if blockchain_type == 'fabric':
            return None
        elif blockchain_type == 'ethereum':
            # TODO need to implement
            return None
        else:
            return JRPCWorkOrderReceiptImpl(config)

    def get_work_order_result(self, blockchain_type, work_order,
                              work_order_id, jrpc_req_id):
        # Get the work order result for direct/proxy model
        res = work_order.work_order_get_result(
            work_order_id,
            jrpc_req_id
        )
        logger.info("Work order result {}".format(res))
        return res

    def get_worker_details(self, blockchain_type,
                           worker_registry, worker_id):
        # get the worker details for direct/proxy model.
        # Retrieve worker details
        jrpc_req_id = 342
        worker_retrieve_result = worker_registry.worker_retrieve(
            worker_id, jrpc_req_id
        )
        logger.info("\n Worker retrieve response: {}\n".format(
            json.dumps(worker_retrieve_result, indent=4)
        ))

        if worker_retrieve_result is None or "error" in worker_retrieve_result:
            logger.error("Unable to retrieve worker details\n")
            sys.exit(1)

        # Initializing Worker Object
        worker_obj1 = worker_details.SGXWorkerDetails()
        if blockchain_type:
            worker_obj1.load_worker(
                json.loads(worker_retrieve_result[4]))
        else:
            worker_obj1.load_worker(
                worker_retrieve_result["result"]["details"])

        return worker_obj1

    def handle_fabric_event(self, event, block_num, txn_id, status):
        """
        callback function for fabric event handler
        """
        payload = event['payload'].decode("utf-8")
        resp = json.loads(payload)
        wo_resp = json.loads(resp["workOrderResponse"])
        if wo_resp["workOrderId"] == self.work_order_id:
            logger.info("Work order response {}".format(wo_resp))
            self.verify_work_order_response(wo_resp)

    def verify_work_order_response(self, res):
        # Verify work order response signature
        sig_obj = signature.ClientSignature()
        status = sig_obj.verify_signature(res, self.verification_key)
        if status == SignatureStatus.PASSED:
            logger.info("Signature verification Successful")
        else:
            logger.error("Signature verification Failed")
        decrypted_res = crypto_utility.decrypted_response(
            res, self.session_key, self.session_iv)
        logger.info("\nDecrypted response:\n {}"
                    .format(decrypted_res))


def Main(args=None):
    generic_client = GenericClient()
    options = generic_client.parse_command_line(args)

    config = generic_client.parse_config_file(options.config)
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
            uri = generic_client.retrieve_uri_from_registry_list(config)
            if uri is None:
                logger.error("\n Unable to get http JSON RPC uri \n")
                sys.exit(-1)

    # Prepare worker
    # JRPC request id. Choose any integer value
    jrpc_req_id = 31
    worker_registry = generic_client.create_worker_registry_instance(
        blockchain, config)
    if not worker_id:
        # Get first worker from worker registry
        worker_id = generic_client.lookup_first_worker(
            blockchain, worker_registry, jrpc_req_id)
        if worker_id is None:
            logger.error("\n Unable to get worker \n")
            sys.exit(-1)

    # Create session key and iv to sign work order request
    session_key = crypto_utility.generate_key()
    session_iv = crypto_utility.generate_iv()

    s_key = session_key
    s_iv = session_iv
    logger.info("**********Worker details Updated with Worker ID" +
                "*********\n%s\n", worker_id)

    worker_obj = generic_client.get_worker_details(
        blockchain, worker_registry, worker_id)
    # Create work order
    verification_key = worker_obj.verification_key
    wo_params = generic_client.create_work_order_params(
        worker_id, workload_id,
        in_data, worker_obj.encryption_key,
        session_key, session_iv, verification_key)

    client_private_key = crypto_utility.generate_signing_keys()
    if requester_signature:
        # Add requester signature and requester verifying_key
        if wo_params.add_requester_signature(client_private_key) is False:
            logger.info("Work order request signing failed")
            exit(1)

    # Submit work order
    logger.info("Work order submit request : %s, \n \n ",
                wo_params.to_jrpc_string(jrpc_req_id))
    work_order = generic_client.create_work_order_instance(
        blockchain, config)
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
        response
    ))

    if blockchain is None:
        if "error" in response and response["error"]["code"] != \
                WorkOrderStatus.PENDING:
            sys.exit(1)
    else:
        if response != ContractResponse.SUCCESS:
            sys.exit(1)

    # Create receipt
    wo_receipt = generic_client.create_work_order_receipt_instance(
        blockchain, config)
    if show_receipt and wo_receipt:
        jrpc_req_id += 1
        generic_client.create_work_order_receipt(
            wo_receipt, wo_params,
            client_private_key, jrpc_req_id)

    # Retrieve work order result
    res = generic_client.get_work_order_result(
        blockchain, work_order,
        wo_params.get_work_order_id(),
        jrpc_req_id+1)

    # Check if result field is present in work order response
    if "result" in res:
        # Verify work order response signature
        if generic_client.verify_wo_res_signature(
                res['result'],
                worker_obj.verification_key,
                wo_params.get_requester_nonce()) is False:
            logger.error(
                "Work order response signature verification Failed")
            sys.exit(1)
        # Decrypt work order response
        if show_decrypted_output:
            decrypted_res = crypto_utility.decrypted_response(
                res['result'], session_key, session_iv)
            logger.info("\nDecrypted response:\n {}".format(decrypted_res))
    else:
        logger.error("\n Work order get result failed {}\n".format(
            res
        ))
        sys.exit(1)

    if show_receipt and wo_receipt:
        # Retrieve receipt
        jrpc_req_id += 1
        retrieve_wo_receipt \
            = generic_client.retrieve_work_order_receipt(
                wo_receipt,
                wo_params, jrpc_req_id)
        # Verify receipt signature
        if "result" in retrieve_wo_receipt:
            if generic_client.verify_receipt_signature(
                    retrieve_wo_receipt) is False:
                logger.error("Receipt signature verification Failed")
                sys.exit(1)
        else:
            logger.info("Work Order receipt retrieve failed")
            sys.exit(1)


# ---------------------------------------------------------------------------
Main()
