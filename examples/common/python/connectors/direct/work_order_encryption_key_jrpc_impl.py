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
from utility.hex_utils import is_valid_hex_str
import base64
from service_client.generic import GenericServiceClient
from connectors.interfaces.work_order_encryption_key_interface import WorkOrderEncryptionKeyInterface
from connectors.utils import create_jrpc_response
from utility.tcf_types import JsonRpcErrorCode


logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class WorkOrderEncryptionKeyJrpcImpl(WorkOrderEncryptionKeyInterface):
    def __init__(self, config):
        self.__uri_client = GenericServiceClient(config["tcf"]["json_rpc_uri"])

    def encryption_key_get(self, worker_id, last_used_key_nonce, tag, requester_id,
            signature_nonce, signature, id=None):
        if not is_valid_hex_str(worker_id):
            logging.error("Invalid Worker id")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid Worker id")
        if last_used_key_nonce is not None and not is_valid_hex_str(last_used_key_nonce):
            logging.error("Invalid last used key nonce")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid last used key nonce")
        if tag is not None and not is_valid_hex_str(tag):
            logging.error("Invalid tag")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid tag")
        if requester_id is not None and not is_valid_hex_str(requester_id):
            logging.error("Invalid requester id")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid requester id")
        if signature_nonce is not None and not is_valid_hex_str(signature_nonce):
            logging.error("Invalid signature nonce")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid signature nonce")
        if signature is not None:
            try:
                base64.b64decode(signature)
            except Exception as e:
                logging.error("Invalid signature")
                return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                    "Invalid signature")

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

    def encryption_key_set(self, worker_id, encryption_key, encryption_key_nonce, tag,
            signature_nonce, signature, id=None):
        if not is_valid_hex_str(worker_id):
            logging.error("Invalid Worker id")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid Worker id")
        if not is_valid_hex_str(encryption_key):
            logging.error("Invalid encryption key")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid encryption key")
        if encryption_key_nonce is not None and not is_valid_hex_str(encryption_key_nonce):
            logging.error("Invalid encryption nonce")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid encryption nonce")
        if tag is not None and not is_valid_hex_str(tag):
            logging.error("Invalid tag")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid tag")
        if signature_nonce is not None and not is_valid_hex_str(signature_nonce):
            logging.error("Invalid signature nonce")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid signature nonce")
        if signature is not None:
            try:
                base64.b64decode(signature)
            except Exception as e:
                logging.error("Invalid signature")
                return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid signature")

        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "EncryptionKeySet",
            "id": id,
            "params": {
                "workerId": worker_id,
                "encryptionKey": encryption_key,
                "encryptionKeyNonce": encryption_key_nonce,
                "tag": tag,
                "signatureNonce": signature_nonce,
                "signature": signature
            }
        }
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response
