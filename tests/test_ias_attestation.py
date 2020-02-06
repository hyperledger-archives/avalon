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
import random
import json
import argparse
import logging
import base64
import secrets

import config.config as pconfig
import utility.logger as plogger
from avalon_sdk.worker.worker_details import WorkerType
import avalon_sdk.worker.worker_details as worker
from avalon_sdk.work_order.work_order_params import WorkOrderParams
from connectors.direct.direct_json_rpc_api_connector \
    import DirectJsonRpcApiConnector
import verify_report.verify_attestation_report as attestation_util
from error_code.error_status import WorkOrderStatus

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
        parser.add_argument(
            "-c", "--config",
            help="the config file containing Ethereum contract information",
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

        options = parser.parse_args(args)

        if options.config:
                conf_files = [options.config]
        else:
                conf_files = [TCFHOME + "/sdk/avalon_sdk/" +
                              "tcf_connector.toml"]
        confpaths = ["."]
        try:
                config = pconfig.parse_configuration_files(conf_files,
                                                           confpaths)
                json.dumps(config)
        except pconfig.ConfigurationException as e:
                logger.error(str(e))
                sys.exit(-1)

        global direct_jrpc
        direct_jrpc = DirectJsonRpcApiConnector(conf_files[0])

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
                registry_list_instance = \
                    direct_jrpc.create_worker_registry_list(config)

                # Lookup returns tuple.
                # The first element is number of registries,
                # the second is element is lookup tag, and
                # the third is list of organization ids.
                registry_count, lookup_tag, registry_list = \
                    registry_list_instance.registry_lookup()
                logger.info(
                    "\n Registry lookup response: registry count: " +
                    "{} lookup tag: {} registry list: {}\n".format(
                        registry_count, lookup_tag, registry_list))
                if (registry_count == 0):
                        logger.warn("No registries found")
                        sys.exit(1)
                # Retrieve the fist registry details.
                registry_retrieve_result = \
                    registry_list_instance.registry_retrieve(registry_list[0])
                logger.info("\n Registry retrieve response: {}\n".format(
                            registry_retrieve_result))
                config["tcf"]["json_rpc_uri"] = registry_retrieve_result[0]

        # Prepare worker
        req_id = 31
        global worker_id
        worker_registry_instance = direct_jrpc.create_worker_registry(config)
        if not worker_id:
                worker_lookup_result = worker_registry_instance.worker_lookup(
                    worker_type=WorkerType.TEE_SGX, id=req_id)
                logger.info("\n Worker lookup response: {}\n".format(
                    json.dumps(worker_lookup_result, indent=4)))
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
        req_id += 1
        worker_retrieve_result = worker_registry_instance.worker_retrieve(
            worker_id, req_id)
        logger.info("\n Worker retrieve response: {}\n".format(
            json.dumps(worker_retrieve_result, indent=4)))
        worker_obj.load_worker(worker_retrieve_result)

        logger.info("**********Worker details Updated with Worker ID" +
                    "*********\n%s\n", worker_id)

        if not worker_obj.proof_data:
            logger.info("Proof data is empty. " +
                        "Skipping verification of attestation report")
            exit(0)

        # Construct enclave signup info json
        enclave_info = {
            'verifying_key': worker_obj.verification_key,
            'encryption_key': worker_obj.encryption_key,
            'proof_data': worker_obj.proof_data,
            'enclave_persistent_id': ''
        }

        logger.info("Perform verification of attestation report")
        verify_report_status = attestation_util.verify_attestation_report(
            enclave_info)
        if verify_report_status is False:
            logger.error("Verification of enclave signup info failed")
        else:
            logger.info("Verification of enclave signup info passed")


# -----------------------------------------------------------------------------
Main()
