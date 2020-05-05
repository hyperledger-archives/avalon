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
import logging
import avalon_crypto_utils.crypto_utility as crypto_utils
from error_code.error_status import ReceiptCreateStatus, WorkOrderStatus
from avalon_sdk.work_order_receipt.work_order_receipt \
    import WorkOrderReceiptRequest

logger = logging.getLogger(__name__)


class WorkOrderKVDelegate:
    """
    Delegate class for enclave managers to make work order
    specific changes in the KV storage.
    """

    def __init__(self, kv_helper):
        self._kv_helper = kv_helper
        # Key pair for work order receipt signing
        # This is temporary approach
        self.private_key = crypto_utils.generate_signing_keys()
        self.public_key = self.private_key.GetPublicKey().Serialize()

    def cleanup_work_orders(self, wo_ids=None):
        """
        Cleanup work orders that might have got stuck due
        to an abrupt shutdown of the system. Update their
        status in the corresponding tables if processing
        was complete but status not updated.
        Parameters :
            wo_ids - List of Work order id to be cleaned up. By default
            all will be cleaned up
        Returns :
            True - If all expected work order are removed successfully
            False - Otherwise

        """
        # @TODO : Enable cleanup for wo_ids passed in argument.
        # As of now a blanket cleanup is being done.
        processing_list = self._kv_helper.lookup("wo-processing")
        if len(processing_list) == 0:
            logger.info("No workorder entries found in " +
                        "wo-processing table, skipping Cleanup")
            return True
        result = True
        for wo in processing_list:
            logger.info("Validating workorders in wo-processing table")
            wo_json_resp = self._kv_helper.get("wo-responses", wo)
            wo_processed = self._kv_helper.get("wo-processed", wo)

            if wo_json_resp is not None:
                try:
                    wo_resp = json.loads(wo_json_resp)
                except ValueError as e:
                    logger.error(
                        "Invalid JSON format found for the response for " +
                        "workorder %s - %s", wo, e)
                    if wo_processed is None:
                        self._kv_helper.set("wo-processed", wo,
                                            WorkOrderStatus.FAILED.name)
                    result &= self._kv_helper.remove("wo-processing", wo)
                    continue

                if "Response" in wo_resp and \
                        wo_resp["Response"]["Status"] == \
                        WorkOrderStatus.FAILED:
                    if wo_processed is None:
                        self._kv_helper.set("wo-processed", wo,
                                            WorkOrderStatus.FAILED.name)
                    logger.error("Work order processing failed; " +
                                 "removing it from wo-processing table")
                    result &= self._kv_helper.remove("wo-processing", wo)
                    continue

                wo_receipt = self._kv_helper.get("wo-receipts", wo)
                if wo_receipt:
                    # update receipt
                    logger.info("Updating receipt in boot flow")
                    self.update_receipt(wo, wo_json_resp)
                    logger.info("Receipt updated for workorder %s during boot",
                                wo)

                if wo_processed is None:
                    self._kv_helper.set("wo-processed", wo,
                                        WorkOrderStatus.SUCCESS.name)
            else:
                logger.info("No response found for the workorder %s; " +
                            "hence placing the workorder request " +
                            "back in wo-scheduled", wo)
                self._kv_helper.set("wo-scheduled", wo,
                                    WorkOrderStatus.SCHEDULED.name)

            logger.info(
                "Finally deleting workorder %s from wo-processing table", wo)
            result &= self._kv_helper.remove("wo-processing", wo)

        return result

    def update_receipt(self, wo_id, wo_json_resp):
        """
        Update the existing work order receipt with the status as
        in wo_json_resp
        Parameters :
            wo_id - Is work order id of request for which receipt is to be
              updated.
            wo_json_resp - Is json rpc response of the work order execution.
            status of the work order receipt and updater signature update in
            the receipt.
        """
        receipt_entry = self._kv_helper.get("wo-receipts", wo_id)
        # If receipt is not created yet, add tag "receiptUpdates" to
        # Receipt entry and update it
        if receipt_entry is None:
            receipt_entry = {
                "params": {
                    "receiptUpdates": []
                }
            }
        # load previous updates to receipt
        receipt_update_entry = receipt_entry["params"]["receiptUpdates"]
        update_type = None
        if "error" in wo_json_resp and \
                wo_json_resp["error"]["code"] != \
                WorkOrderStatus.PENDING.value:
            update_type = ReceiptCreateStatus.FAILED.value
        else:
            update_type = ReceiptCreateStatus.PROCESSED.value
        receipt_obj = WorkOrderReceiptRequest()
        wo_receipt = receipt_obj.update_receipt(
            wo_id,
            update_type,
            wo_json_resp,
            self.private_key
        )

        # If it is first update to receipt
        if len(receipt_update_entry) > 0:
            # Get the last update to receipt
            last_receipt = receipt_update_entry[len(receipt_update_entry) - 1]
            # If receipt updateType is completed,
            # then no further update allowed
            if last_receipt["updateType"] == \
                    ReceiptCreateStatus.COMPLETED.value:
                logger.info(
                    "Receipt for the workorder id %s is completed " +
                    "and no further updates are allowed",
                    wo_id)
                return
        receipt_update_entry.append(wo_receipt)

        # Since receipts_json is jrpc request updating only params object.
        receipt_entry["receiptUpdates"] = receipt_update_entry
        self._kv_helper.set("wo-receipts", wo_id, json.dumps(
            receipt_entry))
        logger.info("Receipt for the workorder id %s is updated to %s",
                    wo_id, wo_receipt)
