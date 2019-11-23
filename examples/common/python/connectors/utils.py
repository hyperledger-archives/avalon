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

import logging
import json
from utility.hex_utils import is_valid_hex_str

from utility.tcf_types import JsonRpcErrorCode

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


def create_jrpc_response(id, code, message, data=None):
    """
    Create the json rpc response object
    """
    if not isinstance(code, JsonRpcErrorCode):
        logging.error("Invalid code type")
    response_obj = {
        "jsonrpc": "2.0",
        "id": id,
        "error": {
            "code": code.value,
            "message": message,
            "data": data
        }
    }
    return response_obj


def validate_details(details):
    """
    Validate the details filed of worker
    """
    details_dict = json.loads(details)
    worker_details_fields = [
                             "workOrderSyncUri",
                             "workOrderAsyncUri",
                             "workOrderPullUri",
                             "workOrderNotifyUri",
                             "receiptInvocationUri",
                             "workOrderInvocationAddress",
                             "receiptInvocationAddress",
                             "fromAddress",
                             "hashingAlgorithm",
                             "signingAlgorithm",
                             "keyEncryptionAlgorithm",
                             "dataEncryptionAlgorithm",
                             "workOrderPayloadFormats",
                             "workerTypeData"
                            ]
    worker_type_fields = [
                          "verificationKey",
                          "extendedMeasurements",
                          "proofDataType",
                          "proofData",
                          "encryptionKey",
                          "encryptionKeyNonce",
                          "encryptionKeySignature",
                          "enclaveCertificate"
                         ]
    for key in details_dict:
        if key not in worker_details_fields:
            return "Invalid argument {}".format(key)

    if "workerTypeData" in details_dict:
        for key in details_dict['workerTypeData']:
            if key not in worker_type_fields:
                return "Invalid argument {}".format(key)

    if ("workOrderSyncUri" in details_dict.keys() and
            not is_valid_hex_str(details_dict['workOrderSyncUri'])):
        return "Invalid argument workOrderSyncUri"

    if ("workOrderAsyncUri" in details_dict.keys() and
            not is_valid_hex_str(details_dict['workOrderAsyncUri'])):
        return "Invalid argument workOrderAsyncUri"

    if ("workOrderPullUri" in details_dict.keys() and
            not is_valid_hex_str(details_dict['workOrderPullUri'])):
        return "Invalid argument workOrderPullUri"

    if ("workOrderNotifyUri" in details_dict.keys() and
            not is_valid_hex_str(details_dict['workOrderNotifyUri'])):
        return "Invalid argument workOrderNotifyUri"

    if ("receiptInvocationUri" in details_dict.keys() and
            not is_valid_hex_str(details_dict['receiptInvocationUri'])):
        return "Invalid argument receiptInvocationUri"

    if ("workOrderInvocationAddress" in details_dict.keys() and
            not is_valid_hex_str(details_dict['workOrderInvocationAddress'])):
        return "Invalid argument workOrderInvocationAddress"

    if ("receiptInvocationAddress" in details_dict.keys() and
            not is_valid_hex_str(details_dict['receiptInvocationAddress'])):
        return "Invalid argument receiptInvocationAddress"

    if ("fromAddress" in details_dict.keys() and
            not is_valid_hex_str(details_dict['fromAddress'])):
        return "Invalid argument fromAddress"

    if ("workOrderPayloadFormats" in details_dict.keys() and
            not is_valid_hex_str(details_dict['workOrderPayloadFormats'])):
        return "Invalid argument workOrderPayloadFormats"

    if ("workerTypeData" in details_dict.keys()):
        if ("verificationKey" in details_dict["workerTypeData"].keys() and
                not is_valid_hex_str(
                details_dict["workerTypeData"]["verificationKey"])):
            return "Invalid argument verificationKey"

        if ("proofDataType" in details_dict["workerTypeData"].keys() and
                not is_valid_hex_str(
                details_dict["workerTypeData"]["proofDataType"])):
            return "Invalid argument proofDataType"

        if ("encryptionKey" in details_dict["workerTypeData"].keys() and
                not is_valid_hex_str(
                details_dict["workerTypeData"]["encryptionKey"])):
            return "Invalid argument encryptionKey"

        if ("encryptionKeyNonce" in details_dict["workerTypeData"].keys() and
                not is_valid_hex_str(
                details_dict["workerTypeData"]["encryptionKeyNonce"])):
            return "Invalid argument encryptionKeyNonce"

        if ("encryptionKeySignature" in details_dict["workerTypeData"].keys()
                and not is_valid_hex_str(
                details_dict["workerTypeData"]["encryptionKeySignature"])):
            return "Invalid argument encryptionKeySignature"

        if ("enclaveCertificate" in details_dict["workerTypeData"].keys() and
                not is_valid_hex_str(
                details_dict["workerTypeData"]["enclaveCertificate"])):
            return "Invalid argument enclaveCertificate"
    return None


def construct_message(status, message):
    """
    Construct a json object with status and message.
    """
    return {
        "status": status,
        "message": message
    }
