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

        workloads_str = config.get("WorkerConfig")["workloads"]
        workloads = workloads_str.split(',')
        self._workloads = []
        for workload in workloads:
            self._workloads.append(workload.encode("UTF-8").hex())

# -------------------------------------------------------------------------

    def _process_work_order_sync(self, process_wo_id):
        """
        Process the work-order of the specified work-order id
        and return the response.
        Used for synchronous execution.
        Parameters:
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
                return None

        except Exception as e:
            logger.error("Problem while reading the work order %s"
                         "from wo-requests table", wo_id)
            self._kv_helper.remove("wo-processing", wo_id)
            return None

        logger.info("Create workorder entry %s in wo-processing table",
                    wo_id)
        self._kv_helper.set("wo-processing", wo_id,
                            WorkOrderStatus.PROCESSING.name)

        logger.info("Delete workorder entry %s from wo-scheduled table",
                    wo_id)
        self._kv_helper.remove("wo-scheduled", wo_id)

        logger.info("Validating JSON workorder request %s", wo_id)
        if not self._validate_request(wo_id, wo_json_req):
            return None

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
            return None

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

    def _handle_wo_process_failure(self, msg, wo_id):
        """
        Handle failure of work order by creating proper response JSON
        and updating database appropriately.

        Parameters:
            @param msg - Error message to put into response
            @param wo_id - Id of the work-order being handled
        """
        # Passing jrpc_id as 0 as this will be overridden anyways
        wo_response = jrpc_utility.create_error_response(
            WorkOrderStatus.FAILED, "0", msg)

        self._kv_helper.set("wo-responses", wo_id, json.dumps(wo_response))
        self._kv_helper.set("wo-processed", wo_id,
                            WorkOrderStatus.FAILED.name)
        self._kv_helper.remove("wo-processing", wo_id)

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

            # Check if wo can be processed by this worker
            if "params" in json_obj and "workloadId" in json_obj["params"]:
                workload_id_in_req = json_obj["params"]["workloadId"]
                if workload_id_in_req not in self._workloads:
                    logger.error("Workload cannot be processed by this worker")
                    self._handle_wo_process_failure(
                        "Workload cannot be processed by this worker", wo_id)
                    return False
            else:
                logger.error("Work order request not well-formed")
                self._handle_wo_process_failure(
                    "Workorder request is not well-formed", wo_id)
                return False
        except ValueError as e:
            logger.error("Invalid JSON format found for workorder - %s", e)
            logger.error(
                "JSON validation for Workorder %s failed; " +
                "handling Failure scenarios", wo_id)
            self._handle_wo_process_failure(
                "Workorder JSON request is invalid", wo_id)
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
