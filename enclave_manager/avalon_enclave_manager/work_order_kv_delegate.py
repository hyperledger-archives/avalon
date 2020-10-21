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
import avalon_crypto_utils.worker_signing as worker_signing
from error_code.error_status import ReceiptCreateStatus, WorkOrderStatus
from avalon_sdk.work_order_receipt.work_order_receipt \
    import WorkOrderReceiptRequest

logger = logging.getLogger(__name__)


class WorkOrderKVDelegate:
    """
    Delegate class for enclave managers to make work order
    specific changes in the KV storage.
    """

    def __init__(self, kv_helper, worker_id):
        self._kv_helper = kv_helper
        self._worker_id = worker_id
        # Key pair for work order receipt signing
        # This is temporary approach
        signer = worker_signing.WorkerSign()
        signer.generate_signing_key()
        self.private_key = signer.sign_private_key
        self.public_key = signer.get_public_sign_key()

    def cleanup_work_orders(self):
        """
        Remove all responses that have been generated for all work order id
        processed by this worker. This is done as the key pair will change
        with the restart of a worker i.e.- Singleton or KME. Since the keys
        used previously are no more available in the worker details, the
        response cannot be verified. Hence they are stale and not useful.
        """
        # Get all work order ids that have been processed by this worker
        # i.e.- Singleton or KME (WPEs using this KME). This list is a
        # comma separated value string which needs to be split to obtain
        # the actual work order ids.
        logger.info("About to start removing stale work orders from database.")
        wo_ids = self._kv_helper.get("wo-worker-processed", self._worker_id)
        if wo_ids is None:
            logger.info("No stale work order found. Cleanup not needed.")
            return
        wo_id_list = wo_ids.split(",")

        count = 0
        for wo_id in wo_id_list:
            self._kv_helper.remove("wo-responses", wo_id)
            self._kv_helper.remove("wo-requests", wo_id)
            self._kv_helper.remove("wo-receipts", wo_id)
            self._kv_helper.remove("wo-timestamps", wo_id)
            count += 1
        self._kv_helper.remove("wo-worker-processed", self._worker_id)
        logger.info("Purged %d work orders from database.", count)

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
        if receipt_entry:
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
            updated_receipt = None
            # load previous updates to receipt
            updates_to_receipt = self._kv_helper.get(
                "wo-receipt-updates", wo_id)
            # If it is first update to receipt
            if updates_to_receipt is None:
                updated_receipt = []
            else:
                updated_receipt = json.loads(updates_to_receipt)
                # Get the last update to receipt
                last_receipt = updated_receipt[len(updated_receipt) - 1]

                # If receipt updateType is completed,
                # then no further update allowed
                if last_receipt["updateType"] == \
                        ReceiptCreateStatus.COMPLETED.value:
                    logger.info(
                        "Receipt for the workorder id %s is completed " +
                        "and no further updates are allowed",
                        wo_id)
                    return
            updated_receipt.append(wo_receipt)

            # Since receipts_json is jrpc request updating only params object.
            self._kv_helper.set("wo-receipt-updates", wo_id, json.dumps(
                updated_receipt))
            logger.info("Receipt for the workorder id %s is updated to %s",
                        wo_id, wo_receipt)
        else:
            logger.info("Work order receipt is not created, " +
                        "so skipping the update")
