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
from utility.hex_utils import is_valid_hex_str

from avalon_sdk.http_client.http_jrpc_client import HttpJrpcClient
from avalon_sdk.interfaces.work_order_receipt \
    import WorkOrderReceipt
from avalon_sdk.work_order_receipt.work_order_receipt \
    import ReceiptCreateStatus

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class JRPCWorkOrderReceiptImpl(WorkOrderReceipt):
    """
    This class is an implementation of WorkOrderReceiptInterface
    to manage work order receipt from client side.
    """
    def __init__(self, config):
        self.__uri_client = HttpJrpcClient(config["tcf"]["json_rpc_uri"])

    def work_order_receipt_create(
            self, work_order_id,
            worker_service_id,
            worker_id,
            requester_id,
            receipt_create_status,
            work_order_request_hash,
            requester_nonce,
            requester_signature,
            signature_rules,
            receipt_verification_key,
            id=None):
        """
        Creating a Work Order Receipt json rpc request and submit tcs listener
        """
        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkOrderReceiptCreate",
            "id": id,
            "params": {
                "workOrderId": work_order_id,
                "workerServiceId": worker_service_id,
                "workerId": worker_id,
                "requesterId": requester_id,
                "receiptCreateStatus": receipt_create_status,
                "workOrderRequestHash": work_order_request_hash,
                "requesterGeneratedNonce": requester_nonce,
                "requesterSignature": requester_signature,
                "signatureRules": signature_rules,
                "receiptVerificationKey": receipt_verification_key
            }
        }
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    def work_order_receipt_update(
            self, work_order_id,
            updater_id,
            update_type,
            update_data,
            update_signature,
            signature_rules, id=None):
        """
        Update a Work Order Receipt json rpc request and submit tcs listener
        """
        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkOrderReceiptUpdate",
            "id": id,
            "params": {
                "workOrderId": work_order_id,
                "updaterId": updater_id,
                "updateType": update_type,
                "updateData": update_data,
                "updateSignature": update_signature,
                "signatureRules": signature_rules
            }
        }
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    def work_order_receipt_retrieve(self, work_order_id, id=None):
        """
        Retrieve a Work Order Receipt json rpc request and submit tcs listener
        """
        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkOrderReceiptRetrieve",
            "id": id,
            "params": {
                "workOrderId": work_order_id
            }
        }
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    def work_order_receipt_update_retrieve(
            self, work_order_id,
            updater_id,
            update_index, id=None):
        """
        Retrieving a Work Order Receipt Update
        """
        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkOrderReceiptUpdateRetrieve",
            "id": id,
            "params": {
                "workOrderId": work_order_id,
                "updaterId": updater_id,
                "updateIndex": update_index
            }
        }
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    def work_order_receipt_lookup(
            self, worker_service_id=None,
            worker_id=None, requester_id=None, receipt_status=None, id=None):
        """
        Work Order Receipt Lookup
        """
        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkOrderReceiptLookUp",
            "id": id,
            "params": {
            }
        }

        if worker_service_id is not None:
            json_rpc_request["params"]["workerServiceId"] = worker_service_id

        if worker_id is not None:
            json_rpc_request["params"]["workerId"] = worker_id

        if requester_id is not None:
            json_rpc_request["params"]["requesterId"] = requester_id

        if receipt_status is not None:
            json_rpc_request["params"]["requestCreateStatus"] = receipt_status

        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    def work_order_receipt_lookup_next(
            self, last_lookup_tag,
            worker_service_id=None, worker_id=None, requester_id=None,
            receipt_status=None, id=None):
        """
        Work Order Receipt Lookup Next
        """
        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkOrderReceiptLookUpNext",
            "id": id,
            "params": {
                "lastLookUpTag": last_lookup_tag
            }
        }

        if worker_service_id is not None:
            json_rpc_request["params"]["workerServiceId"] = worker_service_id

        if worker_id is not None:
            json_rpc_request["params"]["workerId"] = worker_id

        if requester_id is not None:
            json_rpc_request["params"]["requesterId"] = requester_id

        if receipt_status is not None:
            json_rpc_request["params"]["requestCreateStatus"] = receipt_status

        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response
