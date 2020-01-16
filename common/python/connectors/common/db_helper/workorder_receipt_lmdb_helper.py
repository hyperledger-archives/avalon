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
import logging
from error_code.error_status import ReceiptCreateStatus, SignatureStatus,\
    JRPCErrorCodes
from jsonrpc.exceptions import JSONRPCDispatchException

logger = logging.getLogger(__name__)


class WorkOrderReceiptLmdbHelper:
    """
    WorkOrderReceiptDBHelper helps listener or other client facing modules
    to interact with the kv storage for queries related to work order
    receipts' processing.
    """
# -----------------------------------------------------------------------------

    def __init__(self, kv_helper):
        """
        Function to perform init activity
        Parameters:
            - kv_helper is a object of lmdb database
        """
        # Special index 0xFFFFFFFF value to fetch last update to receipt
        self.LAST_RECEIPT_INDEX = 1 << 32
        self.kv_helper = kv_helper

# -----------------------------------------------------------------------------
    def get_wo_req(self, wo_id):
        """
        Function to get a work-order request
        Parameters:
            - wo_id: work-order id
        Return the work-order request corresponding to the id
        """
        return self.kv_helper.get("wo-requests", wo_id)

# -----------------------------------------------------------------------------

    def get_wo_receipt(self, wo_id):
        """
        Function to get a work-order receipt
        Parameters:
            - wo_id: work-order id
        Return the work-order receipt corresponding to the id
        """
        return self.kv_helper.get("wo-receipts", wo_id)

# -----------------------------------------------------------------------------

    def save_wo_receipt(self, wo_id, input_str):
        """
        Function to save a work-order receipt in the database
        Parameters:
            - wo_id: id of work-order
            - input_str: the actual receipt
        """
        self.kv_helper.set("wo-receipts", wo_id, input_str)

# -----------------------------------------------------------------------------

    def get_wo_receipt_update(self, wo_id):
        """
        Function to get work-order receipt updates
        Parameters:
            - wo_id: id of work-order for which receipt updates are required
        Returns the receipt update for corresponding id
        """
        return self.kv_helper.get("wo-receipt-updates", wo_id)

# -----------------------------------------------------------------------------

    def save_receipt_update(self, wo_id, updated_receipt):
        """
        Function to save work-order receipt updates
        Parameters:
            - wo_id: id of work-order for which receipt updates are intended
            - updated_receipt: the content of the updated receipt to be stored
        """
        self.kv_helper.set("wo-receipt-updates", wo_id, updated_receipt)

# -----------------------------------------------------------------------------

    def retrieve_wo_receipt(self, wo_id):
        """
        Function to retrieve details of work-order receipt
        Parameters:
            - wo_id: id of work-order for which receipt details
             are required
        Returns details of a receipt
        """
        value = self.kv_helper.get("wo-receipts", wo_id)
        if value:
            receipt = json.loads(value)
            receipt_updates = self.kv_helper.get("wo-receipt-updates", wo_id)
            if receipt_updates is None:
                receipt["params"]["receiptCurrentStatus"] = \
                    receipt["params"]["receiptCreateStatus"]
            else:
                receipt_updates_json = json.loads(receipt_updates)
                # Get the recent update to receipt
                last_receipt = receipt_updates_json[len(receipt_updates_json)
                                                    - 1]
                receipt["params"]["receiptCurrentStatus"] = \
                    last_receipt["updateType"]
            return receipt["params"]
        else:
            raise JSONRPCDispatchException(
                JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                "Work order receipt for work order id {} not found in the "
                "database. Hence invalid parameter".format(
                    wo_id
                ))

# -----------------------------------------------------------------------------

    def retrieve_wo_receipt_update(self, wo_id, update_index, updater_id):

        """
        Function to retrieve a specific(by index) update for a specific
        updater-id for a work-order id
        Parameters:
            - wo_id: id of work-order for which the receipt is being
            queried
            - update_index: index of update for this specific receipt
            - updater_id: id of updater
        Returns
        """
        receipt_updates = self.kv_helper.get("wo-receipt-updates", wo_id)

        if receipt_updates:
            receipt_updates_json = json.loads(receipt_updates)
            total_updates = len(receipt_updates_json)
            if update_index <= 0:
                raise JSONRPCDispatchException(
                    JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                    "Update index should be positive non-zero number."
                    " Hence invalid parameter")
            elif update_index > total_updates:
                if update_index == self.LAST_RECEIPT_INDEX:
                    # set to the index of last update to receipt
                    update_index = total_updates - 1
                else:
                    raise JSONRPCDispatchException(
                        JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                        "Update index is larger than total update count."
                        " Hence invalid parameter")
            else:
                # If the index is less than total updates
                # then decrement by one since it is zero based array
                update_index = update_index - 1
            update_to_receipt = receipt_updates_json[update_index]
            # If updater id is present then check whether it matches
            if updater_id:
                if update_to_receipt["updaterId"] != updater_id:
                    raise JSONRPCDispatchException(
                        JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                        "Update index and updater id doesn't match."
                        " Hence invalid parameter")
            update_to_receipt["updateCount"] = total_updates
            return update_to_receipt
        else:
            raise JSONRPCDispatchException(
                JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                "There is no updates available to this receipt."
                " Hence invalid parameter")
