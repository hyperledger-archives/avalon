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

import json
import logging
from error_code.error_status import ReceiptCreateStatus
from error_code.error_status import WorkorderError
import utils.utility as utility
from itertools import cycle
from shared_kv.shared_kv_interface import KvStorage

logger = logging.getLogger(__name__)

class TCSWorkOrderReceiptHandler:
    """
    TCSWorkOrderReceiptHandler processes Work Order Receipt Direct API requests. It reads appropriate work order information from the KV storage to create the response. Work order receipts are created and placed in the KV storage by the SGX Enclave Manager after the work order (successfully) completed.
    """
# ------------------------------------------------------------------------------------------------
    def __init__(self,kv_helper):
        """
        Function to perform init activity
        Parameters:
            - kv_helper is a object of lmdb database
        """

        self.kv_helper = kv_helper
        self.receipt_pool = []
        self.__workorder_receipt_on_boot()
# ------------------------------------------------------------------------------------------------

    def __workorder_receipt_on_boot(self):
        """
        Function to perform on-boot process of work order handler
        """

        self.receipt_pool = self.kv_helper.lookup("wo-receipts")
# ------------------------------------------------------------------------------------------------

    def __process_store_workorder_receipt(self, wo_id, input_json_str, response):
        """
        Function to process work order request
        Parameters:
            - wo_id is work order id
            - input_json_str is create work order receipt json
              as per TCF API 7.2.2 Receipt Create Request Payload
            - response is the response object to be returned to client
        """

        input_value_json = json.loads(input_json_str)
        jrpc_id = input_value_json["id"]
        input_value = {}
        input_value['result'] =  input_value_json['params']
        input_value['result']['receiptCurrentStatus'] = ReceiptCreateStatus.PENDING
        #Updater is introduced to maintain multiple update details on a receipt
        input_value['result']['updater'] = {}
        input_json_str = json.dumps(input_value)

        if(self.kv_helper.get("wo-receipts",wo_id) is None):
            value = self.kv_helper.get("wo-requests", wo_id)
            if value:
                self.kv_helper.set("wo-receipts",wo_id,input_json_str)
                response = utility.create_error_response(
                        WorkorderError.SUCCESS, jrpc_id,
                        "Receipt created successfully")
            else:
                response = utility.create_error_response(
                        WorkorderError.INVALID_PARAMETER_FORMAT_OR_VALUE, jrpc_id,
                        "Work order does not exists. Hence invalid parameter")
        else:
            response = utility.create_error_response(
                    WorkorderError.INVALID_PARAMETER_FORMAT_OR_VALUE, jrpc_id,
                    "Work order receipt already exist in the database. Hence invalid parameter")

        return response
# ------------------------------------------------------------------------------------------------

    def __process_workorder_receipt_update(self, wo_id, input_json_str, response):
        """
        Function to process update work order request
        Parameters:
            - wo_id is work order id
            - input_json_str is work order receipt update json as per
              TCF API 7.2.6 Receipt Update Retrieve Request Payload
            - response is the response object to be returned to client
        """

        input_value = json.loads(input_json_str)
        jrpc_id = input_value["id"]

        # value retrieved is 'result' field as per Spec 7.2.5 Receipt Retrieve Response Payload
        value = self.kv_helper.get("wo-receipts", wo_id)
        response['error'] = {}

        if value :
            updater_value = input_value['params']
            # WorkorderId already a part of receipt. And will be not change for a given receipt. Hence it's not stored in updater param.
            del updater_value['workOrderId']

            json_dict = json.loads(value)
            updater_objects = json_dict['result']['updater']

            if len(updater_objects)>0 :
                # Updater Object is sorted based on index and then last index is chosen
                index = int(sorted(updater_objects.keys())[-1]) + 1
            else :
                index = 0

            updater_objects[index] = updater_value
            json_dict['result']['receiptCurrentStatus'] = updater_value['updateType']
            json_dict['result']['updater'] = updater_objects

            value = json.dumps(json_dict)
            self.kv_helper.set("wo-receipts", wo_id, value)
            response = utility.create_error_response(
                    WorkorderError.SUCCESS, jrpc_id,
                    "Receipt Successfully Updated")
        else:
            response = utility.create_error_response(
                WorkorderError.INVALID_PARAMETER_FORMAT_OR_VALUE,
                jrpc_id,
                "Work order id not found in the database. \
                 Hence invalid parameter")
        return response
# ------------------------------------------------------------------------------------------------

    def __lookup_basics(self, lookup_bool, input_json_str, response):
        work_orders = []
        work_orders = self.kv_helper.lookup("wo-receipts")
        alter_items = []

        alter_items = utility.list_difference(self.receipt_pool, work_orders)
        for item in alter_items:
            self.receipt_pool.remove(item)

        alter_items = utility.list_difference(work_orders, self.receipt_pool)
        for item in alter_items:
            self.receipt_pool.append(item)

        input_value = json.loads(input_json_str)
        total_count = 0
        ids = []
        lookupTag = ""

        for wo_id in self.receipt_pool:

            if lookup_bool:

                if (wo_id == input_value["params"]["lastLookUpTag"]):
                    lookup_bool = False
                    continue
                else:
                    continue

            value = self.kv_helper.get("wo-receipts",wo_id)
            json_dict = json.loads(value)
            checkcount = 0
            actualcount = 0
            if value :
                if 'workerServiceId' in input_json_str:
                    checkcount = checkcount+1
                    if json_dict["result"]["workerServiceId"] == input_value["params"]["workerServiceId"]:
                       actualcount = actualcount+1

                if 'workerId' in input_json_str:
                    checkcount = checkcount+1
                    if json_dict["result"]["workerId"] == input_value["params"]["workerId"]:
                       actualcount = actualcount+1

                if 'requesterId' in input_json_str:
                    checkcount = checkcount+1
                    if json_dict["result"]["requesterId"] == input_value["params"]["requesterId"]:
                       actualcount = actualcount+1

                if 'status' in input_json_str:
                    checkcount = checkcount+1
                    if json_dict["result"]["receiptStatus"] == input_value["params"]["receiptStatus"]:
                       actualcount = actualcount+1

            if(checkcount == actualcount):
                total_count = total_count+1
                ids.append(wo_id)
                lookupTag = wo_id

        response["result"] = {}
        response["result"]["totalCount"] = total_count
        response["result"]["lookupTag"] = lookupTag
        response["result"]["ids"] = ids
        return response
# ------------------------------------------------------------------------------------------------

    def __process_workorder_receipt_lookup(self,input_json_str, response):
        """
        Function to look the set of work order receipts available
        Parameters:
            - input_json_str is a work order receipt lookup request json
              as per TCF API 7.2.8 Receipt Lookup Request Payload
            - response is the response object to be returned to client.
        """

        self.__lookup_basics(False, input_json_str, response)
        return response
# ------------------------------------------------------------------------------------------------

    def __process_workorder_receipt_lookup_next(self, input_json_str, response):
        """
        Function to look the set of work order receipt newly added
        Parameters:
            - input_json_str is the work order receipt lookup next json
              as per TCF API 7.2.10 Receipt Lookup Next Request Payload
            - response is the response object to be returned to client.
        """

        self.__lookup_basics(True, input_json_str, response)
        return response
# ------------------------------------------------------------------------------------------------

    def __process_workorder_receipt_retrieve(self,wo_id, jrpc_id, response):
        """
        Function to retrieve the details of worker
        Parameters:
            - worker_id is the worker id specified in worker request json
              as per TCF API 7.2.4 Receipt Retrieve Request Payload
            - response is the response object to be returned to client
            - jrpc_id is the jrpc id of response object to be returned to client
        """

        # value retrieved is 'result' field as per Spec 7.2.5 Receipt Retrieve Response Payload
        value = self.kv_helper.get("wo-receipts", wo_id)
        
        if value:
            input_value = json.loads(value)
            response['result'] = {}
            if 'result' in value :
                response['result'] = input_value['result']
            else:
                #Need to revisit code when actual receipts are created
                response['result'] = input_value['error']
        else :
           response = utility.create_error_response(
                WorkorderError.INVALID_PARAMETER_FORMAT_OR_VALUE,
                jrpc_id,
                "Work order id not found in the database. \
                 Hence invalid parameter")
           return response

        return response
# ------------------------------------------------------------------------------------------------

    def __process_workorder_receipt_update_retrieve(self,wo_id, input_json_str, response):
        """
        Function to process work order receipt update retrieve
        Parameters:
            - wo_id is work order id
            - input_json_str is work order receipt update json
              as per TCF API 7.2.6 Receipt Update Retrieve Request Payload
            - response is the response object to be returned to client
        """

        input_value = json.loads(input_json_str)
        jrpc_id = input_value["id"]

        # value retrieved is 'result' field as per Spec 7.2.5 Receipt Retrieve Response Payload
        value = self.kv_helper.get("wo-receipts",wo_id)

        if value :
            updater_id = input_value["params"]['updaterId']
            update_index = input_value["params"]['updateIndex']

            json_dict = json.loads(value)
            updater_objects = json_dict['result']['updater']

            update_count = 0
            result_item = {}
            for item in updater_objects:
                id = updater_objects[item]['updaterId']
                if id == updater_id :
                    #Considering Index 0 as  first update
                    if update_count == update_index :
                        result_item = updater_objects[item]
                #the total number of updates made by the updaterId.
                update_count = update_count+1

            response['result'] = {}
            response['result'] = result_item
            response['result']['updateCount'] = update_count

        else:
            response = utility.create_error_response(
                WorkorderError.INVALID_PARAMETER_FORMAT_OR_VALUE,
                jrpc_id,
                "Work order id not found in the database. \
                 Hence invalid parameter")

        return response
# ------------------------------------------------------------------------------------------------

    def workorder_receipt_handler(self, input_json_str):
        """
        Function to process work order receipt request
        Parameters:
            - input_json_str is a work order receipt request json
              as per TCF API 7.2 Direct Model Receipt Handling
        """
        input_json = json.loads(input_json_str)
        response = {}
        response['jsonrpc'] = input_json['jsonrpc']
        response['id'] = input_json['id']

        logger.info("Received Work order Receipt request : %s",input_json['method'])
        if(input_json['method'] == "WorkOrderReceiptLookUp") :
            return self.__process_workorder_receipt_lookup(input_json_str, response)
        elif(input_json['method'] == "WorkOrderReceiptLookUpNext") :
            return self.__process_workorder_receipt_lookup_next(input_json_str, response)

        if 'workOrderId' in input_json_str:
           wo_id = str(input_json['params']['workOrderId'])
        else :
           response = utility.create_error_response(
                WorkorderError.INVALID_PARAMETER_FORMAT_OR_VALUE,
                input_json['id'],
                "Work order id not found in the database. \
                 Hence invalid parameter")
           return response

        jrpc_id = input_json['id']
        if(input_json['method'] == "WorkOrderReceiptCreate") :
            return self.__process_store_workorder_receipt(wo_id, input_json_str, response)
        elif(input_json['method'] == "WorkOrderReceiptUpdate") :
            return self.__process_workorder_receipt_update(wo_id, input_json_str, response)
        elif(input_json['method'] == "WorkOrderReceiptRetrieve") :
            return self.__process_workorder_receipt_retrieve(wo_id, jrpc_id, response)
        elif(input_json['method'] == "WorkOrderReceiptUpdateRetrieve") :
            return self.__process_workorder_receipt_update_retrieve(wo_id,input_json_str, response)
# ------------------------------------------------------------------------------------------------

