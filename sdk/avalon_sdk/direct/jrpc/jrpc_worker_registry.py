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

import json
import logging
from utility.hex_utils import is_valid_hex_str
from avalon_sdk.http_client.http_jrpc_client import HttpJrpcClient
from avalon_sdk.interfaces.worker_registry \
    import WorkerRegistry

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s",
                    level=logging.INFO)


class JRPCWorkerRegistryImpl(WorkerRegistry):
    """
    This class is to read the worker registry to get the more details
    of worker.
    """

    def __init__(self, config):
        self.__uri_client = HttpJrpcClient(config["tcf"]["json_rpc_uri"])

    def worker_retrieve(self, worker_id, id=None):
        """
        Retrieve the worker identified by worker id
        Returns jrpc response containing
        organization id, application id, worker status,
        worker details
        """

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
                      application_type_id=None, id=None):
        """
        Worker lookup based on worker type, organization id
        and application id
        Returns jrpc response containing number of workers,
        lookup tag and list of worker ids.
        """
        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkerLookUp",
            "id": id,
            "params": {
            }
        }

        if worker_type is not None:
            json_rpc_request["params"]["workerType"] = worker_type.value

        if organization_id is not None:
            json_rpc_request["params"]["organizationId"] = organization_id

        if application_type_id is not None:
            json_rpc_request["params"]["applicationTypeId"] = \
                application_type_id

        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    def worker_lookup_next(self, lookup_tag, worker_type=None,
                           organization_id=None, application_type_id=None,
                           id=None):
        """
        Similar to workerLookUp with additional
        parameter lookup_tag
        Returns jrpc response containing number of workers,
        lookup tag and list of worker ids.
        """

        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkerLookUpNext",
            "id": id,
            "params": {
                "lookUpTag": lookup_tag
            }
        }

        if worker_type is not None:
            json_rpc_request["params"]["workerType"] = worker_type.value

        if organization_id is not None:
            json_rpc_request["params"]["organizationId"] = organization_id

        if application_type_id is not None:
            json_rpc_request["params"]["applicationTypeId"] = \
                application_type_id

        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    def worker_register(self, worker_id, worker_type, org_id,
                        application_type_ids, details, id=None):
        """
        Adds worker details to registry
        Returns jrpc response with worker registry status.
        """
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
        """
        Update worker with new information
        Returns jrpc response with update status.
        """
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
        """
        Set the worker status to active, offline,
        decommissioned	or compromised state
        Returns jrpc response with status.
        """
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
