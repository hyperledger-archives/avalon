# Copyright 2019 Banco Santander S.A.
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

import base64
import json
import random
import logging

import encryptionAlg
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

logger = logging.getLogger(__name__)
# Number of bytes of encrypted session key to encrypt data
NO_OF_BYTES = 16


# -----------------------------------------------------------------------------
class ClientSignature(object):

    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.param_pool = ["requesterNonce", "workOrderId", "workerId",
            "requesterId", "inData"]

# -----------------------------------------------------------------------------
    def __payload_json_check(self, json_data):
        """
        Function to check if mandatory parameters are available as per param_pool
        Parameters:
            - json_data is a work order submit request json as per TCF API 6.1.1 Work Order Request Payload
        """

        data = json.loads(json_data)
        if 'params' not in data:
            logger.error("ERROR: Worker Order Submit Json does not have the required params")
            return False

        data_params = data['params']
        param_valid = True
        for param in self.param_pool:
            if (param not in data_params):
                # List down all the missing Parameters
                logger.error("ERROR: Worker Order Submit Json does not have the required parameter: %s", param)
                param_valid = False

        if param_valid:
            i_obj = data_params['inData']
            for obj in i_obj:
                if 'data' not in obj or not obj["data"] or 'index' not in obj:
                    logger.error("ERROR: Worker Order Submit Json does not have the required parameter in InData")
                    param_valid = False

        return param_valid

# -----------------------------------------------------------------------------
    def __encrypt_workorder_indata(self, input_json_params,
            session_key, session_iv, worker_encryption_key, data_key=None, data_iv=None):
        """
        Function to encrypt inData of workorder
        Parameters:
            - input_json_params is inData and outData elements within work order
              request as per TCF API 6.1.7 Work Order Data Formats
            - session_key is a one-time encryption key generated by the
              participant submitting the work order.
            - session_iv is an initialization vector if required by the
              data encryption algorithm (encryptedSessionKey). The default is all zeros.
            - data_key is a one time key generated by participant used to encrypt
              work order indata
            - data_iv is an initialization vector used along with data_key.
              Default is all zeros.
        """

        indata_objects = input_json_params['inData']
        indata_objects.sort(key=lambda x: x['index'])
        input_json_params['inData'] = indata_objects
        logger.info("Encrypting Workorder Data")

        i = 0
        for item in indata_objects:
            data = item['data'].encode('UTF-8')
            e_key = item['encryptedDataEncryptionKey'].encode('UTF-8')
            if (not e_key) or (e_key == "null".encode('UTF-8')):
                enc_data = self.encrypt_data(data, session_key, session_iv)
                input_json_params['inData'][i]['data'] = self.byte_array_to_base64(enc_data)
                logger.debug("encrypted indata - %s", self.byte_array_to_base64(enc_data))
            elif e_key == "-".encode('UTF-8'):
                # Skip encryption and just encode workorder data to base64 format
                input_json_params['inData'][i]['data'] = self.byte_array_to_base64(data)
            else:
                enc_data = self.encrypt_data(data, data_key, data_iv)
                input_json_params['inData'][i]['data'] = self.byte_array_to_base64(enc_data)
                logger.debug("encrypted indata - %s", self.byte_array_to_base64(enc_data))
            i = i + 1

        logger.debug("Workorder InData after encryption: %s", indata_objects)

# -----------------------------------------------------------------------------
    def encrypt_data(self, data, encryption_key, iv):
        encrypt = encryptionAlg.encAlgorithm()
        return encrypt.encrypt_data(data, encryption_key, iv)


# -----------------------------------------------------------------------------
    def __calculate_hash_on_concatenated_string(self, input_json_params, nonce_hash):
        """
        Function to calculate a hash value of the string concatenating the following values:
        requesterNonce, workOrderId, workerId, workloadId, and requesterId.
        Parameters:
            - input_json_params is a collection of parameters as per TCF APi 6.1.1 Work Order Request Payload
            - nonce_hash is SHA256 hashed value of a random string generated by the participant.
        """

        workorder_id = (input_json_params['workOrderId']).encode('UTF-8')
        worker_id = (input_json_params['workerId']).encode('UTF-8')
        workload_id = "".encode('UTF-8')
        if 'workloadId' in input_json_params:
            workload_id = (input_json_params['workloadId']).encode('UTF-8')
        requester_id = (input_json_params['requesterId']).encode('UTF-8')

        concat_string = nonce_hash + workorder_id + worker_id + workload_id + requester_id
        concat_hash = bytes(concat_string)
        # SHA-256 hashing is used
        hash_1 = self.compute_message_hash(concat_hash)
        result_hash = self.byte_array_to_base64(hash_1)

        return result_hash


# -----------------------------------------------------------------------------
    def __calculate_datahash(self, data_objects):
        """
        Function to calculate a hash value of the array concatenating
        dataHash, data, encryptedDataEncryptionKey, iv for each item in the
        inData/outData array
        Parameters:
            - data_objects is each item in inData or outData part of
              workorder request as per TCF API 6.1.7 Work Order Data Formats
        """

        hash_str = ""
        for item in data_objects:
            datahash = "".encode('UTF-8')
            e_key = "".encode('UTF-8')
            iv = "".encode('UTF-8')
            if 'dataHash' in item:
                datahash = item['dataHash'].encode('UTF-8')
            data = item['data'].encode('UTF-8')
            if 'encryptedDataEncryptionKey' in item:
                e_key = item['encryptedDataEncryptionKey'].encode('UTF-8')
            if 'iv' in item:
                iv = item['iv'].encode('UTF-8')
            concat_string = datahash + data + e_key + iv
            concat_hash = bytes(concat_string)
            hash = self.compute_message_hash(concat_hash)
            hash_str = hash_str + self.byte_array_to_base64(hash)

        return hash_str

# -----------------------------------------------------------------------------
    def __generate_signature(self, hash, private_key):
        """
        Function to generate signature object
        Parameters:
            - hash is the combined array of all hashes calculated on the message
            - private_key is Client private key
        """

        self.private_key = private_key
        self.public_key = self.private_key.getPublicKeySerialized()
        signature_base64 = self.private_key.sign_message(hash).toBase64()
        return signature_base64

# -----------------------------------------------------------------------------
    def generate_client_signature(self, input_json_str,
            worker, private_key, session_key, session_iv, encrypted_session_key,
            data_key=None, data_iv=None):
        """
        Function to generate client signature
        Parameters:
            - input_json_str is requester Work Order Request payload in a
              JSON-RPC based format defined 6.1.1 Work Order Request Payload
            - worker is a worker object to store all the common details of
              worker as per TCF API 8.1 Common Data for All Worker Types
            - private_key is Client private key
            - session_key is one time session key generated by the participant
              submitting the work order.
            - session_iv is an initialization vector if required by the
              data encryption algorithm (encryptedSessionKey). The default is all zeros.
            - data_key is a one time key generated by participant used to encrypt
              work order indata
            - data_iv is an intialization vector used along with data_key.
              Default is all zeros.
            - encrypted_session_key is a encrypted version of session_key.
        """

        if (self.__payload_json_check(input_json_str) is False):
            logger.error("ERROR: Signing the request failed")
            return None

        input_json = json.loads(input_json_str)
        input_json_params = input_json['params']
        input_json_params["sessionKeyIv"] = ''.join(format(i, '02x') for i in session_iv)

        encrypted_session_key_str = ''.join(format(i, '02x') for i in encrypted_session_key)
        self.__encrypt_workorder_indata(input_json_params, session_key,
                session_iv, worker.encryption_key, data_key, data_iv)
        # [NO_OF_BYTES] 16 BYTES for nonce, is the recommendation by NIST to
        # avoid collisions by the "Birthday Paradox".
        nonce = self.random_bit_string(NO_OF_BYTES)

        request_nonce_hash = self.compute_message_hash(nonce)
        nonce_hash = (self.byte_array_to_base64(request_nonce_hash)).encode('UTF-8')
        hash_string_1 = self.__calculate_hash_on_concatenated_string(input_json_params, nonce_hash)
        data_objects = input_json_params['inData']
        hash_string_2 = self.__calculate_datahash(data_objects)

        hash_string_3 = ""
        if 'outData' in input_json_params:
            data_objects = input_json_params['outData']
            data_objects.sort(key=lambda x: x['index'])
            hash_string_3 = self.__calculate_datahash(data_objects)

        concat_string = hash_string_1 + hash_string_2 + hash_string_3
        concat_hash = bytes(concat_string, 'UTF-8')
        final_hash = self.compute_message_hash(concat_hash)

        encrypted_request_hash = self.encrypt_data(final_hash, session_key, session_iv)
        encrypted_request_hash_str = ''.join(format(i, '02x') for i in encrypted_request_hash)
        logger.debug("encrypted request hash: \n%s", encrypted_request_hash_str)

        # Update the input json params
        input_json_params["encryptedRequestHash"] = encrypted_request_hash_str
        # input_json_params['requesterSignature'] = \
        #     self.__generate_signature(final_hash, private_key)
        input_json_params["encryptedSessionKey"] = encrypted_session_key_str
        # Temporary mechanism to share client's public key. Not a part of Spec
        input_json_params['verifyingKey'] = self.public_key
        input_json_params['requesterNonce'] = self.byte_array_to_base64(request_nonce_hash)
        input_json['params'] = input_json_params
        input_json_str = json.dumps(input_json)
        logger.info("Request Json successfully Signed")

        return input_json_str

# -----------------------------------------------------------------------------

    def byte_array_to_base64(self, byte_array):
        hash_b_arr = bytearray(list(byte_array))
        hash_b64 = base64.b64encode(hash_b_arr)
        hash_b64_str = str(hash_b64, 'utf-8')

        return hash_b64_str

# -----------------------------------------------------------------------------

    def base64_to_byte_array(self, b64_str):
        hash_b64 = bytearray(b64_str, 'utf-8')
        hash_b_arr = base64.b64decode(hash_b64)
        hash_tuple = tuple(list(hash_b_arr))

        return hash_tuple

# -----------------------------------------------------------------------------
    def random_bit_string(self, length):
        list = []
        for x in range(0, length):
            list.append(random.randrange(256))
        return tuple(list)

# -----------------------------------------------------------------------------
    def generate_sessioniv(self):
        return self.random_bit_string(12)

# -----------------------------------------------------------------------------
    def generate_encrypted_session_key(self, session_key, worker_encryption_key):
        session_key = encryptionAlg.encAlgorithm()
        return self.encrypt_data(worker_encryption_key.encode(), session_key.generateKey(), session_iv)

# -----------------------------------------------------------------------------

    def compute_message_hash(self, message):
        byte_arr = bytes(message)

        hash_obj = SHA256.new()
        hash_obj.update(byte_arr)
        hash_tuple = tuple(list(hash_obj.digest()))

        return hash_tuple

    def generate_key(self):
        return self.random_bit_string(16)

    def generate_encrypted_key(self, session_key, encryption_key):

        key = RSA.importKey(encryption_key)
        cipher = PKCS1_OAEP.new(key, label='')
        ciphered_data = cipher.encrypt(bytes(list(session_key)))

        ciphered_data_list = list(ciphered_data)

        return tuple(ciphered_data_list)
