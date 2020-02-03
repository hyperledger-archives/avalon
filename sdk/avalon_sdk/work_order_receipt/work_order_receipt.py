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
import random

import crypto_utils.crypto.crypto as crypto
import crypto_utils.signature as signature
import crypto_utils.crypto_utility as crypto_utility
from error_code.error_status import ReceiptCreateStatus as ReceiptCreateStatus
from error_code.error_status import WorkOrderStatus
from enum import Enum, unique


@unique
class ReceiptCreateStatus(Enum):
    PENDING = 0
    COMPLETED = 1
    PROCESSED = 2
    FAILED = 3
    REJECTED = 4


class WorkOrderReceiptRequest():
    """
    Class to create work order receipt APIs like
    create, update, retrieve and lookup
    """

    def __init__(self):
        self.sig_obj = signature.ClientSignature()
        self.SIGNING_ALGORITHM = "SECP256K1"
        self.HASHING_ALGORITHM = "SHA-256"

    def create_receipt(self, wo_request,
                       receipt_create_status, signing_key, nonce=None):
        """
        Create work order receipt corresponding to workorder id
        Parameters:
            - wo_request is jrpc work order request used to create the
            work order request as defined in EEA spec 6.1.1.
            - receipt_create_status is enum of type ReceiptCreateStatus
            - signing_key is private key
            - nonce is int type random number or monotonic counter
        Returns jrpc request of type dictionary
        """
        final_hash_str = self.sig_obj.calculate_request_hash(wo_request)
        wo_request_params = wo_request["params"]
        worker_id = wo_request_params["workerId"]
        requester_nonce = nonce
        if nonce is None:
            requester_nonce = str(random.randint(1, 10**10))
        public_key = signing_key.GetPublicKey().Serialize()
        wo_receipt_request = {
            "workOrderId": wo_request_params["workOrderId"],
            # TODO: workerServiceId is same as worker id,
            # needs to be updated with actual service id
            "workerServiceId": worker_id,
            "workerId": worker_id,
            "requesterId": wo_request_params["requesterId"],
            "receiptCreateStatus": receipt_create_status,
            "workOrderRequestHash": final_hash_str,
            "requesterGeneratedNonce": requester_nonce,
            "signatureRules":
            self.HASHING_ALGORITHM + "/" + self.SIGNING_ALGORITHM,
            "receiptVerificationKey": public_key
        }
        wo_receipt_str = wo_receipt_request["workOrderId"] + \
            wo_receipt_request["workerServiceId"] + \
            wo_receipt_request["workerId"] + \
            wo_receipt_request["requesterId"] + \
            str(wo_receipt_request["receiptCreateStatus"]) + \
            wo_receipt_request["workOrderRequestHash"] + \
            wo_receipt_request["requesterGeneratedNonce"]
        wo_receipt_bytes = bytes(wo_receipt_str, "UTF-8")
        wo_receipt_hash = crypto.compute_message_hash(wo_receipt_bytes)
        status, wo_receipt_sign = self.sig_obj.generate_signature(
            wo_receipt_hash,
            signing_key
        )
        if status is False:
            # if generate signature is failed.
            wo_receipt_request["requesterSignature"] = ""
            raise Exception("Generate signature is failed")
        else:
            wo_receipt_request["requesterSignature"] = wo_receipt_sign
        return wo_receipt_request

    def update_receipt(self, work_order_id, update_type,
                       update_data, signing_key):
        """
        Update the existing work order receipt with
        update_type, update_data.
        Parameters:
            - work_order_id is work order id whose receipt
              needs to be updated.
            - update_type is integer, these values corresponds to
              receipt status as defined in 7.1.1
            - update_data is update-specific data that depend on
              the workOrderStatus
        Returns jrpc work order update receipt request of type dictionary
        """
        data = update_data
        if update_type in [ReceiptCreateStatus.PROCESSED.value,
                           ReceiptCreateStatus.COMPLETED.value]:
            # Work Order Receipt status is set to be completed or processed,
            # then update_data should be work order response.
            wo_resp_str = json.dumps(update_data)
            wo_resp_bytes = bytes(wo_resp_str, "UTF-8")
            # Hash of work order response is update_data
            wo_resp_hash = crypto.compute_message_hash(wo_resp_bytes)
            wo_resp_hash_str = crypto.byte_array_to_hex(wo_resp_hash)
            data = wo_resp_hash_str
        public_key = signing_key.GetPublicKey().Serialize()
        updater_id = crypto_utility.strip_begin_end_public_key(public_key)

        wo_receipt_update = {
            "workOrderId": work_order_id,
            "updaterId": updater_id,
            "updateType": update_type,
            "updateData": data,
            "signatureRules":
            self.HASHING_ALGORITHM + "/" + self.SIGNING_ALGORITHM,
            "receiptVerificationKey": public_key
        }
        wo_receipt_str = wo_receipt_update["workOrderId"] + \
            str(wo_receipt_update["updateType"]) + \
            wo_receipt_update["updateData"]
        wo_receipt_bytes = bytes(wo_receipt_str, "UTF-8")
        wo_receipt_hash = crypto.compute_message_hash(wo_receipt_bytes)
        status, wo_receipt_sign = self.sig_obj.generate_signature(
            wo_receipt_hash,
            signing_key
        )
        if status is False:
            # if generating signature failed.
            wo_receipt_update["updateSignature"] = ""
            raise Exception("Generate signature is failed")
        else:
            wo_receipt_update["updateSignature"] = wo_receipt_sign
        return wo_receipt_update
