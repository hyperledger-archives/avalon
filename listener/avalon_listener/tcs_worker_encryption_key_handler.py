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
import crypto_utils.crypto.crypto as crypto
from error_code.error_status import WorkerError

from jsonrpc.exceptions import JSONRPCDispatchException

logger = logging.getLogger(__name__)
# No of bytes of encryptionKeyNonce to encrypt data
NO_OF_BYTES = 16

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


class WorkerEncryptionKeyHandler:
    """
    TCSEncryptionKeyHandler processes Workers Encryption Key Direct API
    requests.
    It is used if the Worker supports requester specific encryption keys in
    addition or instead of the encryptionKey defined in section Appendix A:
    Worker Specific Detailed Data.
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

# ---------------------------------------------------------------------------------------------
    def EncryptionKeySet(self, **params):
        """
        Function to process set encryption key request.
        Parameters:
            - param is the 'param' object in the a worker request as per TCF
                API 6.1.11 Set Encryption Key Request Payload
        """

        raise JSONRPCDispatchException(
            WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE,
            "Operation is not supported. Hence invalid parameter")

# ---------------------------------------------------------------------------------------------
    def EncryptionKeyGet(self, **params):
        """
        Function to process get encryption key request.
        Parameters:
            - param is the 'param' object in the a worker request as per TCF
                API 6.1.10 Get Encryption Key Request Payload
        """

        worker_id = str(params['workerId'])
        value = self.kv_helper.get("workers", worker_id)

        if value is None:
            raise JSONRPCDispatchException(
                WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE,
                "Worker id not found in the database. Hence invalid parameter")

        worker_type_data = json.loads(value).get(
            "details").get("workerTypeData")
        encryptionKey = worker_type_data["encryptionKey"]
        try:
            encryptionKeyNonce = worker_type_data["encryptionKeyNonce"]
        except Exception:
            encryptionKeyNonce = crypto.random_bit_string(NO_OF_BYTES)

        tag = ""
        # calculate signature
        concat_string = worker_id.encode('UTF-8') + encryptionKey.encode(
            'UTF-8') + encryptionKeyNonce.encode('UTF-8') + tag.encode('UTF-8')
        concat_hash = bytes(concat_string)
        hash_1 = crypto.compute_message_hash(concat_hash)
        s1 = crypto.byte_array_to_base64(hash_1)
        # Requires worker private key to sign.
        # signature =  self.PrivateKey.SignMessage(hash)

        result = {
            "workerId": worker_id,
            "encryptionKey": encryptionKey,
            "encryptionKeyNonce": encryptionKeyNonce,
            "tag": "",
            "signature": s1,
        }

        return result

# ---------------------------------------------------------------------------------------------
