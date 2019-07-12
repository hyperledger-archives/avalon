import json
import logging
from eth_utils.hexadecimal import is_hex
from service_client.generic import GenericServiceClient
from tcf_connector.worker_registry_interface import WorkerRegistryInterface
from utils.tcf_types import WorkerType, JsonRpcErrorCode
from tcf_connector.utils import create_jrpc_response,validate_details

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
class WorkerRegistryJRPCImpl(WorkerRegistryInterface):
    def __init__(self, config):
        self.__uri_client = GenericServiceClient(config["tcf"]["json_rpc_uri"])

    def worker_register(self, worker_id, worker_type, org_id, application_type_ids,
        details, id=None):
        """ Adds worker details to registry """
        if worker_id is None or not is_hex(worker_id):
            logging.error("Worker id is empty or Invalid")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Worker id is empty or Invalid")
        if not isinstance(worker_type, WorkerType):
            logging.error("Invalid worker type")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid worker type")
        if org_id is not None and not is_hex(org_id):
            logging.error("Invalid organization id")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid organization id")
        if application_type_ids is not None:
            for appId in application_type_ids:
                if not is_hex(appId):
                    logging.error("Invalid application type id")
                    return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                        "Invalid application type id")
                    break
        if details is not None:
            is_valid = validate_details(details)
            if is_valid is not None:
                logging.error(is_valid)
                return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                    is_valid)
        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkerRegister",
            "id": id,
            "params": {
                "workerId": worker_id,
                "workerType": worker_type.value,
                "organizationId": org_id,
                "applicationTypeId": application_type_ids,
                "details": details
            }
        }
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response
    
    def worker_update(self, worker_id, details, id=None):
        """ Update worker with new information """
        if worker_id is None or not is_hex(worker_id):
            logging.error("Worker id is empty or invalid")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Worker id is empty or Invalid")
        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkerUpdate",
            "id": id,
            "params": {
                "workerId": worker_id,
                "details": details
            }
        }
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response


    def worker_set_status(self, worker_id, status, id=None):
        """ Set the worker status to active, offline, decommissioned 
        or compromised state 
        """
        if worker_id is None or not is_hex(worker_id):
            logging.error("Worker id is empty or Invalid")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Worker id is empty or Invalid")

        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkerSetStatus",
            "id": id,
            "params": {
                "workerId": worker_id,
                "status": status.value
            }
        }
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response
    

    def worker_retrieve(self, worker_id, id=None):
        """ Retrieve the worker identified by worker id """
        if worker_id is None or not is_hex(worker_id):
            logging.error("Worker id is empty or Invalid")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Worker id is empty or Invalid")

        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkerRetrieve",
            "id": id,
            "params": {
                "workerId": worker_id
            }
        }
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    
    def worker_lookup(self, worker_type, organization_id, application_type_id,
        id=None):
        """ Worker lookup based on worker type, organization id and application id"""
        if not isinstance(worker_type, WorkerType):
            logging.error("Worker type is invalid")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Worker type is invalid")
        if organization_id is None or not is_hex(organization_id):
            logging.error("Invalid Organization id")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid Organization id")
        if application_type_id is not None:
            for appId in application_type_id:
                if not is_hex(appId):
                    logging.error("Invalid application type id")
                    return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                        "Invalid application type id")
                    break
        

        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkerLookUp",
            "id": id,
            "params": {
                "workerType": worker_type.value,
                "organizationId": organization_id,
                "applicationTypeId": application_type_id
            }
        }
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    
    def worker_lookup_next(self, worker_type, organization_id, 
        application_type_id, lookup_tag, id=None):
        """ Similar to workerLookUp with additional parameter lookup_tag """
        if not isinstance(worker_type, WorkerType):
            logging.error("Worker type is invalid")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Worker type is invalid")
        if organization_id is None or not is_hex(organization_id):
            logging.error("Invalid organization id")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid organization id")
        if application_type_id is not None:
            for appId in application_type_id:
                if not is_hex(appId):
                    logging.error("Invalid application id")
                    return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                        "Invalid application id")
                    break
        

        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkerLookUpNext",
            "id": id,
            "params": {
                "workerType": worker_type.value,
                "organizationId": organization_id,
                "applicationTypeId": application_type_id,
                "lookUpTag": lookup_tag
            }
        }
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

