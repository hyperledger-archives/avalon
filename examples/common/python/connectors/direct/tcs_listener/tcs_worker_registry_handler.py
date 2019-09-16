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
import utility.utility as utility
from error_code.error_status import WorkerError
from error_code.error_status import WorkerStatus

logger = logging.getLogger(__name__)


class TCSWorkerRegistryHandler:
    """
     TCSWorkerRegistryHandler processes worker registry requests defined in the TC API spec at Worker Registry Direct API and Worker Type Data API . It reads appropriate worker information from the KV storage to generate the response
    """
# ------------------------------------------------------------------------------------------------

    def __init__(self, kv_helper):
        """
        Function to perform init activity
        Parameters:
            - kv_helper is a object of lmdb database
        """

        self.kv_helper = kv_helper
        self.worker_pool = []
        self.__worker_registry_handler_on_boot()
# ------------------------------------------------------------------------------------------------

    def __worker_registry_handler_on_boot(self):
        """
        Function to perform on-boot process of worker registry handler
        """

        worker_list = []
        worker_list = self.kv_helper.lookup("workers")

        # Initial Worker details are loaded
        self.worker_pool = worker_list
        organisation_id = self.kv_helper.lookup("registries")
        for o_id in organisation_id:
            self.kv_helper.remove("registries", o_id)

        # Adding a new entry that corresponds to this handler, its URI, etc.
        # json with byte32 orgID, string uri, byte32 scAddr, bytes32[] appTypeIds)
        new_registry = {}
        new_registry["orgID"] = "regid"
        new_registry["uri"] = "http://localhost:2020"
        new_registry["scAddr"] = "reg_scAddr"
        new_registry["appTypeIds"] = "reg_appn"

        value = json.dumps(new_registry)
        response = {}
        response['id'] = "regid"

        set_response = self.kv_helper.set("registries", "regid", value)
        if set_response:
            response['result'] = "WorkerRegistryHandleronBoot Successful"
            response['error'] = {}
            response['error']['code'] = WorkerError.SUCCESS
        else:
            response['error'] = {}
            response['error']['code'] = WorkerError.UNKNOWN_ERROR
            response['error']['message'] = 'Unknown Error occurred during worker registry handler boot up'

        return response
# ------------------------------------------------------------------------------------------------

    def worker_registry_handler(self, input_json_str):
        """
        Function to process worker request
        Parameters:
            - input_json_str is a worker request json as per TCF API 5.3 Off-Chain Worker Registry JSON RPC API
        """

        input_json = json.loads(input_json_str)
        response = {}
        response['jsonrpc'] = '2.0'
        response['id'] = input_json['id']

        logger.info("Received Worker request : %s", input_json['method'])

        if(input_json['method'] == "WorkerLookUp"):
            return self.__process_worker_lookup(input_json, response)
        elif(input_json['method'] == "WorkerLookUpNext"):
            return self.__process_worker_lookup_next(input_json, response)

        if 'workerId' in input_json_str:
            worker_id = str(input_json['params']['workerId'])
        else:
            return utility.create_error_response(
                WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE,
                input_json["id"],
                "Worker Id not found in the database. \
                     Hence invalid parameter")

        if(input_json['method'] == "WorkerRegister"):
            return self.__process_worker_register(worker_id, input_json, response)
        elif(input_json['method'] == "WorkerSetStatus"):
            return self.__process_worker_set_status(worker_id, input_json, response)
        elif(input_json['method'] == "WorkerRetrieve"):
            return self.__process_worker_retrieve(worker_id, response)
        elif(input_json['method'] == "WorkerUpdate"):
            return self.__process_worker_update(worker_id, input_json, response)
# ------------------------------------------------------------------------------------------------

    def __process_worker_register(self, worker_id, input_value_json, response):
        """
        Function to register a new worker to the enclave
        Parameters:
            - worker_id is the worker id specified in the input json str.
            - input_json_str is a worker request json as per TCF API 5.3.1 Worker Register JSON Payload.
            - response is the response object to be returned to client.
        """

        jrpc_id = input_value_json["id"]

        if(self.kv_helper.get("workers", worker_id) is None):
            input_value = {}
            input_value = input_value_json['params']

            # Worker Initial Status is set to Active
            input_value["status"] = WorkerStatus.ACTIVE

            input_json_str = json.dumps(input_value)
            self.kv_helper.set("workers", worker_id, input_json_str)
            response = utility.create_error_response(
                WorkerError.SUCCESS, jrpc_id,
                "Successfully Registered")
        else:
            response = utility.create_error_response(
                WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE,
                jrpc_id,
                "Worker Id already exists in the database. \
                 Hence invalid parameter")
        return response
# ------------------------------------------------------------------------------------------------

    def __process_worker_set_status(self, worker_id, input_value, response):
        """
        Function to set the status of worker
        Parameters:
            - worker_id is the worker id specified in the input json str.
            - input_json_str is a worker request json as per TCF API 5.3.3 Worker Set Status JSON Payload
            - response is the response object to be returned to client.
        """

        # status can be one of active, offline, decommissioned, or compromised

        jrpc_id = input_value["id"]

        value = self.kv_helper.get("workers", worker_id)
        if value:
            json_dict = json.loads(value)
            json_dict['status'] = input_value['params']['status']

            value = json.dumps(json_dict)
            self.kv_helper.set("workers", worker_id, value)
            response = utility.create_error_response(
                WorkerError.SUCCESS, jrpc_id,
                "Successfully Set Status")
        else:
            response = utility.create_error_response(
                WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE,
                jrpc_id,
                "Worker Id not found in the database. \
                 Hence invalid parameter")

        return response
# ------------------------------------------------------------------------------------------------

    def __lookup_basic(self, is_lookup_next, input_value, response):
        # sync the work pool to that of DB
        self.worker_pool = self.kv_helper.lookup("workers")

        total_count = 0
        ids = []
        lookupTag = ""

        params = input_value["params"]
        for worker_id in self.worker_pool:
            if is_lookup_next:
                # loop until found the expected lookUpTag
                is_lookup_next = (worker_id != params["lookupTag"])
                continue

            matched = True
            value = self.kv_helper.get("workers", worker_id)
            if value:
                worker = json.loads(value)
                criteria = ["workerType", "organizationId", "applicationTypeId"]

                for c in criteria:
                    if params.get(c) is None:
                        continue

                    matched = (worker[c] == params[c])
                    if not matched:
                        break

            if matched:
                total_count = total_count+1
                ids.append(worker_id)
                lookupTag = worker_id

        response["result"] = {
            "totalCount": total_count,
            "lookupTag": lookupTag,
            "ids": ids,
        }

        return response
# ------------------------------------------------------------------------------------------------

    def __process_worker_lookup(self, input_json, response):
        """
        Function to look the set of workers available
        Parameters:
            - input_json is a worker request as per TCF API 5.3.4 Worker Lookup JSON Payload
            - response is the response object to be returned to client.
        """

        self.__lookup_basic(False, input_json, response)
        return response
# ------------------------------------------------------------------------------------------------

    def __process_worker_lookup_next(self, input_json, response):
        """
        Function to look the set of worker newly added
        Parameters:
            - input_json is a worker request as per TCF API 5.3.5 Worker Lookup Next JSON Payload
            - response is the response object to be returned to client.
        """

        self.__lookup_basic(True, input_json, response)
        return response
# ------------------------------------------------------------------------------------------------

    def __process_worker_retrieve(self, worker_id, response):
        """
        Function to retrieve the details of worker
        Parameters:
            - worker_id is the worker id specified in worker request json as per TCF API 5.3.7 Worker Retrieve JSON Payload
            - response is the response object to be returned to client.
        """

        # value retrieved is 'result' field as per Spec 5.3.8 Worker Retrieve Response Payload
        value = self.kv_helper.get("workers", worker_id)

        if value is not None:
            json_dict = json.loads(value)
            response["result"] = {}
            response["result"]["workerType"] = json_dict["workerType"]
            response["result"]["organizationId"] = json_dict["organizationId"]
            response["result"]["applicationTypeId"] = json_dict["applicationTypeId"]
            response["result"]["details"] = json_dict["details"]
            response["result"]["status"] = json_dict["status"]
        else:
            jrpc_id = json.loads(response)["id"]
            response = utility.create_error_response(
                WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE,
                jrpc_id,
                "Worker Id not found in the database. Hence invalid parameter")
        return response
# ------------------------------------------------------------------------------------------------

    def __process_worker_update(self, worker_id, input_value, response):
        """
        Function to update the worker details.
        Parameters:
            - worker_id is the worker id specified in the input json str.
            - input_json is a worker request as per TCF API 5.3.2 Worker Update JSON Payload
            - response is the response object to be returned to client.
        """

        jrpc_id = input_value["id"]

        # value retrieved is 'result' field as per Spec 5.3.8 Worker Retrieve Response Payload
        value = self.kv_helper.get("workers", worker_id)

        if value is not None:
            json_dict = json.loads(value)
            worker_details = input_value["params"]["details"]
            for item in worker_details:
                json_dict["details"][item] = worker_details[item]

            value = json.dumps(json_dict)
            self.kv_helper.set("workers", worker_id, value)
            response = utility.create_error_response(
                WorkerError.SUCCESS, jrpc_id,
                "Successfully Updated")
        else:
            response = utility.create_error_response(
                WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE,
                jrpc_id,
                "Worker Id not found in the database. \
                 Hence invalid parameter")
        return response
# ------------------------------------------------------------------------------------------------
