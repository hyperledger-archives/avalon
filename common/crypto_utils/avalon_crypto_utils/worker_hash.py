#!/usr/bin/python3

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
import sys
import logging
from Cryptodome.Hash import SHA256


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# -------------------------------------------------------------------------


class WorkerHash():
    """
    Worker Request and Response Hash calculation class.
    """

# -------------------------------------------------------------------------

    def calculate_request_hash(self, wo_request_params):
        """
        Function to create the work order request hash
        as defined in EEA spec v1.1 section 6.6.1.

        Parameters:
            wo_request_params: dictionary containing work order request
                               payload params as defined in EEA spec v1.1
                               section 6.1.
        Returns hash of work order request as bytes.
        """
        concat_string = wo_request_params["requesterNonce"] + \
            wo_request_params["workOrderId"] + \
            wo_request_params["workerId"] + \
            wo_request_params["workloadId"] + \
            wo_request_params["requesterId"]
        concat_bytes = concat_string.encode("UTF-8")
        # SHA-256 hashing is used
        hash_1 = self.compute_message_hash(concat_bytes)
        hash_2 = self.calculate_datahash(wo_request_params["inData"])
        hash_3 = bytearray()
        if "outData" in wo_request_params and \
                len(wo_request_params["outData"]) > 0:
            hash_3 = self.calculate_datahash(wo_request_params["outData"])
        concat_hashes = hash_1 + hash_2 + hash_3
        final_hash = self.compute_message_hash(concat_hashes)
        return final_hash

# -------------------------------------------------------------------------

    def calculate_response_hash(self, wo_response):
        """
        Function to create the work order response hash
        as defined in EEA spec 6.6.2.

        Parameters:
            wo_response: dictionary containing work order result payload
                         as define EEA spec v1.1 section 6.1
        Returns hash of work order response as bytes.
        """
        concat_string = wo_response["workerNonce"] + \
            wo_response["workOrderId"] + \
            wo_response["workerId"] + \
            wo_response["workloadId"] + \
            wo_response["requesterId"]
        concat_bytes = concat_string.encode("UTF-8")
        # SHA-256 hashing is used
        hash_1 = self.compute_message_hash(concat_bytes)
        hash_2 = ""
        # Compute outData hash
        if "outData" in wo_response and \
                len(wo_response["outData"]) > 0:
            hash_2 = self.calculate_datahash(wo_response["outData"])
        # Concatenate hash and compute final hash
        concat_hashes = hash_1 + hash_2
        final_hash = self.compute_message_hash(concat_hashes)
        return final_hash

# -------------------------------------------------------------------------

    def calculate_datahash(self, data_objects):
        """
        Function to calculate a hash value of the array concatenating dataHash,
        data, encryptedDataEncryptionKey, iv for each item in the
        inData/outData array.

        Parameters:
            data_objects: inData/outData elements within the
                          work order request as per Trusted Compute
                          EEA API 6.1.7 Work Order Data Formats.
        Returns data hash of iData/outData.
        """
        hash_str = ""
        # Sort the data items based on index field before calculating
        # data hash.
        data_objects.sort(key=lambda x: x['index'])
        for item in data_objects:
            datahash = ""
            e_key = ""
            iv = ""
            data = ""
            if 'dataHash' in item:
                datahash = item['dataHash']
            if 'data' in item:
                data = item['data']
            if 'encryptedDataEncryptionKey' in item:
                e_key = item['encryptedDataEncryptionKey']
            if 'iv' in item:
                iv = item['iv']
            concat_string = datahash + data + e_key + iv
            hash_str = hash_str + concat_string

        result_hash = self.compute_message_hash(hash_str.encode("UTF-8"))
        return result_hash

# -------------------------------------------------------------------------

    def compute_message_hash(self, message_bytes):
        """
        Computes SHA256 message hash.

        Parameters :
            message_bytes: Message in bytes
        Returns :
            SHA256 message hash.
        """
        hash_obj = SHA256.new()
        hash_obj.update(message_bytes)
        return hash_obj.digest()

# -------------------------------------------------------------------------

    def verify_data_hash(self, msg, data_hash):
        '''
        Function to verify data hash
        Parameters:
            msg - Input text
            data_hash - hash of the data in hex format
        Returns:
            verify_success: Boolean value, status of data hash verification
        '''
        verify_success = True
        msg_hash = self.compute_message_hash(msg)
        # Convert both hash hex string values to upper case
        msg_hash_hex = hex_utils.byte_array_to_hex_str(msg_hash).upper()
        data_hash = data_hash.upper()
        if msg_hash_hex == data_hash:
            logger.info("Computed hash of message matched with data hash")
        else:
            logger.error(
                "Computed hash of message does not match with data hash")
            verify_success = False
        return verify_success
