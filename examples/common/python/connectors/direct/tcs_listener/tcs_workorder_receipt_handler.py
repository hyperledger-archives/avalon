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
from error_code.error_status import WorkOrderStatus

from jsonrpc.exceptions import JSONRPCDispatchException

logger = logging.getLogger(__name__)


def must_get_work_order_id(params):
    if "workOrderId" not in params:
        raise JSONRPCDispatchException(
            WorkOrderStatus.INVALID_PARAMETER_FORMAT_OR_VALUE,
            "Work order id not found in the database. Hence invalid parameter")

    return str(params["workOrderId"])


class TCSWorkOrderReceiptHandler:
    """
    TCSWorkOrderReceiptHandler processes Work Order Receipt Direct API requests.
    It reads appropriate work order information from the KV storage to create
    the response. Work order receipts are created and placed in the KV storage
    by the SGX Enclave Manager after the work order (successfully) completed.
    All raised exceptions will be caught and handled by any
    jsonrpc.dispatcher.Dispatcher delegating work to this handler. In our case,
    the exact dispatcher will be the one configured by the TCSListener in the
    ./tcs_listener.py
    """
# ------------------------------------------------------------------------------------------------

    def __init__(self, kv_helper):
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

    def WorkOrderReceiptCreate(self, **params):
        """
        Function to process work order request
        Parameters:
            - params is the "params" object in the a worker request as per TCF
              API 7.2.2 Receipt Create Request Payload
        """

        wo_id = must_get_work_order_id(params)

        if self.kv_helper.get("wo-receipts", wo_id) is not None:
            raise JSONRPCDispatchException(
                WorkOrderStatus.INVALID_PARAMETER_FORMAT_OR_VALUE,
                "Work order receipt already exist in the database. Hence"
                + "invalid parameter")

        value = self.kv_helper.get("wo-requests", wo_id)
        if not value:
            raise JSONRPCDispatchException(
                WorkOrderStatus.INVALID_PARAMETER_FORMAT_OR_VALUE,
                "Work order does not exists. Hence invalid parameter")

        # sanitize params
        params["receiptCurrentStatus"] = ReceiptCreateStatus.PENDING
        # Updater is introduced to maintain multiple update details on a receipt
        params["updater"] = {}

        receipt_json = json.dumps({"result": params})
        self.kv_helper.set("wo-receipts", wo_id, receipt_json)

        raise JSONRPCDispatchException(
            WorkOrderStatus.SUCCESS, "Receipt created successfully")

# ------------------------------------------------------------------------------------------------

    def WorkOrderReceiptUpdate(self, **params):
        """
        Function to process update work order request
        Parameters:
            - params is the "params" object in the a worker request as per TCF
              API 7.2.6 Receipt Update Retrieve Request Payload
        """

        wo_id = must_get_work_order_id(params)

        # value retrieved is 'result' field as per Spec 7.2.5 Receipt Retrieve
        # Response Payload
        value = self.kv_helper.get("wo-receipts", wo_id)

        if not value:
            raise JSONRPCDispatchException(
                WorkOrderStatus.INVALID_PARAMETER_FORMAT_OR_VALUE,
                "Work order id not found in the database. Hence invalid"
                + " parameter")

        # WorkorderId already a part of receipt. And will be not change for a
        # given receipt. Hence it's not stored in updater param.
        del params["workOrderId"]

        receipt = json.loads(value)

        updaters = receipt["result"]["updater"]
        if len(updaters) > 0:
            # Updater Object is sorted based on index and then last index is
            # chosen
            index = int(sorted(updaters.keys())[-1]) + 1
        else:
            index = 0

        updaters[index] = params
        receipt["result"]["receiptCurrentStatus"] = params["updateType"]
        receipt["result"]["updater"] = updaters

        self.kv_helper.set("wo-receipts", wo_id, json.dumps(receipt))

        raise JSONRPCDispatchException(
            WorkOrderStatus.SUCCESS, "Receipt Successfully Updated")

# ------------------------------------------------------------------------------------------------

    def __lookup_basics(self, is_lookup_next, params):
        self.receipt_pool = self.kv_helper.lookup("wo-receipts")

        total_count = 0
        ids = []
        lookupTag = ""

        for wo_id in self.receipt_pool:
            if is_lookup_next:
                is_lookup_next = (wo_id != params["lastLookUpTag"])
                continue

            value = self.kv_helper.get("wo-receipts", wo_id)
            if not value:
                continue

            criteria = ["workerServiceId",
                        "workerId", "requesterId", "status"]

            wo = json.loads(value)
            matched = True
            for c in criteria:
                if c not in params:
                    continue

                matched = (wo[c] == params[c])
                if not matched:
                    break

            if matched:
                total_count = total_count+1
                ids.append(wo_id)
                lookupTag = wo_id

        result = {
            "totalCount": total_count,
            "lookupTag": lookupTag,
            "ids": ids,
        }

        return result

# ------------------------------------------------------------------------------------------------

    def WorkOrderReceiptLookUp(self, **params):
        """
        Function to look the set of work order receipts available
        Parameters:
            - params is the "params" object in the a worker request as per TCF
              API 7.2.8 Receipt Lookup Request Payload
        """

        return self.__lookup_basics(False, params)
# ------------------------------------------------------------------------------------------------

    def WorkOrderReceiptLookUpNext(self, **params):
        """
        Function to look the set of work order receipt newly added
        Parameters:
            - params is the "params" object in the a worker request as per TCF
              API 7.2.10 Receipt Lookup Next Request Payload
        """

        return self.__lookup_basics(True, params)
# ------------------------------------------------------------------------------------------------

    def WorkOrderReceiptRetrieve(self, **params):
        """
        Function to retrieve the details of worker
        Parameters:
            - params is the "params" object in the a worker request as per TCF
              API 7.2.4 Receipt Retrieve Request Payload
        """

        wo_id = must_get_work_order_id(params)

        # value retrieved is 'result' field as per Spec 7.2.5 Receipt Retrieve
        # Response Payload
        value = self.kv_helper.get("wo-receipts", wo_id)

        if not value:
            raise JSONRPCDispatchException(
                WorkOrderStatus.INVALID_PARAMETER_FORMAT_OR_VALUE,
                "Work order id not found in the database. Hence invalid" +
                " parameter")

        receipt = json.loads(value)
        if "result" not in receipt:
            # Need to revisit code when actual receipts are created
            return receipt["error"]

        return receipt["result"]

# ------------------------------------------------------------------------------------------------

    def WorkOrderReceiptUpdateRetrieve(self, **params):
        """
        Function to process work order receipt update retrieve
        Parameters:
            - params is the "params" object in the a worker request as per TCF
              API 7.2.6 Receipt Update Retrieve Request Payload
        """

        wo_id = must_get_work_order_id(params)

        # value retrieved is 'result' field as per Spec 7.2.5 Receipt Retrieve
        # Response Payload
        receipt_json = self.kv_helper.get("wo-receipts", wo_id)
        if not receipt_json:
            raise JSONRPCDispatchException(
                WorkOrderStatus.INVALID_PARAMETER_FORMAT_OR_VALUE,
                "Work order id not found in the database. Hence invalid" +
                " parameter")

        updater_id = params["updaterId"]
        update_index = params["updateIndex"]

        updaters = json.loads(receipt_json).get("result").get("updater")

        update_count = 0
        result = {}
        for k in updaters:
            if updaters[k]["updaterId"] == updater_id:
                # Considering Index 0 as first update
                if update_count == update_index:
                    result = updaters[k]

            # the total number of updates made by the updaterId.
            update_count = update_count+1

        result["updateCount"] = update_count

        return result

# ------------------------------------------------------------------------------------------------
