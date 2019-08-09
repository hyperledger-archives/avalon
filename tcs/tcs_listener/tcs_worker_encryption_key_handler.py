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
import crypto.crypto as crypto
from error_code.error_status import WorkerError
from shared_kv.shared_kv_interface import KvStorage
import utils.utility as utility

logger = logging.getLogger(__name__)
#No of bytes of encryptionKeyNonce to encrypt data
NO_OF_BYTES = 16

## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
class WorkerEncryptionKeyHandler:
    """
    TCSEncryptionKeyHandler processes Workers Encryption Key Direct API requests. 
    It is used if the Worker supports requester specific encryption keys in addition or instead of the encryptionKey defined 
    in section Appendix A: Worker Specific Detailed Data.
    """
# ------------------------------------------------------------------------------------------------
    def __init__(self,kv_helper):
        """
        Function to perform init activity
        Parameters:
            - kv_helper is a object of lmdb database
        """

        self.kv_helper = kv_helper

#---------------------------------------------------------------------------------------------
    def process_encryption_key(self, input_json_str):
        """
        Function to process encryption key request
        Parameters:
            - input_json_str is defines a JSON RPC request that is called by a requester to receive a Worker's key 
            as per TCF API 6.1 Work Order Direct Mode Invocation
        """

        input_json = json.loads(input_json_str)
        logger.info("Received encryption key request : %s",input_json['method'])

        response = {}
        response['jsonrpc'] = '2.0'
        response['id'] = input_json['id']

        if(input_json['method'] == "EncryptionKeyGet"):
            return self.__process_encryption_key_get(input_json_str, response)
        elif(input_json['method'] == "EncryptionKeySet"):
            return self.__process_encryption_key_set(input_json_str, response)
        else :
            return None

#---------------------------------------------------------------------------------------------
    def __process_encryption_key_set(self, input_json_str, response):
        """
        Function to process set encryption key request.
        Parameters:
            - input_json_str is a work order request json as per TCF API 6.1.11 Set Encryption Key Request Payload
            - response is the response object to be returned
        """

        input_json = json.loads(input_json_str)
        jrpc_id = input_json["id"]
        response = utility.create_error_response(
                WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE, jrpc_id,
                "Operation is not supported. Hence invalid parameter")
        return response

#---------------------------------------------------------------------------------------------
    def __process_encryption_key_get(self, input_json_str, response):
        """
        Function to process get encryption key request.
        Parameters:
            - input_json_str is a work order request json as per TCF API 6.1.10 Get Encryption Key Request Payload
            - response is the response object to be returned
        """

        input_json = json.loads(input_json_str)
        jrpc_id = input_json["id"]
        worker_id = str(input_json['params']['workerId'])
        value = self.kv_helper.get("workers", worker_id)

        if value is not None:
            json_dict = json.loads(value)
            response["result"] = {}
            response["result"]["workerId"] = worker_id
            encryptionKey = json_dict["details"]["workerTypeData"]["encryptionKey"]
            try :
                encryptionKeyNonce = json_dict["details"]["workerTypeData"]["encryptionKeyNonce"]
            except :
                encryptionKeyNonce = crypto.random_bit_string(NO_OF_BYTES)
            tag = ""
            response["result"]["encryptionKey"] = encryptionKey
            response["result"]["encryptionKeyNonce"] = encryptionKeyNonce
            response["result"]["tag"] = tag
            #calculate signature
            concat_string = worker_id.encode('UTF-8') + encryptionKey.encode('UTF-8') + encryptionKeyNonce.encode('UTF-8') + tag.encode('UTF-8')
            concat_hash =  bytes()
            concat_hash =  bytes(concat_string)
            hash_1 = crypto.compute_message_hash(concat_hash)
            s1 = crypto.byte_array_to_base64(hash_1)
            # Requires worker private key to sign.
            # signature =  self.PrivateKey.SignMessage(hash)
            response["result"]["signature"] = s1
        else :
            # Workorder id already exists
            response = utility.create_error_response(
                    WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE, jrpc_id,
                    "Worker id not found in the database. Hence invalid parameter")

        return response
#---------------------------------------------------------------------------------------------

