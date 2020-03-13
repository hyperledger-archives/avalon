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

import time
import json
import logging
from error_code.error_status import WorkOrderStatus
from error_code.enclave_error import EnclaveError

from jsonrpc.exceptions import JSONRPCDispatchException

logger = logging.getLogger(__name__)


class WorkOrderLmdbHelper:
    """
    WorkOrderDBHelper helps listener or other client facing modules
    to interact with the kv storage for queries related to work
    order processing.
    """
# ------------------------------------------------------------------------------------------------

    def __init__(self, kv_helper):
        """
        Function to perform init activity
        Parameters:
            - kv_helper is a object of shared kv database
        """

        self.kv_helper = kv_helper

# ---------------------------------------------------------------------------------------------
    def get_wo_result(self, wo_id):
        """
        Function to get work-order result from shared kv database
        Parameters:
            - wo_id is the id of the work-order for which result is
            requested.
        Returns jrpc response as defined in EEA spec 6.1.2
        """

        # Work order is processed if it is in wo-response table
        value = self.kv_helper.get("wo-responses", wo_id)
        if value:
            response = json.loads(value)
            if 'result' in response:
                return response['result']

            # response without a result should have an error
            err_code = response["error"]["code"]
            err_msg = response["error"]["message"]
            if err_code == EnclaveError.ENCLAVE_ERR_VALUE:
                err_code = WorkOrderStatus.INVALID_PARAMETER_FORMAT_OR_VALUE
            elif err_code == EnclaveError.ENCLAVE_ERR_UNKNOWN:
                err_code = WorkOrderStatus.UNKNOWN_ERROR
            else:
                err_code = WorkOrderStatus.FAILED
            raise JSONRPCDispatchException(err_code, err_msg)

        if(self.kv_helper.get("wo-timestamps", wo_id) is not None):
            # work order is yet to be processed
            raise JSONRPCDispatchException(
                WorkOrderStatus.PENDING,
                "Work order result is yet to be updated")

        # work order not in 'wo-timestamps' table
        raise JSONRPCDispatchException(
            WorkOrderStatus.INVALID_PARAMETER_FORMAT_OR_VALUE,
            "Work order Id not found in the database. Hence invalid parameter")

# ---------------------------------------------------------------------------------------------
    def submit_wo(self, wo_id, input_json_str):
        """
        Function to submit and store a new work-order
        Parameters:
            - wo_id: id of work-order being submitted
            - input_json_str: The actual work-order as received
            from the requester
        """

        if(self.kv_helper.get("wo-timestamps", wo_id) is None):

            # Create a new work order entry.
            # Don't change the order of table updation.
            # The order is important for clean up if the TCS is restarted in
            # the middle.
            epoch_time = str(time.time())

            # Update the tables
            self.kv_helper.set("wo-timestamps", wo_id, epoch_time)
            self.kv_helper.set("wo-requests", wo_id, input_json_str)
            self.kv_helper.set("wo-scheduled", wo_id, input_json_str)

            raise JSONRPCDispatchException(
                WorkOrderStatus.PENDING,
                "Work order is computing. Please query for WorkOrderGetResult \
                 to view the result")

        # Workorder id already exists
        raise JSONRPCDispatchException(
            WorkOrderStatus.INVALID_PARAMETER_FORMAT_OR_VALUE,
            "Work order id already exists in the database. \
                Hence invalid parameter")

    def clear_a_processed_wo(self):
        """
        Function to clears one(least recently added) processed
        work-order from wo-processed table
        """
        work_orders = self.kv_helper.lookup("wo-timestamps")
        for id in work_orders:

            # If work order is processed then remove from table
            if (self.kv_helper.get("wo-processed", id) is not None):
                self.kv_helper.remove("wo-processed", id)
                self.kv_helper.remove("wo-requests", id)
                self.kv_helper.remove("wo-responses", id)
                self.kv_helper.remove("wo-receipts", id)
                self.kv_helper.remove("wo-timestamps", id)
                return id

    def cleanup_hindered_wo(self):
        """
        This function is meant to do a boot time cleanup
        Returns the list of work-order to be processed and the count
        """
        workorder_count = 0
        workorder_list = []
        work_orders = self.kv_helper.lookup("wo-timestamps")
        for wo_id in work_orders:

            if (self.kv_helper.get("wo-scheduled", wo_id) is None and
                    self.kv_helper.get("wo-processing", wo_id) is None and
                    self.kv_helper.get("wo-processed", wo_id) is None):

                if (self.kv_helper.get("wo-requests", wo_id) is not None):
                    self.kv_helper.remove("wo-requests", wo_id)

                if (self.kv_helper.get("wo-responses", wo_id) is not None):
                    self.kv_helper.remove("wo-responses", wo_id)

                if (self.kv_helper.get("wo-receipts", wo_id) is not None):
                    self.kv_helper.remove("wo-receipts", wo_id)

                self.kv_helper.remove("wo-timestamps", wo_id)

            else:
                # Add to the internal FIFO
                workorder_list.append(wo_id)
                workorder_count += 1

        return workorder_list, workorder_count
# ---------------------------------------------------------------------------------------------
