#!/usr/bin/env python3

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

import argparse
import json
import logging
import os
import sys
import random

import avalon_enclave_manager.sgx_work_order_request as work_order_request
import avalon_enclave_manager.kme.kme_enclave_info as enclave_info
from avalon_enclave_manager.base_enclave_manager import EnclaveManager
from listener.base_jrpc_listener import parse_bind_url
from avalon_enclave_manager.kme.kme_listener import KMEListener
from error_code.error_status import WorkOrderStatus
from jsonrpc.exceptions import JSONRPCDispatchException
from avalon_enclave_manager.enclave_type import EnclaveType
from utility.jrpc_utility import get_request_json

logger = logging.getLogger(__name__)


class KeyManagementEnclaveManager(EnclaveManager):
    """
    Class to manage key management enclave in a worker pool
    setup for processing work orders
    """

    def __init__(self, config):

        super().__init__(config)
        self.proof_data_type = config.get("WorkerConfig")["ProofDataType"]

# -------------------------------------------------------------------------

    def _create_signup_data(self):
        """
        Create KME signup data.

        Returns :
            signup_data - Relevant signup data to be used for requests to the
                          enclave
        """
        return enclave_info.\
            KeyManagementEnclaveInfo(self._config,
                                     self._worker_id,
                                     EnclaveType.KME)

# -------------------------------------------------------------------------

    def _manager_on_boot(self):
        """
        Executes Boot flow of enclave manager
        """
        logger.info("Executing boot time procedure")

        # Cleanup all stale work orders for this worker which
        # used old worker keys
        self._wo_kv_delegate.cleanup_work_orders()

        # Clear all WPEs mapped to this worker_id (pool). WPEs will have
        # to register afresh to get into the pool now.
        self._worker_kv_delegate.cleanup_pool(self._worker_id)

        # Add a new worker
        worker_info = EnclaveManager.create_json_worker(self, self._config)
        # Hex string read from config which is 64 characters long
        self._worker_kv_delegate.add_new_worker(self._worker_id, worker_info)

# -------------------------------------------------------------------------

    def _execute_work_order(self, input_json_str, ext_data=""):
        """
        Submits request to KME and retrieves the response

        Parameters :
            @param input_json_str - A JSON formatted str of the request
            @param ext_data - Extended data to pass to trusted code
        Returns :
            @returns json_response - A JSON formatted str of the response
                                     received from the enclave
        """
        try:
            logger.info("Request sent to enclave %s", input_json_str)
            wo_request = work_order_request.SgxWorkOrderRequest(
                EnclaveType.KME,
                input_json_str,
                ext_data
            )
            wo_response = wo_request.execute()
            try:
                json_response = json.dumps(wo_response, indent=4)
                logger.info("Response from enclave %s", json_response)
            except Exception as err:
                logger.error("ERROR: Failed to serialize JSON; %s", str(err))

        except Exception as e:
            logger.error("failed to execute work order; %s", str(e))
            wo_response = dict()
            wo_response["error"] = dict()
            wo_response["error"]["code"] = WorkOrderStatus.FAILED
            wo_response["error"]["message"] = str(e)
            json_response = json.dumps(wo_response, indent=4)

        return json_response

# -------------------------------------------------------------------------

    def start_enclave_manager(self):
        """
        Execute boot flow and run time flow
        """
        try:
            logger.info(
                "--------------- Starting Boot time flow ----------------")
            self._manager_on_boot()
            logger.info(
                "--------------- Boot time flow Complete ----------------")
        except Exception as err:
            logger.error("Failed to execute boot time flow; " +
                         "exiting Intel SGX Enclave manager: {}".format(err))
            exit(1)

        self._start_kme_listener()


# -------------------------------------------------------------------------

    def _start_kme_listener(self):
        """
        This function reads the host_name and port for the listener to
        bind. It instantiates the KMEListener and starts it. This
        listener runs indefinitely processing requests received from
        WPEs. It terminates only when an exception occurs within start
        method os the listener instance.
        """
        host_name, port = parse_bind_url(
            self._config["KMEListener"].get("bind"))

        rpc_methods = [
            self.GetUniqueVerificationKey,
            self.RegisterWorkOrderProcessor,
            self.PreProcessWorkOrder
        ]
        self._kme_listener = KMEListener(rpc_methods)
        self._kme_listener.start(host_name, port)


# -----------------------------------------------------------------

    def GetUniqueVerificationKey(self, **params):
        """
        RPC method registered with the KME listener to generate an
        unique verification key before a WPE registration.

        Parameters :
            @param params - variable-length argument list
        Returns :
            @returns response - A jrpc response
        """
        try:
            wo_request = get_request_json("GetUniqueVerificationKey",
                                          random.randint(0, 100000))
            wo_request["params"] = params
            wo_response = self._execute_work_order(json.dumps(wo_request), "")
            wo_response_json = json.loads(wo_response)

            data = {
                "workOrderId": wo_request["params"]["workOrderId"]
            }

            if "result" in wo_response_json:
                return wo_response_json["result"]
            else:
                logger.error("Could not get UniqueVerificationKey - %s",
                             wo_response_json)
                # For all negative cases, response should have an error field.
                # Hence constructing JSONRPC error response with
                # error code and message mapped to KME enclave response
                err_code = wo_response_json["error"]["code"]
                err_msg = wo_response_json["error"]["message"]
                raise JSONRPCDispatchException(err_code, err_msg, data)
        except Exception as e:
            raise JSONRPCDispatchException(
                WorkOrderStatus.FAILED, str(e), data)

# -----------------------------------------------------------------

    def RegisterWorkOrderProcessor(self, **params):
        """
        RPC method registered with the KME listener to register a WPE
        with a KME.

        Parameters :
            @param params - variable-length argument list
        Returns :
            @returns response - A jrpc response
        """
        wo_request = get_request_json("RegisterWorkOrderProcessor",
                                      random.randint(0, 100000))
        wo_request["params"] = params
        wo_response = self._execute_work_order(json.dumps(wo_request), "")
        wo_response_json = json.loads(wo_response)

        if "result" in wo_response_json:
            return wo_response_json["result"]
        else:
            logger.error("Could not register WPE")
            return wo_response_json

# -----------------------------------------------------------------

    def PreProcessWorkOrder(self, **params):
        """
        RPC method registered with the KME listener to pre-process a
        work order request.

        Parameters :
            @param params - variable-length argument list
        Returns :
            @returns response - A jrpc response
        """
        wo_request = get_request_json("PreProcessWorkOrder",
                                      random.randint(0, 100000))
        wo_request["params"] = params
        wo_response = self._execute_work_order(json.dumps(wo_request), "")
        wo_response_json = json.loads(wo_response)

        if "result" in wo_response_json:
            return wo_response_json["result"]
        else:
            logger.error("Could not preprocess work order at KME")
            # For all negative cases, response should have an error field.
            # Hence constructing JSONRPC error response with
            # error code and message mapped to KME enclave response
            err_code = wo_response_json["error"]["code"]
            err_msg = wo_response_json["error"]["message"]
            data = {
                "workOrderId": wo_response_json["error"]["data"]["workOrderId"]
            }
            raise JSONRPCDispatchException(err_code, err_msg, data)

# -----------------------------------------------------------------


def main(args=None):
    import config.config as pconfig
    import utility.logger as plogger

    # parse out the configuration file first
    tcf_home = os.environ.get("TCF_HOME", "../../../../")

    conf_files = ["kme_config.toml"]
    conf_paths = [".", tcf_home + "/"+"config"]

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="configuration file", nargs="+")
    parser.add_argument("--config-dir", help="configuration folder", nargs="+")
    parser.add_argument("--bind", help="KME listener url for requests to KME",
                        type=str)
    parser.add_argument("--worker_id",
                        help="Id of worker in plain text", type=str)
    parser.add_argument(
        "--wpe-mrenclave",
        help="MRENCLAVE of WPE that can register with this KME",
        type=str)

    (options, remainder) = parser.parse_known_args(args)

    if options.config:
        conf_files = options.config

    if options.config_dir:
        conf_paths = options.config_dir

    try:
        config = pconfig.parse_configuration_files(conf_files, conf_paths)
        json.dumps(config, indent=4)
    except pconfig.ConfigurationException as e:
        logger.error(str(e))
        sys.exit(-1)

    if options.bind:
        config["KMEListener"]["bind"] = options.bind
    if options.worker_id:
        config["WorkerConfig"]["worker_id"] = options.worker_id
    if options.wpe_mrenclave:
        config["EnclaveModule"]["wpe_mrenclave"] = options.wpe_mrenclave

    plogger.setup_loggers(config.get("Logging", {}))
    sys.stdout = plogger.stream_to_logger(
        logging.getLogger("STDOUT"), logging.DEBUG)
    sys.stderr = plogger.stream_to_logger(
        logging.getLogger("STDERR"), logging.WARN)

    EnclaveManager.parse_command_line(config, remainder)
    logger.info("Initialize KeyManagement enclave_manager")
    enclave_manager = KeyManagementEnclaveManager(config)
    logger.info("About to start KeyManagement Enclave manager")
    enclave_manager.start_enclave_manager()


main()
