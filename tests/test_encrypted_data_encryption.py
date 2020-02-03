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
import random
import json
import argparse
import logging
import base64

import config.config as pconfig
import utility.logger as plogger
from avalon_sdk.http_client.http_jrpc_client import HttpJrpcClient
import crypto_utils.crypto_utility as utility
import worker.worker_details as worker
import json_rpc_request.json_rpc_request as jrpc_request
from connectors.direct.direct_adaptor_factory_wrapper \
    import DirectAdaptorFactoryWrapper

# Remove duplicate loggers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logger = logging.getLogger(__name__)

TCFHOME = os.environ.get("TCF_HOME", "../../")


def ParseCommandLine(args):

        global worker_obj
        global worker_id
        global message
        global config
        global off_chain

        parser = argparse.ArgumentParser()
        use_service = parser.add_mutually_exclusive_group()
        parser.add_argument("-c", "--config",
                            help="the config file containing the Ethereum " + "
                            "contract information",
                            type=str)
        use_service.add_argument("-r", "--registry-list",
                                 help="the Ethereum address of the " +
                                 "registry list",
                                 type=str)
        use_service.add_argument("-s", "--service-uri",
                                 help="skip URI lookup and send to " +
                                 "specified URI",
                                 type=str)
        use_service.add_argument("-o", "--off-chain",
                                 help="skip URI lookup and use the registry " +
                                 "in the config file",
                                 action="store_true")
        parser.add_argument("-w", "--worker-id",
                            help="skip worker lookup and retrieve " +
                            "specified worker",
                            type=str)
        parser.add_argument("-m", "--message",
                            help="text message to be included in the " +
                            "JSON request payload",
                            type=str)

        options = parser.parse_args(args)

        if options.config:
            conffiles = [options.config]
        else:
            conffiles = [TCFHOME + "/sdk/avalon-sdk/" +
                         "tcf_connector.toml"]
        confpaths = ["."]
        try:
                config = pconfig.parse_configuration_files(
                    conffiles, confpaths)
                json.dumps(config)
        except pconfig.ConfigurationException as e:
                logger.error(str(e))
                sys.exit(-1)

        global direct_wrapper
        direct_wrapper = DirectAdaptorFactoryWrapper(conffiles[0])

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

        worker_id = options.worker_id
        message = options.message
        if options.message is None or options.message == "":
                message = "Hello world"

        # Initializing Worker Object
        worker_obj = worker.WorkerDetails()


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
                direct_wrapper.init_worker_registry_list(config)
                registry_lookup_result = direct_wrapper.registry_lookup()
                if (registry_lookup_result[0] == 0):
                    logger.warn("No registries found")
                    sys.exit(1)
                registry_retrieve_result = direct_wrapper.registry_retrieve(
                    registry_lookup_result[2][0])
                config["tcf"]["json_rpc_uri"] = registry_retrieve_result[0]

        # Prepare worker
        direct_wrapper.init_worker_registry(config)

        global worker_id
        if not worker_id:
                worker_lookup_json = jrpc_request.WorkerLookupJson(
                    1, worker_type=1)
                worker_lookup_result = direct_wrapper.worker_lookup(
                    worker_lookup_json)
                if "result" in worker_lookup_result and \
                        "ids" in worker_lookup_result["result"].keys():
                        if worker_lookup_result["result"]["totalCount"] != 0:
                            worker_id = \
                                worker_lookup_result["result"]["ids"][0]
                        else:
                            logger.error("ERROR: No workers found")
                            sys.exit(1)
                else:
                        logger.error("ERROR: Failed to lookup worker")
                        sys.exit(1)

        worker_retrieve_json = jrpc_request.WorkerRetrieveJson(2, worker_id)
        worker_obj.load_worker(
            direct_wrapper.worker_retrieve(worker_retrieve_json))

        logger.info("********** Worker details Updated with Worker ID" +
                    "*********\n%s\n", worker_id)

        # Convert workloadId to hex
        workload_id = "echo-result"
        workload_id = workload_id.encode("UTF-8").hex()
        # Create work order
        wo_submit_json = jrpc_request.WorkOrderSubmitJson(
            3, 6000, "pformat",
            worker_id, workload_id, "0x2345",
            worker_encryption_key=base64.b64decode(
                worker_obj.worker_encryption_key).hex(),
            data_encryption_algorithm="AES-GCM-256")
        wo_id = wo_submit_json.get_work_order_id()

        # Sign work order
        private_key = utility.generate_signing_keys()
        session_key = utility.generate_key()
        session_iv = utility.generate_iv()
        encrypted_session_key = utility.generate_encrypted_key(
            session_key, worker_obj.worker_encryption_key)
        # Generate one time key used for encrypting inData
        data_key = utility.generate_key()
        # Initialation vector of size 12 bytes with all zeros.
        data_iv = bytearray(12)

        encrypted_key = utility.generate_encrypted_key(
            data_key, worker_obj.worker_encryption_key)
        encrypted_data_encryption_key = utility.encrypt_data(
            encrypted_key, session_key)
        encrypted_data_encryption_key_str = ''.join(
            format(i, '02x') for i in encrypted_data_encryption_key)
        data_iv_str = ''.join(format(i, '02x') for i in data_iv)
        wo_submit_json.add_in_data(
            message, None, encrypted_data_encryption_key_str, data_iv_str)
        # Submit work order
        direct_wrapper.init_work_order(config)
        direct_wrapper.work_order_submit(
            wo_submit_json, encrypted_session_key, worker_obj, private_key,
            session_key, session_iv, data_key, data_iv)

        # Retrieve result
        wo_get_result_json = jrpc_request.WorkOrderGetResultJson(4, wo_id)
        direct_wrapper.work_order_get_result(
            wo_get_result_json, session_key, session_iv, data_key, data_iv)


# -----------------------------------------------------------------------------
Main()
