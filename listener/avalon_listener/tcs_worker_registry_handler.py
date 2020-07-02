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
from error_code.error_status import WorkerError
from avalon_sdk.worker.worker_details import WorkerStatus
import schema_validation.validate as Validator
from jsonrpc.exceptions import JSONRPCDispatchException

logger = logging.getLogger(__name__)


class TCSWorkerRegistryHandler:
    """
     TCSWorkerRegistryHandler processes worker registry requests defined in the
     TC API spec at Worker Registry Direct API and Worker Type Data API. It
     reads appropriate worker information from the KV storage to generate the
     response.
     All raised exceptions will be caught and handled by any
    jsonrpc.dispatcher.Dispatcher delegating work to this handler. In our case,
    the exact dispatcher will be the one configured by the TCSListener in the
    ./tcs_listener.py
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
        # json with byte32 orgID, string uri, byte32 scAddr,
        #   bytes32[] appTypeIds)
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
            response['error']['message'] = 'Unknown Error occurred during' + \
                'worker registry handler boot up'

        return response

# ------------------------------------------------------------------------------------------------
    def __lookup_basic(self, is_lookup_next, params):
        # sync the work pool to that of DB
        self.worker_pool = self.kv_helper.lookup("workers")

        total_count = 0
        ids = []
        lookupTag = ""

        for worker_id in self.worker_pool:
            if is_lookup_next:
                # loop until found the expected lookUpTag
                is_lookup_next = (worker_id != params["lookupTag"])
                continue

            matched = True
            value = self.kv_helper.get("workers", worker_id)
            if value:
                worker = json.loads(value)
                criteria = ["workerType", "organizationId",
                            "applicationTypeId"]

                for c in criteria:
                    if params.get(c) is None:
                        continue

                    matched = (worker[c] == params[c])
                    if not matched:
                        break

            if matched:
                total_count = total_count + 1
                ids.append(worker_id)
                lookupTag = worker_id

        result = {
            "totalCount": total_count,
            "lookupTag": lookupTag,
            "ids": ids,
        }

        return result

# ------------------------------------------------------------------------------------------------

    def WorkerLookUp(self, **params):
        """
        Function to look the set of workers available
        Parameters:
            - param is the 'param' object in the a worker request as per TCF
                API 5.3.4 Worker Lookup JSON Payload
        """
        input_json_str = params["raw"]
        input_value_json = json.loads(input_json_str)
        valid, err_msg = \
            Validator.schema_validation(
                "WorkerLookUp",
                input_value_json["params"])
        logger.info(err_msg)
        if not valid:
            raise JSONRPCDispatchException(
                WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE,
                err_msg
             )
        return self.__lookup_basic(False, params)
# ------------------------------------------------------------------------------------------------

    def WorkerLookUpNext(self, **params):
        """
        Function to look the set of worker newly added
        Parameters:
            - param is the 'param' object in the a worker request as per TCF
                API 5.3.5 Worker Lookup Next JSON Payload
        """
        input_json_str = params["raw"]
        input_value_json = json.loads(input_json_str)
        valid, err_msg = \
            Validator.schema_validation(
                "WorkerLookUpNext",
                input_value_json["params"])
        if not valid:
            raise JSONRPCDispatchException(
                WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE,
                err_msg
            )
        return self.__lookup_basic(True, params)
# ------------------------------------------------------------------------------------------------

    def WorkerRetrieve(self, **params):
        """
        Function to retrieve the details of worker
        Parameters:
            - param is the 'param' object in the a worker request as per
                Trusted Compute EEA API 5.3.7 Worker Retrieve JSON Payload
        """

        input_json_str = params["raw"]
        input_value_json = json.loads(input_json_str)
        valid, err_msg = \
            Validator.schema_validation(
                "WorkerRetrieve",
                input_value_json["params"])
        if not valid:
            raise JSONRPCDispatchException(
                WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE,
                err_msg
            )
        # value retrieved is 'result' field as per Spec 5.3.8 Worker Retrieve
        # Response Payload
        worker_id = str(params['workerId'])
        value = self.kv_helper.get("workers", worker_id)

        if value is None:
            raise JSONRPCDispatchException(
                WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE,
                "Worker Id not found in the database. Hence invalid parameter")

        json_dict = json.loads(value)

        result = {
            "workerType": json_dict["workerType"],
            "organizationId": json_dict["organizationId"],
            "applicationTypeId": json_dict["applicationTypeId"],
            "details": json_dict["details"],
            "status": json_dict["status"],
        }

        return result
# ------------------------------------------------------------------------------------------------
