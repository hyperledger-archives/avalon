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
from utility.hex_utils import is_valid_hex_str
from avalon_sdk.http_client.http_jrpc_client import HttpJrpcClient
from avalon_sdk.interfaces.work_order import WorkOrder
from error_code.error_status import WorkOrderStatus, JRPCErrorCodes

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class JRPCWorkOrderImpl(WorkOrder):
    """
    This class is for to manage to the work orders from client side.
    """

    def __init__(self, config):
        self.__uri_client = HttpJrpcClient(config["tcf"]["json_rpc_uri"])

    def work_order_submit(self, work_order_id, worker_id,
                          requester_id, work_order_request, id=None):
        """
        Submit work order request to avalon listener.
        work_order_request is work order request in json string format.
        """
        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkOrderSubmit",
            "id": id
        }
        json_rpc_request["params"] = json.loads(work_order_request)

        logging.debug("Work order request %s", json.dumps(json_rpc_request))
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    def work_order_get_result_nonblocking(self, work_order_id, id=None):
        """
        Get the work order result in non-blocking way.
        It return json rpc response of dictionary type
        """
        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkOrderGetResult",
            "id": id,
            "params": {
                "workOrderId": work_order_id
            }
        }
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    def work_order_get_result(self, work_order_id, id=None):
        """
        Get the work order result in blocking way until it get the result/error
        It return json rpc response of dictionary type
        """
        response = self.work_order_get_result_nonblocking(work_order_id, id)
        if "error" in response:
            if response["error"]["code"] != WorkOrderStatus.PENDING:
                return response
            else:
                while "error" in response and \
                        response["error"]["code"] == WorkOrderStatus.PENDING:
                    response = self.work_order_get_result_nonblocking(
                        work_order_id, id)
                    # TODO: currently pooling after every 2 sec interval
                    # forever.
                    # We should implement feature to timeout after
                    # responseTimeoutMsecs in the request.
                    time.sleep(2)
                return response

    def encryption_key_get(self, worker_id, requester_id,
                           last_used_key_nonce=None, tag=None,
                           signature_nonce=None, signature=None, id=None):
        """
        API to receive a Worker's key
        parameters
            worker_id is the id of the worker whose
            encryption key is requested.
            last_used_key_nonce is an optional nonce associated
            with last retrieved key. If it is provided,
            the key retrieved should be newer than this one.
            Otherwise any key can be retrieved.
            tag is tag that should be associated with the returned key
            e.g. requester id. This is an optional parameter.
            If it is not provided, requesterId is used as a key.
            requester_id is the id of the requester that plans to use
            the returned key to submit one or more work orders using this key.
            signature_nonce is an optional parameter and is used only if
            signature below is also provided.
            signature is an optional signature
            of worker_id, last_used_key_nonce, tag, and signature_nonce.
        """
        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "EncryptionKeyGet",
            "id": id,
            "params": {
                "workerId": worker_id,
                "lastUsedKeyNonce": last_used_key_nonce,
                "tag": tag,
                "requesterId": requester_id,
                "signatureNonce": signature_nonce,
                "signature": signature
            }
        }
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    def encryption_key_set(self, worker_id, encryption_key, encryption_nonce,
                           tag, signature_nonce, signature, id=None):
        """
        API called by a Worker or Worker Service to receive a Worker's key.
        parameters
            1. worker_id is an id of the worker to retrieve an encryption
            key for.
            2. encryption_key is an encryption key.
            3. encryption_nonce is a nonce associated with the key.
            4. tag is tag that should be associated with the returned key,
            e.g. requester id. This is an optional parameter. If it is not
             provided, requesterId below is used as a key.
            5.signature is a signature generated by
            the worker on the worker_id, tag and encryption_nonce.
        Returns
            jrpc response with the result of the operation.
        """
        # Not supported for direct model.
        return {
            "jsonrpc": "2.0",
            "method": "EncryptionKeySet",
            "id": id,
            "result": {
                "code": JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                "message": "Unsupported method"
            }
        }
