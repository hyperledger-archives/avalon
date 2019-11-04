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
import random

import crypto.crypto as crypto
from automation_framework.utilities.tamper_utility import tamper_request
from error_code.error_status import SignatureStatus
import worker.worker_details as worker

logger = logging.getLogger(__name__)
NO_OF_BYTES = 16

class WorkOrderSubmit():
    def __init__(self):
        self.id_obj = {"jsonrpc": "2.0", "method": "WorkOrderSubmit", "id": 3}
        self.params_obj = {}
        self.session_key = self.generate_key()
        self.session_iv = self.generate_iv()

    def add_json_values(self, input_json_temp, worker_obj, private_key, tamper):

        self.private_key = private_key
        self.worker_obj = worker_obj

        input_params_list = input_json_temp["params"].keys()
        if "responseTimeoutMSecs" in input_params_list :
            if input_json_temp["params"]["responseTimeoutMSecs"] != "" :
                self.set_response_timeout_msecs(
                input_json_temp["params"]["responseTimeoutMSecs"])
            else :
                self.set_response_timeout_msecs(6000)

        if "payloadFormat" in input_params_list :
            if input_json_temp["params"]["payloadFormat"] != "" :
                self.set_payload_format(
                input_json_temp["params"]["payloadFormat"])
            else :
                self.set_payload_format("JSON-RPC")

        if "resultUri" in input_params_list :
            if input_json_temp["params"]["resultUri"] != "" :
                self.set_result_uri(input_json_temp["params"]["resultUri"])
            else :
                self.set_result_uri("")

        if "notifyUri" in input_params_list :
            if input_json_temp["params"]["notifyUri"] != "" :
                self.set_notify_uri(input_json_temp["params"]["notifyUri"])
            else :
                self.set_notify_uri("")

        if "workOrderId" in input_params_list :
            if input_json_temp["params"]["workOrderId"] != "" :
                self.set_work_order_id(input_json_temp["params"]["workOrderId"])
            else :
                work_order_id = hex(random.randint(1, 2**64 -1))
                self.set_work_order_id(work_order_id)

        if "workerId" in input_params_list :
            if input_json_temp["params"]["workerId"] != "" :
                self.set_worker_id(input_json_temp["params"]["workerId"])
            else :
                self.set_worker_id(worker_obj.worker_id)

        if "workloadId" in input_params_list :
            if input_json_temp["params"]["workloadId"] != "" :
                self.set_workload_id(
                input_json_temp["params"]["workloadId"].encode('UTF-8').hex())
            else :
                workload_id = "echo-client"
                self.set_workload_id(workload_id.encode('UTF-8').hex())

        if "requesterId" in input_params_list :
            if input_json_temp["params"]["requesterId"] != "" :
                self.set_requester_id(input_json_temp["params"]["requesterId"])
            else :
                self.set_requester_id("0x3456")

        if "workerEncryptionKey" in input_params_list :
            if input_json_temp["params"]["workerEncryptionKey"] != "" :
                self.set_worker_encryption_key(
                input_json_temp["params"]["workerEncryptionKey"].encode(
                    "UTF-8").hex())
            else :
                self.set_worker_encryption_key(self.strip_rsa_begin_end_key(
                worker_obj.encryption_key).encode("UTF-8").hex())

        if "dataEncryptionAlgorithm" in input_params_list :
            if input_json_temp["params"]["dataEncryptionAlgorithm"] != "" :
                self.set_data_encryption_algorithm(
                input_json_temp["params"]["dataEncryptionAlgorithm"])
            else :
                self.set_data_encryption_algorithm("AES-GCM-256")

        if "sessionKeyIv" in input_params_list :
            if input_json_temp["params"]["sessionKeyIv"] != "" :
                self.set_session_key_iv(
                     input_json_temp["params"]["sessionKeyIv"])
            else :
                self.set_session_key_iv(self.byte_array_to_hex_str(
                     self.session_iv))

        if "encryptedSessionKey" in input_params_list :
            if input_json_temp["params"]["encryptedSessionKey"] != "" :
                self.set_encrypted_session_key(
                     input_json_temp["params"]["encryptedSessionKey"])
                self.encrypted_session_key = (
                     input_json_temp["params"]["encryptedSessionKey"])
            else :
                self.encrypted_session_key = (
                     self.generate_encrypted_key (self.session_key,
                                    worker_obj.encryption_key))
                self.set_encrypted_session_key(self.byte_array_to_hex_str(
                                               self.encrypted_session_key))

        if "requesterNonce" in input_params_list :
            if input_json_temp["params"]["requesterNonce"] != "" :
                self.nonce = crypto.string_to_byte_array(
                             input_json_temp["params"]["requesterNonce"])
                self.nonce_hash = (crypto.byte_array_to_base64(
                                  crypto.compute_message_hash(
                                  self.nonce))).encode('UTF-8')
                self.set_requester_nonce(crypto.byte_array_to_base64(
                                  crypto.compute_message_hash(
                                  self.nonce)))
            else :
                self.nonce = crypto.random_bit_string(NO_OF_BYTES)
                self.nonce_hash = (crypto.byte_array_to_base64(
                                  crypto.compute_message_hash(
                                  self.nonce))).encode('UTF-8')
                self.set_requester_nonce(crypto.byte_array_to_base64(
                                  crypto.compute_message_hash(
                                  self.nonce)))

        if "inData" in input_params_list :
            if input_json_temp["params"]["inData"] != "" :
                input_json_inData = input_json_temp["params"]["inData"]
                self.add_in_data(input_json_inData)
            else :
                self.params_obj["inData"] = ""

        if "outData" in input_params_list :
            if input_json_temp["params"]["outData"] != "" :
                input_json_outData = input_json_temp["params"]["outData"]
                self.add_out_data(input_json_outData)
            else :
                self.params_obj["outData"] = ""

        if "encryptedRequestHash" in input_params_list :
            if input_json_temp["params"]["encryptedRequestHash"] != "" :
                self.params_obj["encryptedRequestHash"] = \
                     input_json_temp["params"]["encryptedRequestHash"]
            else :
                self._compute_encrypted_request_hash()

        if "requesterSignature" in input_params_list :
            if input_json_temp["params"]["requesterSignature"] != "" :
                self.params_obj["requesterSignature"] = \
                     input_json_temp["params"]["requesterSignature"]
            else :
                self.params_obj["requesterSignature"] = ""

        if "verifyingKey" in input_params_list :
            if input_json_temp["params"]["verifyingKey"] != "" :
                self.params_obj["verifyingKey"] = \
                     input_json_temp["params"]["verifyingKey"]

        if "default" in tamper.keys():
            if "params" in tamper["default"].keys():
                for key, value in tamper["default"]["params"] :
                    param = key
                    value = value
            self.set_unknown_parameter(param, value)

    def set_unknown_parameter(self, param, value):
        self.params_obj[param] = value

    def _compute_encrypted_request_hash(self) :
        first_string = self.nonce_hash
        worker_order_id = self.get_work_order_id()
        if worker_order_id is not None:
            first_string = first_string + worker_order_id.encode('UTF-8')
            logger.info("first_string - %s", first_string)
        else :
            first_string = first_string + "".encode('UTF-8')

        worker_id = self.get_worker_id()
        if worker_id is not None:
            first_string = first_string + worker_id.encode('UTF-8')
        else :
            first_string = first_string + "".encode('UTF-8')

        workload_id = self.get_workload_id()
        if workload_id is not None:
            first_string = first_string + workload_id.encode('UTF-8')
        else :
            first_string = first_string + "".encode('UTF-8')

        requester_id = self.get_requester_id()
        if requester_id is not None:
            first_string = first_string + requester_id.encode('UTF-8')
        else :
            first_string = first_string + "".encode('UTF-8')

        concat_hash =  bytes(first_string)
        self.hash_1 = crypto.byte_array_to_base64(
                      crypto.compute_message_hash(concat_hash))

        in_data = self.get_in_data()
        out_data = self.get_out_data()

        self.hash_2 = ""
        if in_data is not None:
            self.hash_2 = self._compute_hash_string(in_data)

        self.hash_3 = ""
        if out_data is not None:
            self.hash_3 = self._compute_hash_string(out_data)

        final_string = self.hash_1 + self.hash_2 + self.hash_3
        self.final_hash = crypto.compute_message_hash(
                          bytes(final_string, 'UTF-8'))

        self.encrypted_request_hash = self.byte_array_to_hex_str(
                                      self.encrypt_data(
                                      self.final_hash, self.session_key,
                                      self.session_iv))

        self.params_obj["encryptedRequestHash"] = self.encrypted_request_hash

    def _compute_hash_string(self, data):
        final_hash_str = ""
        hash_string = ""
        for data_item in data :
            data = "".encode('UTF-8')
            datahash = "".encode('UTF-8')
            e_key = "".encode('UTF-8')
            iv = "".encode('UTF-8')
            if 'dataHash' in data_item:
                datahash = data_item['dataHash'].encode('UTF-8')
            if 'data' in data_item:
                data = data_item['data'].encode('UTF-8')
            if 'encryptedDataEncryptionKey' in data_item:
                e_key = \
                data_item['encryptedDataEncryptionKey'].encode('UTF-8')
            if 'iv' in data_item:
                iv = data_item['iv'].encode('UTF-8')
            hash_string =  datahash + data + e_key + iv
            complete_bytes = bytes(hash_string)
            hash = crypto.compute_message_hash(complete_bytes)
            final_hash_str = final_hash_str + crypto.byte_array_to_base64(hash)
        return final_hash_str

    def _compute_requester_signature(self):
        self.public_key =  self.private_key.GetPublicKey().Serialize()
        signature_result =  self.private_key.SignMessage(self.final_hash)
        self.requester_signature  =  crypto.byte_array_to_base64(
                                     signature_result)
        self.params_obj["requesterSignature"] = self.requester_signature
        self.params_obj["verifyingKey"] = self.public_key

    def byte_array_to_hex_str(self, in_byte_array):
        '''
        Converts tuple of bytes to hex string
        '''
        logger.debug("Input Byte Array: %s", in_byte_array)
        hex_str = ''.join(format(i, '02x') for i in in_byte_array)
        logger.debug("Output Byte Array to str: %s", hex_str)
        return hex_str

    def strip_begin_end_key(self, key) :
        """
        Strips off newline chars, BEGIN PUBLIC KEY and END PUBLIC KEY.
        """
        return key.replace("\n", "").replace(
               "-----BEGIN PUBLIC KEY-----", "").replace(
               "-----END PUBLIC KEY-----", "")

    def strip_rsa_begin_end_key(self, key) :
        """
        Strips off newline chars, BEGIN PUBLIC KEY and END PUBLIC KEY.
        """
        return key.replace("\n", "").replace(
               "-----BEGIN RSA PUBLIC KEY-----", "").replace(
               "-----END RSA PUBLIC KEY-----", "")

    def generate_key(self):
        """
        Function to generate symmetric key
        """
        return crypto.SKENC_GenerateKey()

    def generate_iv(self):
        """
        Function to generate random initialization vector
        """
        return crypto.SKENC_GenerateIV()

    def generate_encrypted_key(self, key, encryption_key):
        """
        Function to generate session key for the client
        Parameters:
        - encryption_key is a one-time encryption used to encrypt the passed key
        - key that needs to be encrypted
        """
        pub_enc_key = crypto.PKENC_PublicKey(encryption_key)
        return pub_enc_key.EncryptMessage(key)

    def set_response_timeout_msecs(self, response_timeout_msecs):
        self.params_obj["responseTimeoutMSecs"] = \
                response_timeout_msecs

    def set_payload_format(self, payload_format):
        self.params_obj["payloadFormat"] = payload_format

    def set_result_uri(self, result_uri):
        self.params_obj["resultUri"] = result_uri

    def set_notify_uri(self, notify_uri):
        self.params_obj["notifyUri"] = notify_uri

    def set_worker_id(self, worker_id):
        self.params_obj["workerId"] = worker_id

    def set_work_order_id(self, work_order_id):
        self.params_obj["workOrderId"] = work_order_id

    def set_workload_id(self, workload_id):
        self.params_obj["workloadId"] = workload_id

    def set_requester_id(self, requester_id):
        self.params_obj["requesterId"] = requester_id

    def set_worker_encryption_key(self, worker_encryption_key):
        self.params_obj["workerEncryptionKey"] = worker_encryption_key

    def set_data_encryption_algorithm(self, data_encryption_algorithm):
        self.params_obj["dataEncryptionAlgorithm"] = \
                data_encryption_algorithm

    def set_encrypted_session_key(self, encrypted_session_key):
        self.params_obj["encryptedSessionKey"] = encrypted_session_key

    def set_session_key_iv(self, session_iv):
        self.params_obj["sessionKeyIv"] = session_iv

    def set_requester_nonce(self, requester_nonce):
        self.params_obj["requesterNonce"] = requester_nonce

    def add_encrypted_request_hash(self, encrypted_request_hash):
        self.params_obj["encryptedRequestHash"] = encrypted_request_hash

    def add_requester_signature(self, requester_signature):
        self.params_obj["requesterSignature"] = requester_signature

    def set_verifying_key(self, verifying_key):
        self.params_obj["verifyingKey"] = verifying_key

    def add_in_data(self, input_json_inData):
        if not "inData" in self.params_obj:
            self.params_obj["inData"] = []

        try :
            input_json_inData.sort(key=lambda x: x['index'])
        except :
            logger.debug("Sorting Indata based on Index failed \n")

        for inData_item in input_json_inData :
            in_data_copy = self.params_obj["inData"]
            mod_data_copy = self._add_data_item(in_data_copy, inData_item)
            if mod_data_copy is not None :
                self.params_obj["inData"] = mod_data_copy
            else :
                in_data_copy = self.params_obj["inData"]
                in_data_copy.append(inData_item)
                self.params_obj["inData"] = in_data_copy

    def add_out_data(self, input_json_outData):
        if not "outData" in self.params_obj:
                self.params_obj["outData"] = []

        for outData_item in input_json_outData :
            out_data_copy = self.params_obj["outData"]
            mod_data_copy = self._add_data_item(out_data_copy, outData_item)
            if mod_data_copy is not None :
                self.params_obj["outData"] = mod_data_copy
            else :
                out_data_copy = self.params_obj["outData"]
                out_data_copy.append(outData_item)
                self.params_obj["outData"] = out_data_copy

    def _add_data_item (self, data_copy, data_item):

        try :
            index = data_item['index']
            data = data_item['data'].encode('UTF-8')
            if 'encryptedDataEncryptionKey' in data_item :
                e_key = data_item['encryptedDataEncryptionKey'].encode(
                                                                  'UTF-8')
            else :
                e_key = "null".encode('UTF-8')
            if (not e_key ) or (e_key == "null".encode('UTF-8')):
                enc_data = self.encrypt_data(data, self.session_key,
                           self.session_iv)
                base64_enc_data = (crypto.byte_array_to_base64(enc_data))
                if 'dataHash' in data_item :
                    dataHash_enc_data = (self.byte_array_to_hex_str(
                       crypto.compute_message_hash(data)))
                logger.debug("encrypted indata - %s",
                       crypto.byte_array_to_base64(enc_data))
            elif e_key == "-".encode('UTF-8'):
                # Skip encryption and just encode workorder data
                # to base64 format
                base64_enc_data = (crypto.byte_array_to_base64(data))
                if 'dataHash' in data_item :
                    dataHash_enc_data = (self.byte_array_to_hex_str(
                       crypto.compute_message_hash(data)))
            else:
                data_key = None
                data_iv = None
                enc_data = self.encrypt_data(data, data_key, data_iv)
                base64_enc_data = (crypto.byte_array_to_base64(enc_data))
                if 'dataHash' in data_item :
                    dataHash_enc_data = (self.byte_array_to_hex_str(
                       crypto.compute_message_hash(data)))
                logger.debug("encrypted indata - %s",
                       crypto.byte_array_to_base64(enc_data))

            enc_indata_item = {'index': index,
                               'dataHash': dataHash_enc_data,
                               'data': base64_enc_data,
                               'encryptedDataEncryptionKey' : \
                               data_item['encryptedDataEncryptionKey'],
                               'iv' : data_item['iv']}
            data_copy.append(enc_indata_item)

            return data_copy
        except :
            return None

    def encrypt_data(self, data, encryption_key, iv):
        """
        Function to encrypt data based on encryption key and iv
        Parameters:
            - data is each item in inData or outData part of workorder request
              as per TCF API 6.1.7 Work Order Data Formats
            - encryption_key is the key used to encrypt the data
            - iv is an initialization vector if required by the data encryption algorithm.
              The default is all zeros.iv must be a unique random number for every
              encryption operation.
        """
        logger.debug("encrypted_session_key: %s", encryption_key)
        if iv is not None:
            encrypted_data = crypto.SKENC_EncryptMessage(encryption_key, iv, data)
        else:
            encrypted_data = crypto.SKENC_EncryptMessage(encryption_key, 0,  data)
        return encrypted_data

    def get_verifying_key(self):
        if "verifyingKey" in self.params_obj:
            return self.params_obj["verifyingKey"]
        else :
            return None

    def get_params(self):
        params_copy = self.params_obj.copy()
        if "inData" in params_copy:
            params_copy.pop("inData")
        if "outData" in params_copy:
            params_copy.pop("outData")
        return params_copy

    def get_in_data(self):
        if "inData" in self.params_obj:
            return self.params_obj["inData"]
        else :
            return None

    def get_out_data(self):
        if "outData" in self.params_obj:
            return self.params_obj["outData"]
        else :
            return None

    def get_requester_nonce(self):
        return self.params_obj["requesterNonce"]

    def get_worker_id(self):
        if "workerId" in self.params_obj:
            return self.params_obj["workerId"]
        else :
            return None

    def get_workload_id(self):
        if "workloadId" in self.params_obj:
            return self.params_obj["workloadId"]
        else :
            return None

    def get_requester_id(self):
        if "requesterId" in self.params_obj:
            return self.params_obj["requesterId"]
        else :
            return None

    def get_session_key_iv(self):
        return self.params_obj["sessionKeyIv"]

    def get_work_order_id(self):
        if "workOrderId" in self.params_obj:
            return self.params_obj["workOrderId"]
        else :
            return None

    def get_encrypted_session_key(self):
        return self.params_obj["encryptedSessionKey"]

    def get_encrypted_request_hash(self):
        if "encryptedRequestHash" in self.params_obj:
            return self.params_obj["encryptedRequestHash"]
        else :
            return None

    def get_requester_signature(self):
        if "requesterSignature" in self.params_obj:
            return self.params_obj["requesterSignature"]
        else :
            return None

    def verify_signature(self, input_json, verification_key):
        """
        Function to verify the signature received from the enclave
        Parameters:
            - input_json is dictionary contains payload returned by the
              Worker Service in response to successful workorder submit request
              as per TCF API 6.1.2 Work Order Result Payload
            - verification_key is ECDSA/SECP256K1 public key used to verify signatures
              created by the Enclave
        Returns enum type SignatureStatus
        """

        input_json_params = input_json['result']

        nonce = (input_json_params['workerNonce']).encode('UTF-8')
        signature = input_json_params['workerSignature']

        hash_string_1 = ""

        workorder_id = (input_json_params['workOrderId']).encode('UTF-8')
        worker_id = (input_json_params['workerId']).encode('UTF-8')
        workload_id = (input_json_params['workloadId']).encode('UTF-8')
        requester_id = (input_json_params['requesterId']).encode('UTF-8')

        concat_string = nonce + workorder_id + worker_id + workload_id + requester_id
        concat_hash =  bytes(concat_string)
        #SHA-256 hashing is used
        hash_1 = crypto.compute_message_hash(concat_hash)
        hash_string_1 = crypto.byte_array_to_base64(hash_1)

        data_objects = input_json_params['outData']
        data_objects.sort(key = lambda x:x['index'])
        hash_string_2 = ""

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
            concat_string =  datahash + data + e_key + iv
            concat_hash = bytes(concat_string)
            hash = crypto.compute_message_hash(concat_hash)
            hash_str = hash_str + crypto.byte_array_to_base64(hash)

        hash_string_2 = hash_str

        concat_string =  hash_string_1+ hash_string_2
        concat_hash = bytes(concat_string, 'UTF-8')
        final_hash = crypto.compute_message_hash(concat_hash)

        try:
            _verifying_key = crypto.SIG_PublicKey(verification_key)
        except Exception as error:
            logger.info("Error in verification key : %s", error)
            return SignatureStatus.INVALID_VERIFICATION_KEY

        decoded_signature = crypto.base64_to_byte_array(signature)
        sig_result =_verifying_key.VerifySignature(final_hash, decoded_signature)

        if sig_result == 1:
            return SignatureStatus.PASSED
        elif sig_result == 0:
            return SignatureStatus.FAILED
        else:
            return SignatureStatus.INVALID_SIGNATURE_FORMAT

    def compute_signature(self, tamper):

        self._compute_requester_signature()

        json_rpc_request = self.id_obj
        json_rpc_request["params"] = self.get_params()

        input_after_sign = self.to_string()
        tamper_instance = 'after_sign'
        tampered_request = tamper_request(input_after_sign, tamper_instance,
                                          tamper)
        return tampered_request

    def to_string(self):
        json_rpc_request = self.id_obj
        json_rpc_request["params"] = self.get_params()

        in_data = self.get_in_data()
        out_data = self.get_out_data()

        if in_data is not None:
            json_rpc_request["params"]["inData"] = in_data

        if out_data is not None:
            json_rpc_request["params"]["outData"] = out_data

        return json.dumps(json_rpc_request, indent=4)
