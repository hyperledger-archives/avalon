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

from utility.hex_utils import is_valid_hex_str
import base64


class WorkOrderRequestValidator():
    """
    WorkOrderRequestValidator - validates work order request
    for proper params fields and valid data formats
    """
    def __init__(self):
        """
        key value pair with field name and boolean indicator that tells
        whether field is mandatory or not.
        True is mandatory and False is optional.
        """
        self.__param_key_map = {
            "responseTimeoutMSecs": True,
            "payloadFormat": False,
            "resultUri": False,
            "notifyUri": False,
            "workOrderId": True,
            "workerId": True,
            "workloadId": True,
            "requesterId": True,
            "workerEncryptionKey": False,
            "dataEncryptionAlgorithm": False,
            "encryptedSessionKey": True,
            "sessionKeyIv": False,
            "requesterNonce": True,
            "encryptedRequestHash": True,
            "requesterSignature": False,
            "verifyingKey": False,
            "inData": True,
            "outData": False}
        self.__data_key_map = {
            "index": True,
            "dataHash": False,
            "data": True,
            "encryptedDataEncryptionKey": False,
            "iv": False}

    def validate_parameters(self, params):
        """
        Validate parameter dictionary for existence of
        fields and mandatory fields
        Returns False and string with error message on failure and
        True and empty string on success
        """
        key_list = []
        for key in params.keys():
            if key not in self.__param_key_map.keys():
                return False, "Invalid parameter {}".format(key)
            else:
                key_list.append(key)
        for k, v in self.__param_key_map.items():
            if v is True and k not in key_list:
                return False, "Missing parameter {}".format(k)

        if not is_valid_hex_str(params["workerId"]):
            return False, "Invalid data format for Worker id"
        if not is_valid_hex_str(params["workOrderId"]):
            return False, "Invalid data format for work order id"
        if not is_valid_hex_str(params["workloadId"]):
            return False, "Invalid data format for work load id"
        if not is_valid_hex_str(params["requesterId"]):
            return False, "Invalid data format for requester id"
        if "workerEncryptionKey" in params and \
                not is_valid_hex_str(params["workerEncryptionKey"]):
            return False, "Invalid data format for worker encryption key"
        if "encryptedSessionKey" in params and \
                not is_valid_hex_str(params["encryptedSessionKey"]):
            return False, "Invalid data format for encrypted session key"
        if "sessionKeyIv" in params and \
                not is_valid_hex_str(params["sessionKeyIv"]):
            return False, "Invalid data format for session key iv"
        if "encryptedRequestHash" in params and \
                not is_valid_hex_str(params["encryptedRequestHash"]):
            return False, "Invalid data format for encrypted request hash"
        return True, ""

    def validate_data_format(self, data):
        """
        Validate data format of the params data field (in data or out data)
        Returns False and string with error message on failure and
        True and empty string on success
        """
        for data_item in data:
            in_data_keys = []
            for key in data_item.keys():
                if key not in self.__data_key_map.keys():
                    return False, "Invalid in data parameter {}".format(key)
                else:
                    in_data_keys.append(key)
            for k, v in self.__data_key_map.items():
                if v is True and k not in in_data_keys:
                    return False, "Missing in data parameter {}".format(k)

            if "dataHash" in data_item:
                data_hash = data_item["dataHash"]
                if not is_valid_hex_str(data_hash):
                    return False, \
                        "Invalid data format for data hash of in data"
            if "encryptedDataEncryptionKey" in data_item:
                enc_key = data_item["encryptedDataEncryptionKey"]
                if enc_key != "-" and \
                        enc_key != "" and \
                        enc_key != "null" and \
                        not is_valid_hex_str(enc_key):
                    return False, \
                        "Invalid data format for Encryption key of in data"
            if "iv" in data_item and data_item["iv"] != "" and \
                    data_item["iv"] != "0" and \
                    not is_valid_hex_str(data_item["iv"]):
                return False, \
                    "Invalid data format for initialization vector of in data"
            try:
                base64.b64decode(data_item["data"])
            except Exception as e:
                return False, \
                    "Invalid data format for in data"

        return True, ""
