import json
import logging
from eth_utils.hexadecimal import is_hex
import base64
from service_client.generic import GenericServiceClient
from tcf_connector.work_order_interface import WorkOrderInterface
from tcf_connector.utils import create_jrpc_response
from utils.tcf_types import JsonRpcErrorCode

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
            "encryptedDataEncryptionKey":True,
            "iv":True
            }
    
    def __validate_parameters(self, params, in_data, out_data):
        """Validate parameter dictionary for existence of fields and mandatory fields """
        key_list = []
        for key in params.keys():
            if not key in self.__param_key_map.keys():
                logging.error("Invalid parameter %s",key)
                return "Invalid parameter {}".format(key)
            else:
                key_list.append(key)
        for k, v in self.__param_key_map.items():
            if v == True and not k in key_list:
                logging.error("Missing parameter %s", k)
                return "Missing parameter {}".format(k)
        """Validate in_data and out_data dictionary for existence of fields
        and mandatory fields """
        
        for data in in_data:
            in_data_keys = []
            for key in data.keys():
                if not key in self.__data_key_map.keys():
                    logging.error("Invalid in data parameter %s",key)
                    return "Invalid in data parameter {}".format(key)
                else:
                    in_data_keys.append(key)
            for k, v in self.__data_key_map.items():
                if v == True and not k in in_data_keys:
                    logging.error("Missing in data parameter %s", k)
                    return "Missing in data parameter {}".format(k)
        
        for data in out_data:
            out_data_keys = []
            for key in data.keys():
                if not key in self.__data_key_map.keys():
                    logging.error("Invalid out data parameter %s",key)
                    return "Invalid out data parameter {}".format(key)
                else:
                    out_data_keys.append(key)
            for k, v in self.__data_key_map.items():
                if v == True and not k in out_data_keys:
                    logging.error("Missing out data parameter %s", k)
                    return "Missing out data parameter {}".format(k)

        return None
    
    def work_order_submit(self, params, in_data, out_data, id=None):
        is_valid = self.__validate_parameters(params, in_data, out_data)
        if is_valid is not None:
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                    is_valid)
        if not is_hex(params["workOrderId"]):
            logging.error("Invalid work order id")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid work order id")
        if not is_hex(params["workloadId"]):
            logging.error("Invalid work load id")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid work load id")
        if not is_hex(params["requesterId"]):
            logging.error("Invalid requester id id")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid requester id id")
        if not is_hex(params["workerEncryptionKey"]):
            logging.error("Invalid worker encryption key")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid worker encryption key")
        for data in in_data:
            if not is_hex(data["dataHash"]):
                logging.error("Invalid data hash of in data")
                return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                    "Invalid data hash of in data")
            if not is_hex(data["encryptedDataEncryptionKey"]):
                logging.error("Invalid Encryption key of in data")
                return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                    "Invalid Encryption key of in data")
            if not is_hex(data["iv"]):
                logging.error("Invalid initialization vector of in data")
                return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                    "Invalid initialization vector of in data")
            try:
                base64.b64decode(data["data"])
            except Exception as e:
                logging.error("Invalid base64 format of in data")
                return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                    "Invalid base64 format of in data")
        
        for data in out_data:
            if not is_hex(data["dataHash"]):
                logging.error("Invalid data hash of out data")
                return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                    "Invalid data hash of out data")
            if not is_hex(data["encryptedDataEncryptionKey"]):
                logging.error("Invalid Encryption key of out data")
                return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                    "Invalid Encryption key of out data")
            if not is_hex(data["iv"]):
                logging.error("Invalid initialization vector of out data")
                return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                    "Invalid initialization vector of out data")
            try:
                base64.b64decode(data["data"])
            except Exception as e:
                logging.error("Invalid base64 format of out data")
                return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                    "Invalid base64 format of out data")

        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkOrderSubmit",
            "id": id,
            "params": 
            {
                "responseTimeoutMSecs": params["responseTimeoutMSecs"],
                "payloadFormat": params["payloadFormat"],
                "resultUri": params["resultUri"],
                "notifyUri": params["notifyUri"],
                "workOrderId": params["workOrderId"],
                "workerId": params["workerId"],
                "workloadId": params["workloadId"],
                "requesterId": params["requesterId"],
                "workerEncryptionKey": params["workerEncryptionKey"],
                "dataEncryptionAlgorithm": params["dataEncryptionAlgorithm"],
                "encryptedSessionKey": params["encryptedSessionKey"],
                "sessionKeyIv": params["sessionKeyIv"],
                "requesterNonce": params["requesterNonce"],
                "encryptedRequestHash": params["encryptedRequestHash"],
                "requesterSignature": params["requesterSignature"],
                "inData": in_data,
                "outData": out_data
            }
        }
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    def work_order_get_result(self, work_order_id, id=None):
        if not is_hex(work_order_id):
            logging.error("Invalid workOrder Id")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid workOrder Id")

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

