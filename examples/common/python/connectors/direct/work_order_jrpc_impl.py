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
import time
import logging
from eth_utils.hexadecimal import is_hex
import base64
from service_client.generic import GenericServiceClient
from connectors.interfaces.work_order_interface import WorkOrderInterface
from connectors.utils import create_jrpc_response
from utility.tcf_types import JsonRpcErrorCode
from error_code.error_status import WorkOrderStatus

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

class WorkOrderJRPCImpl(WorkOrderInterface):
    def __init__(self, config):
        self.__uri_client = GenericServiceClient(config["tcf"]["json_rpc_uri"])

        """
        key value pair with field name and boolean indicator that tells 
        whether field is mandatory or not. True is mandatory and False is optional
        """
        self.__param_key_map = {
            "responseTimeoutMSecs":True,
            "payloadFormat":False,
            "resultUri":False,
            "notifyUri":False,
            "workOrderId":True,
            "workerId":True,
            "workloadId":True,
            "requesterId":True,
            "workerEncryptionKey":False,
            "dataEncryptionAlgorithm":False,
            "encryptedSessionKey":True,
            "sessionKeyIv":False,
            "requesterNonce":True,
            "encryptedRequestHash":True,
            "requesterSignature":False,
            "verifyingKey":True
            }
        self.__data_key_map = {
            "index":True,
            "dataHash":False,
            "data":True,
            "encryptedDataEncryptionKey":False,
            "iv":False
            }
    
    def __validate_parameters(self, params):
        """
        Validate parameter dictionary for existence of 
        fields and mandatory fields 
        Returns False and string with error message on failure and 
        True and empty string on success
        """
        key_list = []
        for key in params.keys():
            if not key in self.__param_key_map.keys():
                logging.error("Invalid parameter %s",key)
                return False, "Invalid parameter {}".format(key)
            else:
                key_list.append(key)
        for k, v in self.__param_key_map.items():
            if v == True and not k in key_list:
                logging.error("Missing parameter %s", k)
                return False, "Missing parameter {}".format(k)

        if not is_hex(params["workOrderId"]):
            logging.error("Invalid work order id")
            return False, "Invalid work order id"
        if not is_hex(params["workloadId"]):
            logging.error("Invalid work load id")
            return False, "Invalid work load id"
        if not is_hex(params["requesterId"]):
            logging.error("Invalid requester id id")
            return False, "Invalid requester id id"
        if not is_hex(params["workerEncryptionKey"]):
            logging.error("Invalid worker encryption key")
            return False, "Invalid worker encryption key"

        return True, ""
    
    def __validate_data_format(self, data):
        """
        Validate data format of the params data field (in data or out data)
        Returns False and string with error message on failure and 
        True and empty string on success
        """
        for data_item in data:
            in_data_keys = []
            for key in data_item.keys():
                if not key in self.__data_key_map.keys():
                    logging.error("Invalid in data parameter %s",key)
                    return False, "Invalid in data parameter {}".format(key)
                else:
                    in_data_keys.append(key)
            for k, v in self.__data_key_map.items():
                if v == True and not k in in_data_keys:
                    logging.error("Missing in data parameter %s", k)
                    return False, "Missing in data parameter {}".format(k)

            if "dataHash" in data_item:
                data_hash = data_item["dataHash"]
                if not is_hex(data_hash) and data_hash != "":
                    logging.error("Invalid data hash of in data")
                    return False, "Invalid data hash of in data"
            if "encryptedDataEncryptionKey" in data_item:
                enc_key = data_item["encryptedDataEncryptionKey"]
                if enc_key != "-" and \
                    enc_key != "" and \
                    enc_key != "null" and \
                    not is_hex(enc_key):
                    logging.error("Invalid Encryption key of in data")
                    return False, \
                        "Invalid Encryption key of in data"
            if "iv" in data_item and data_item["iv"] != "" and \
                data_item["iv"] != "0" and not is_hex(data_item["iv"]):
                logging.error("Invalid initialization vector of in data")
                return False, \
                    "Invalid initialization vector of in data"
            try:
                base64.b64decode(data_item["data"])
            except Exception as e:
                logging.error("Invalid base64 format of in data")
                return False, \
                    "Invalid base64 format of in data"

        return True, ""
    
    def work_order_submit(self, params, in_data, out_data=None, id=None):
        valid, err = self.__validate_parameters(params)
        if not valid:
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                    err)

        valid, err = self.__validate_data_format(in_data)
        if not valid:
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                    err)

        if out_data is not None:
            valid, err = self.__validate_data_format(out_data)
            if not valid:
                return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                    err)

        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkOrderSubmit",
            "id": id
        }
        json_rpc_request["params"] = params
        json_rpc_request["params"]["inData"] = in_data

        if out_data is not None:
            json_rpc_request["outData"] = out_data

        logging.debug("Work order request %s", json.dumps(json_rpc_request))
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    def work_order_get_result_nonblocking(self, work_order_id, id=None):
        """
        Get the work order result in non-blocking way.
        It return json rpc response of dictionary type
        """
        if not is_hex(work_order_id):
            logging.error("Invalid work order Id")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid work order Id")

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
                    response = self.work_order_get_result_nonblocking(work_order_id, id)
                    # TODO: currently pooling after every 2 sec interval forever.
                    # We should implement feature to timeout after responseTimeoutMsecs in the request
                    time.sleep(2)
                return response
