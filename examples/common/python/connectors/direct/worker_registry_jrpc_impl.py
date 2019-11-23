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
from utility.hex_utils import is_valid_hex_str
from service_client.generic import GenericServiceClient
from connectors.interfaces.worker_registry_interface import WorkerRegistryInterface
from utility.tcf_types import WorkerType, JsonRpcErrorCode
from connectors.utils import create_jrpc_response, validate_details

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class WorkerRegistryJRPCImpl(WorkerRegistryInterface):
    def __init__(self, config):
        self.__uri_client = GenericServiceClient(config["tcf"]["json_rpc_uri"])

    def worker_register(self, worker_id, worker_type, org_id, application_type_ids,
            details, id=None):
        """ Adds worker details to registry """
        if worker_id is None or not is_valid_hex_str(worker_id):
            logging.error("Worker id is empty or Invalid")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Worker id is empty or Invalid")
        if not isinstance(worker_type, WorkerType):
            logging.error("Invalid worker type")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid worker type")
        if org_id is not None and not is_valid_hex_str(org_id):
            logging.error("Invalid organization id")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid organization id")
        if application_type_ids is not None:
            for app_id in application_type_ids:
                if not is_valid_hex_str(app_id):
                    logging.error("Invalid application type id")
                    return create_jrpc_response(
                        id, JsonRpcErrorCode.INVALID_PARAMETER,
                        "Invalid application type id")
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
                "details": json.loads(details)
            }
        }
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    def worker_update(self, worker_id, details, id=None):
        """ Update worker with new information """
        if worker_id is None or not is_valid_hex_str(worker_id):
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
        if worker_id is None or not is_valid_hex_str(worker_id):
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
        if worker_id is None or not is_valid_hex_str(worker_id):
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

    def worker_lookup(self, worker_type=None, organization_id=None,
            application_type_id=None,
            id=None):
        """ Worker lookup based on worker type, organization id
        and application id"""
        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkerLookUp",
            "id": id,
            "params": {
            }
        }

        if worker_type is not None:
            if not isinstance(worker_type, WorkerType):
                logging.error("Invalid worker type")
                return create_jrpc_response(
                    id, JsonRpcErrorCode.INVALID_PARAMETER,
                    "Invalid worker type")
            json_rpc_request["params"]["workerType"] = worker_type.value

        if organization_id is not None:
            if not is_valid_hex_str(organization_id):
                logging.error("Invalid organization id")
                return create_jrpc_response(
                    id, JsonRpcErrorCode.INVALID_PARAMETER,
                    "Invalid organization id")
            json_rpc_request["params"]["organizationId"] = organization_id

        if application_type_id is not None:
            for app_id in application_type_id:
                if not is_valid_hex_str(app_id):
                    logging.error("Invalid application type id")
                    return create_jrpc_response(
                        id, JsonRpcErrorCode.INVALID_PARAMETER,
                        "Invalid application type id")
            json_rpc_request["params"]["applicationTypeId"] = application_type_id

        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    def worker_lookup_next(self, lookup_tag, worker_type=None,
            organization_id=None, application_type_id=None, id=None):
        """ Similar to workerLookUp with additional parameter lookup_tag """

        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkerLookUpNext",
            "id": id,
            "params": {
                "lookUpTag": lookup_tag
            }
        }

        if worker_type is not None:
            if not isinstance(worker_type, WorkerType):
                logging.error("Invalid worker type2")
                return create_jrpc_response(
                    id, JsonRpcErrorCode.INVALID_PARAMETER,
                    "Invalid worker type")
            json_rpc_request["params"]["workerType"] = worker_type.value

        if organization_id is not None:
            if not is_valid_hex_str(organization_id):
                logging.error("Invalid organization id")
                return create_jrpc_response(
                    id, JsonRpcErrorCode.INVALID_PARAMETER,
                    "Invalid organization id")
            json_rpc_request["params"]["organizationId"] = organization_id

        if application_type_id is not None:
            for app_id in application_type_id:
                if not is_valid_hex_str(app_id):
                    logging.error("Invalid application type id")
                    return create_jrpc_response(
                        id, JsonRpcErrorCode.INVALID_PARAMETER,
                        "Invalid application type id")
            json_rpc_request["params"]["applicationTypeId"] = application_type_id

        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response
