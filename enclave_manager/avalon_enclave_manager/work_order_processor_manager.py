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


import zmq
import json
import time
import logging
import utility.jrpc_utility as jrpc_utility

from abc import abstractmethod
from error_code.error_status import WorkOrderStatus
from avalon_enclave_manager.base_enclave_manager import EnclaveManager

logger = logging.getLogger(__name__)


class WOProcessorManager(EnclaveManager):
    """
    Abstract class for enclave managers capable of processing work orders
    """

    def __init__(self, config):
        super().__init__(config)
        self._identity = None

# -------------------------------------------------------------------------

    def _process_work_order_sync(self, process_wo_id):
        """
        Process the work-order of the specified work-order id
        and return the response. Used for synchronous execution.

        Parameters:
            @param process_wo_id - Id of the work-order that is to be processed
        """
        logger.info(
            "About to process work orders found in wo-worker-scheduled table.")

        # csv_match_pop will peek into the deque and pop out the first
        # work-order id if it matches the process_wo_id
        wo_id = self._kv_helper.csv_match_pop(
            "wo-worker-scheduled", self._worker_id, process_wo_id)
        if process_wo_id == wo_id:
            wo_process_result = self._process_work_order_by_id(wo_id)

            # Cleanup wo-worker-processing that hold in-progress work orders
            self._kv_helper.remove("wo-worker-processing", self._identity)

            return wo_process_result
        else:
            return None

        logger.info("No more worker orders in wo-worker-scheduled table.")

# -------------------------------------------------------------------------

    def _process_work_orders(self):
        """
        Executes Run time flow of enclave manager
        """
        logger.info(
            "About to process work orders found in wo-worker-scheduled table.")

        wo_id = self._kv_helper.csv_pop("wo-worker-scheduled", self._worker_id)
        while wo_id is not None:

            self._process_work_order_by_id(wo_id)
            # Cleanup wo-worker-processing that hold in-progress work orders
            self._kv_helper.remove("wo-worker-processing", self._identity)

            wo_id = self._kv_helper.csv_pop("wo-worker-scheduled",
                                            self._worker_id)
        # end of loop
        logger.info("No more worker orders in wo-worker-scheduled table.")

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
            # Get JSON workorder request corresponding to wo_id
            wo_json_req = self._kv_helper.get("wo-requests", wo_id)
            if wo_json_req is None:
                logger.error("Received empty work order corresponding " +
                             "to id %s from wo-requests table", wo_id)
                return None

        except Exception as e:
            logger.error("Problem while reading the work order %s "
                         "from wo-requests table", wo_id)
            return None

        logger.info("Validating JSON workorder request %s", wo_id)
        if not self._validate_request(wo_id, wo_json_req):
            return None

        # wo-worker-processing holds a mapping of worker_identity->wo_id.
        # The identity of a worker is the worker_id in case of Singleton
        # worker and it is the enclave id in case of a worker from a worker
        # pool(WPE).
        self._kv_helper.set("wo-worker-processing", self._identity, wo_id)
        logger.info("Workorder %s picked up for processing by %s",
                    wo_id, self._identity)

        # Execute work order request

        logger.info("Execute workorder with id %s", wo_id)
        wo_json_resp = self._execute_work_order(wo_json_req)
        wo_resp = json.loads(wo_json_resp)

        logger.info("Update workorder receipt for workorder %s", wo_id)
        self._wo_kv_delegate.update_receipt(wo_id, wo_resp)

        if "error" in wo_resp and \
                wo_resp["error"]["code"] == WorkOrderStatus.FAILED:
            self._persist_wo_response_to_db(
                wo_id, WorkOrderStatus.FAILED, wo_json_resp)
            return None

        self._persist_wo_response_to_db(
            wo_id, WorkOrderStatus.SUCCESS, wo_json_resp)

        return wo_resp

    # -------------------------------------------------------------------------

    @abstractmethod
    def _execute_wo_in_trusted_enclave(self, input_json_str):
        """
        Submits workorder request to Worker enclave and retrieves the response

        Parameters :
            input_json_str - A JSON formatted str of the request to execute
        Returns :
            json_response - A JSON formatted str of the response received from
                            the enclave. Errors are also wrapped in a JSON str
                            if exceptions have occurred.
        """
        pass

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
        try:
            wo_response = self._execute_wo_in_trusted_enclave(input_json_str)
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

    def _persist_wo_response_to_db(self, wo_id, status,
                                   wo_response=None, msg=None):
        """
        persist the response of a work order processing into the database
        for success as well as failure. Construct response JSON in case
        one is not passed in. Make use of msg field in json.

        Parameters:
            @param wo_id - Id of the work-order being handled
            @param status - WorkOrderStatus of work order ro be persisted
            @param wo_response - Response JSON to be persisted
            @param msg - Message in response in case wo_response is None
        """
        if wo_response is None:
            # Passing jrpc_id as 0 as this will be overridden anyways
            err_response = jrpc_utility.create_error_response(
                WorkOrderStatus.FAILED, "0", msg)
            wo_response = json.dumps(err_response)

        logger.info("Update response in wo-responses for workorder %s.", wo_id)
        self._kv_helper.set("wo-responses", wo_id, wo_response)

        logger.info(
            "Persist work order id %s in wo-worker-processed map.", wo_id)
        # Append wo_id to the list of work orders processed by this worker
        self._kv_helper.csv_append("wo-worker-processed",
                                   self._worker_id, wo_id)

    # -----------------------------------------------------------------

    def _validate_request(self, wo_id, wo_request):
        """
        Validate workorder request.
        Parameters :
            @param wo_id - Work order id of the request
            @param wo_request - Flattened JSON request
        Returns :
            @returns True - If the input request is validated
                            False, otherwise
        """
        try:
            json_obj = json.loads(wo_request)
        except ValueError as e:
            logger.error("Invalid JSON format found for workorder - %s", e)
            logger.error(
                "JSON validation for Workorder %s failed; " +
                "handling failure scenarios", wo_id)
            self._persist_wo_response_to_db(
                wo_id, WorkOrderStatus.FAILED, None,
                "Workorder JSON request is invalid")
            return False
        return True

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

    # -----------------------------------------------------------------

    def _bind_zmq_socket(self, zmq_port):
        """
        Function to bind to zmq port configured. ZMQ is used for
        synchronous work order processing.

        Returns :
            socket - An instance of a Socket bound to the configured
                     port.
        """
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://0.0.0.0:"+zmq_port)
        return socket

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
            socket = self._bind_zmq_socket(
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
