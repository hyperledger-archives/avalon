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

logger = logging.getLogger(__name__)


class WorkerRegister():
    def __init__(self):
        self.id_obj = {"jsonrpc": "2.0", "method": "WorkerRegister", "id": 10}
        self.params_obj = {}
        self.details_obj = {}
        self.worker_type_data_obj = {}

    def add_json_values(self, input_json_temp, worker_obj, tamper):

        if "workerId" in input_json_temp["params"].keys():
            if input_json_temp["params"]["workerId"] != "":
                self.set_worker_type(input_json_temp["params"]["workerId"])
            else:
                self.set_worker_type(worker_obj.worker_id)

        if "id" in input_json_temp.keys():
            self.set_request_id(input_json_temp["id"])

        if "workerType" in input_json_temp["params"].keys():
            if input_json_temp["params"]["workerType"] != "":
                self.set_worker_type(input_json_temp["params"]["workerType"])
            else:
                self.set_worker_type(1)

        if "organizationId" in input_json_temp["params"].keys():
            if input_json_temp["params"]["organizationId"] != "":
                self.set_worker_type(
                    input_json_temp["params"]["organizationId"])
            else:
                self.set_worker_type(worker_obj.organization_id)

        if "applicationTypeId" in input_json_temp["params"].keys():
            if input_json_temp["params"]["applicationTypeId"] != "":
                self.set_worker_type(
                    input_json_temp["params"]["applicationTypeId"])
            else:
                self.set_worker_type(worker_obj.application_type_id)

        if "workerEncryptionKey" in input_json_temp["params"].keys():
            if input_json_temp["params"]["workerEncryptionKey"] != "":
                self.set_worker_type(
                    input_json_temp["params"]["workerEncryptionKey"])
            else:
                self.set_worker_type(worker_obj.worker_encryption_key)

        if "details" in input_json_temp["params"].keys():
            if ("hashingAlgorithm" in
                    input_json_temp["params"]["details"].keys()):
                self.set_hashing_algorithm(
                    input_json_temp["params"]["details"]["hashingAlgorithm"])

            if ("signingAlgorithm" in
                    input_json_temp["params"]["details"].keys()):
                self.set_signing_algorithm(
                    input_json_temp["params"]["details"]["signingAlgorithm"])

            if ("keyEncryptionAlgorithm" in
                    input_json_temp["params"]["details"].keys()):
                self.set_key_encryption_algorithm(
                    input_json_temp["params"]["details"]
                    ["keyEncryptionAlgorithm"])

            if ("dataEncryptionAlgorithm" in
                    input_json_temp["params"]["details"].keys()):
                self.set_data_encryption_algorithm(
                    input_json_temp["params"]["details"]
                    ["dataEncryptionAlgorithm"])

        for key in tamper["params"].keys():
            param = key
            value = tamper["params"][key]
            self.set_unknown_parameter(param, value)

    def set_unknown_parameter(self, param, value):
        self.params_obj[param] = value

    def set_worker_type(self, worker_type):
        self.params_obj["workerType"] = worker_type

    def set_request_id(self, request_id):
        self.id_obj["id"] = request_id

    def set_hashing_algorithm(self, hashing_algorithm):
        self.details_obj["hashingAlgorithm"] = hashing_algorithm

    def set_signing_algorithm(self, signing_algorithm):
        self.details_obj["signingAlgorithm"] = signing_algorithm

    def set_key_encryption_algorithm(self, key_encryption_algorithm):
        self.details_obj["keyEncryptionAlgorithm"] = key_encryption_algorithm

    def set_data_encryption_algorithm(self, data_encryption_algorithm):
        self.details_obj["dataEncryptionAlgorithm"] = data_encryption_algorithm

    def get_params(self):
        return self.params_obj.copy()

    def get_details(self):
        return self.details_obj.copy()

    def to_string(self):
        json_rpc_request = self.id_obj
        json_rpc_request["params"] = self.get_params()
        json_rpc_request["params"]["details"] = self.get_details()

        return json.dumps(json_rpc_request, indent=4)
