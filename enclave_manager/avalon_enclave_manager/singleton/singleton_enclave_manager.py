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
import time
import random
import zmq

import avalon_enclave_manager.sgx_work_order_request as work_order_request
import avalon_enclave_manager.singleton.singleton_enclave_info as enclave_info
import avalon_crypto_utils.crypto_utility as crypto_utils
from avalon_enclave_manager.base_enclave_manager import EnclaveManager
from avalon_enclave_manager.worker_kv_delegate import WorkerKVDelegate
from avalon_enclave_manager.work_order_kv_delegate import WorkOrderKVDelegate
from error_code.error_status import ReceiptCreateStatus, WorkOrderStatus

logger = logging.getLogger(__name__)


class SingletonEnclaveManager(EnclaveManager):
    """
    Manager class to handle single enclave based work order processing
    """

    def __init__(self, config):

        super().__init__(config)
        self.proof_data_type = config.get("WorkerConfig")["ProofDataType"]

# -------------------------------------------------------------------------

    def _manager_on_boot(self):
        """
        Executes Boot flow of enclave manager
        """
        logger.info("Executing boot time procedure")

        # Cleanup "workers" table
        self._worker_kv_delegate.cleanup_worker()

        # Add a new worker
        worker_info = EnclaveManager.create_json_worker(self, self._config)
        # Hex string read from config which is 64 characters long
        worker_id = self._worker_id
        self._worker_kv_delegate.add_new_worker(worker_id, worker_info)

        # Cleanup wo-processing" table
        self._wo_kv_delegate.cleanup_work_orders()

# -------------------------------------------------------------------------

    def _create_signup_data(self):
        """
        Create Singleton enclave signup data.

        Returns :
            signup_data - Relevant signup data to be used for requests to the
                          enclave
        """
        return enclave_info.\
            SingletonEnclaveInfo(self._config.get("EnclaveModule"))

# -------------------------------------------------------------------------

    def _process_work_order_sync(self, process_wo_id):
        """
        Process the work-order of the specified work-order id
        and return the response.
        Used for synchronous execution.
        Parameters:
        - kv_helper is lmdb instance to access database
        - process_wo_id is id of the work-order that is to be processed
        """
        logger.info("Processing work order")
        try:
            # Get all workorders requests from KV storage lookup and process
            list_of_workorders = self._kv_helper.lookup("wo-scheduled")
            if not list_of_workorders:
                logger.info("Received empty list of work orders from " +
                            "wo-scheduled table")
                return
        except Exception as e:
            logger.error("Problem while getting ids from wo-scheduled table")
            return

        for wo_id in list_of_workorders:
            if wo_id == process_wo_id:
                resp = self._process_work_order_by_id(wo_id)
                return resp
            else:
                return None
        # end of for loop

# -------------------------------------------------------------------------

    def _process_work_orders(self):
        """
        Executes Run time flow of enclave manager
        """
        logger.info("Processing work orders")
        try:
            # Get all workorders requests from KV storage lookup and process
            list_of_workorders = self._kv_helper.lookup("wo-scheduled")
            if not list_of_workorders:
                logger.info("Received empty list of work orders from " +
                            "wo-scheduled table")
                return
        except Exception as e:
            logger.error("Problem while getting keys from wo-scheduled table")
            return

        for wo_id in list_of_workorders:
            self._process_work_order_by_id(wo_id)
        # end of for loop

# -------------------------------------------------------------------------

    def _process_work_order_by_id(self, wo_id):
        """
        Process the work-order of the specified work-order id. Execute the
        work-order and update the tables accordingly.
        Parameters :
            wo_id - It is the work-order id of the work-order that is to be
                    processed
        Returns :
            wo_resp - A JSON response of the executed work order
        """
        try:
            self._kv_helper.set("wo-processing", wo_id,
                                WorkOrderStatus.PROCESSING.name)

            # Get JSON workorder request corresponding to wo_id
            wo_json_req = self._kv_helper.get("wo-requests", wo_id)
            if wo_json_req is None:
                logger.error("Received empty work order corresponding " +
                             "to id %s from wo-requests table", wo_id)
                self._kv_helper.remove("wo-processing", wo_id)
                return

        except Exception as e:
            logger.error("Problem while reading the work order %s"
                         "from wo-requests table", wo_id)
            self._kv_helper.remove("wo-processing", wo_id)
            return

        logger.info("Create workorder entry %s in wo-processing table",
                    wo_id)
        self._kv_helper.set("wo-processing", wo_id,
                            WorkOrderStatus.PROCESSING.name)

        logger.info("Delete workorder entry %s from wo-scheduled table",
                    wo_id)
        self._kv_helper.remove("wo-scheduled", wo_id)

        logger.info("Validating JSON workorder request %s", wo_id)
        validation_status = EnclaveManager.validate_request(wo_json_req)

        if not validation_status:
            logger.error(
                "JSON validation for Workorder %s failed; " +
                "handling Failure scenarios", wo_id)
            wo_response = dict()
            wo_response["Response"] = dict()
            wo_response["Response"]["Status"] = WorkOrderStatus.FAILED
            wo_response["Response"]["Message"] = \
                "Workorder JSON request is invalid"
            self._kv_helper.set("wo-responses", wo_id, json.dumps(wo_response))
            self._kv_helper.set("wo-processed", wo_id,
                                WorkOrderStatus.FAILED.name)
            self._kv_helper.remove("wo-processing", wo_id)
            return

        # Execute work order request

        logger.info("Execute workorder with id %s", wo_id)
        wo_json_resp = self._execute_work_order(wo_json_req)
        wo_resp = json.loads(wo_json_resp)

        logger.info("Update workorder receipt for workorder %s", wo_id)
        self._wo_kv_delegate.update_receipt(wo_id, wo_resp)

        if "Response" in wo_resp and \
                wo_resp["Response"]["Status"] == WorkOrderStatus.FAILED:
            logger.error("error in Response")
            self._kv_helper.set("wo-processed", wo_id,
                                WorkOrderStatus.FAILED.name)
            self._kv_helper.set("wo-responses", wo_id, wo_json_resp)
            self._kv_helper.remove("wo-processing", wo_id)
            return

        logger.info("Mark workorder status for workorder id %s " +
                    "as Completed in wo-processed", wo_id)
        self._kv_helper.set("wo-processed", wo_id,
                            WorkOrderStatus.SUCCESS.name)

        logger.info("Create entry in wo-responses table for workorder %s",
                    wo_id)
        self._kv_helper.set("wo-responses", wo_id, wo_json_resp)

        logger.info("Delete workorder entry %s from wo-processing table",
                    wo_id)
        self._kv_helper.remove("wo-processing", wo_id)
        return wo_resp

# -------------------------------------------------------------------------

    def _execute_work_order(self, input_json_str):
        """
        Submits workorder request to Worker enclave and retrieves the response

        Parameters :
            input_json_str - A JSON formatted str of the request to execute
        Returns :
            json_response - A JSON formatted str of the response received from
                            the enclave. Errors are also wrapped in a JSON str
                            if exceptions have occurred.
        """
        wo_response = dict()
        try:
            wo_request = work_order_request.SgxWorkOrderRequest(
                self._config,
                input_json_str)
            wo_response = wo_request.execute()

            try:
                json_response = json.dumps(wo_response, indent=4)
            except Exception as err:
                wo_response["Response"] = dict()
                logger.error("ERROR: Failed to serialize JSON; %s", str(err))
                wo_response["Response"]["Status"] = WorkOrderStatus.FAILED
                wo_response["Response"]["Message"] = "Failed to serialize JSON"
                json_response = json.dumps(wo_response)

        except Exception as e:
            wo_response["Response"] = dict()
            logger.error("failed to execute work order; %s", str(e))
            wo_response["Response"]["Status"] = WorkOrderStatus.FAILED
            wo_response["Response"]["Message"] = str(e)
            json_response = json.dumps(wo_response)

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

        sync_workload_exec = int(
            self._config["WorkloadExecution"]["sync_workload_execution"])

        if sync_workload_exec == 1:
            self._start_zmq_listener()
        else:
            self._start_polling_kvstore()

# -------------------------------------------------------------------------

    def _start_polling_kvstore(self):
        """
        This function is runs indefinitely polling the KV Storage
        for new work-order request and processing them. The poll
        is interleaved with sleeps hence avoiding busy waits. It
        terminates only when an exception occurs.
        """
        try:
            sleep_interval = \
                int(self._config["EnclaveManager"]["sleep_interval"])
        except Exception as err:
            logger.error("Failed to get sleep interval from config file. " +
                         "Setting sleep interval to 10 seconds: %s", str(err))
            sleep_interval = 10

        try:
            while True:
                # Poll KV storage for new work-order requests and process
                self._process_work_orders()
                logger.info("Enclave manager sleeping for %d secs",
                            sleep_interval)
                time.sleep(sleep_interval)
        except Exception as inst:
            logger.error("Error while processing work-order; " +
                         "shutting down enclave manager")
            logger.error("Exception: {} args {} details {}"
                         .format(type(inst), inst.args, inst))
            exit(1)

# -------------------------------------------------------------------------

    def _start_zmq_listener(self):
        """
        This function binds to the port configured for zmq and
        then indefinitely processes work order requests received
        over the zmq connection. It terminates only when an
        exception occurs.
        """
        # Binding with ZMQ Port
        try:
            socket = EnclaveManager.bind_zmq_socket(
                self._config.get("EnclaveManager")["zmq_port"])
            logger.info("ZMQ Port hosted by Enclave")
        except Exception as ex:
            logger.exception("Failed to bind socket" +
                             "shutting down enclave manager")
            logger.error("Exception: {} args{} details{}".format(type(ex),
                                                                 ex.args, ex))
            exit(1)
        try:
            while True:
                # Wait for the next request
                logger.info("Enclave Manager waiting for next request")
                wo_id = socket.recv()
                wo_id = wo_id.decode()
                logger.info("Received request at enclave manager: %s" % wo_id)
                result = self._process_work_order_sync(wo_id)
                if result is None:
                    socket.send_string("Error while processing work order: " +
                                       str(wo_id))
                else:
                    socket.send_string("Work order processed: " + str(wo_id))
        except Exception as inst:
            logger.error("Error while processing work-order; " +
                         "shutting down enclave manager")
            logger.error("Exception: {} args {} details {}"
                         .format(type(inst), inst.args, inst))
            exit(1)

# -----------------------------------------------------------------


def main(args=None):
    import config.config as pconfig
    import utility.logger as plogger

    # parse out the configuration file first
    tcf_home = os.environ.get("TCF_HOME", "../../../../")

    conf_files = ["singleton_enclave_config.toml"]
    conf_paths = [".", tcf_home + "/"+"config"]

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="configuration file", nargs="+")
    parser.add_argument("--config-dir", help="configuration folder", nargs="+")
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

    plogger.setup_loggers(config.get("Logging", {}))
    sys.stdout = plogger.stream_to_logger(
        logging.getLogger("STDOUT"), logging.DEBUG)
    sys.stderr = plogger.stream_to_logger(
        logging.getLogger("STDERR"), logging.WARN)

    EnclaveManager.parse_command_line(config, remainder)
    logger.info("Initialize singleton enclave_manager")
    enclave_manager = SingletonEnclaveManager(config)
    logger.info("About to start Singleton Enclave manager")
    enclave_manager.start_enclave_manager()


main()
