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

import time
import json
import logging
import crypto.crypto as crypto
from error_code.error_status import WorkorderError
from shared_kv.shared_kv_interface import KvStorage
import utils.utility as utility

logger = logging.getLogger(__name__)

## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
class TCSWorkOrderHandler:
    """
    TCSWorkOrderHandler processes Worker Order Direct API requests. It puts a new work order requests into the KV storage or it reads appropriate work order information from the KV storage when processing “getter” and enumeration requests. Actual work order processing is done by the SGX Enclave Manager within the enclaves its manages.
    """
# ------------------------------------------------------------------------------------------------
    def __init__(self,kv_helper, max_wo_count):
        """
        Function to perform init activity
        Parameters:
            - kv_helper is a object of lmdb database
        """

        self.kv_helper = kv_helper
        self.workorder_count = 0
        self.max_workorder_count = max_wo_count
        self.workorder_list = []

        self.__work_order_handler_on_boot()

#---------------------------------------------------------------------------------------------
    def __work_order_handler_on_boot(self):
        """
        Function to perform on-boot process of work order handler
        """

        work_orders = self.kv_helper.lookup("wo-timestamps")
        for wo_id in work_orders:

            if(self.kv_helper.get("wo-scheduled", wo_id) is None and
                    self.kv_helper.get("wo-processing", wo_id) is None and
                    self.kv_helper.get("wo-processed", wo_id) is None):

                if(self.kv_helper.get("wo-requests", wo_id) is not None):
                    self.kv_helper.remove("wo-requests", wo_id)

                if(self.kv_helper.get("wo-responses", wo_id) is not None):
                    self.kv_helper.remove("wo-responses", wo_id)

                if(self.kv_helper.get("wo-receipts", wo_id) is not None):
                    self.kv_helper.remove("wo-receipts", wo_id)

                #TODO: uncomment after fixing lmbd error
                self.kv_helper.remove("wo-timestamps", wo_id)

            else:
                #Add to the internal FIFO
                self.workorder_list.append(wo_id)
                self.workorder_count += 1

#---------------------------------------------------------------------------------------------
    def process_work_order(self, input_json_str):
        """
        Function to process work order request
        Parameters:
            - input_json_str is a work order request json as per TCF API 6.1 Work Order Direct Mode Invocation
        """

        input_json = json.loads(input_json_str)
        logger.info("Received Work Order request : %s",input_json['method'])

        response = {}
        response['jsonrpc'] = '2.0'
        response['id'] = input_json['id']
        wo_id = str(input_json['params']['workOrderId'])

        if(input_json['method'] == "WorkOrderSubmit"):
            return self.__process_work_order_submission(wo_id, input_json_str, response)
        elif(input_json['method'] == "WorkOrderGetResult"):
            return self.__process_work_order_get_result(wo_id,
                                                        input_json['id'],
                                                        response)

#---------------------------------------------------------------------------------------------
    def __process_work_order_get_result(self, wo_id, jrpc_id, response):
        """
        Function to process work order get result
        This API corresponds to TCF API 6.1.4 Work Order Pull Request Payload
        Parameters:
            - wo_id is work order id
            - jrpc_id is JRPC id of response
            - response is the response object to be returned
        """

        # Work order is processed if it is in wo-response table
        value = self.kv_helper.get("wo-responses", wo_id)
        if value:
            input_value = json.loads(value)
            if 'result' in value :
                response['result'] = input_value['result']
            else:
                response['result'] = input_value['error']
        else:
            if(self.kv_helper.get("wo-timestamps", wo_id) is not None):
                # work order is yet to be processed
                response = utility.create_error_response(
                        WorkorderError.PENDING, jrpc_id,
                        "Work order result is yet to be updated")
            else :
                # work order not in 'wo-timestamps' table
                response = utility.create_error_response(
                    WorkorderError.INVALID_PARAMETER_FORMAT_OR_VALUE,
                    jrpc_id,
                    "Work order Id not found in the database. \
                     Hence invalid parameter")

        return response

#---------------------------------------------------------------------------------------------
    def __process_work_order_submission(self, wo_id, input_json_str, response):
        """
        Function to process work order request
        Parameters:
            - wo_id is work order id
            - input_json_str is a work order request json as per TCF API 6.1.1 Work Order Request Payload
            - response is the response object to be returned to client
        """

        input_value_json = json.loads(input_json_str)
        jrpc_id = input_value_json["id"]

        if((self.workorder_count + 1) > self.max_workorder_count):

            #if max count reached clear a processed entry
            work_orders = self.kv_helper.lookup("wo-timestamps")
            for id in work_orders:

                # If work order is processed then remove from table
                if(self.kv_helper.get("wo-processed", id) is not None):
                    self.kv_helper.remove("wo-processed", id)
                    self.kv_helper.remove("wo-requests", id)
                    self.kv_helper.remove("wo-responses", id)
                    self.kv_helper.remove("wo-receipts", id)
                    self.kv_helper.remove("wo-timestamps", id)

                    self.workorder_list.remove(id)
                    self.workorder_count -= 1
                    break

            # If no work order is processed then return busy
            if((self.workorder_count + 1) > self.max_workorder_count):
                response = utility.create_error_response(
                    WorkorderError.BUSY,
                    jrpc_id,
                    "Work order handler is busy updating the result")
                return response

        if(self.kv_helper.get("wo-timestamps",wo_id) is None):

            # Create a new work order entry. Dont change the order of table updation.
            # The order is important for clean up if the TCS is restarted in middle
            epoch_time = str(time.time())

            # Update the tables
            self.kv_helper.set("wo-timestamps", wo_id, epoch_time)
            self.kv_helper.set("wo-requests", wo_id, input_json_str)
            self.kv_helper.set("wo-scheduled", wo_id, input_json_str)
            #Add to the internal FIFO
            self.workorder_list.append(wo_id)
            self.workorder_count += 1

            response = utility.create_error_response(
                WorkorderError.PENDING,
                jrpc_id,
                "Work order is computing. Please query for WorkOrderGetResult \
                 to view the result")

        else:
            # Workorder id already exists
            response = utility.create_error_response(
                WorkorderError.INVALID_PARAMETER_FORMAT_OR_VALUE,
                jrpc_id,
                "Work order id already exists in the database. \
                 Hence invalid parameter")

        return response
#---------------------------------------------------------------------------------------------
