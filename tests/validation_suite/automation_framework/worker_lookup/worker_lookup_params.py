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
import worker.worker_details as worker

logger = logging.getLogger(__name__)

class WorkerLookUp():
    def __init__(self):
        self.id_obj = {"jsonrpc": "2.0", "method": "WorkerLookUp", "id": 1}
        self.params_obj = {}

    def add_json_values(self, input_json_temp, worker_obj, tamper):

        if "workerType" in input_json_temp["params"].keys() :
            if input_json_temp["params"]["workerType"] != "" :
                self.set_worker_type(input_json_temp["params"]["workerType"])
            else :
                self.set_worker_type(1)

        if "id" in input_json_temp.keys() :
            self.set_request_id(input_json_temp["id"])

        for key in tamper["params"].keys() :
            param = key
            value = tamper["params"][key]
            self.set_unknown_parameter(param, value)

    def set_unknown_parameter(self, param, value):
        self.params_obj[param] = value

    def set_worker_type(self, worker_type):
        self.params_obj["workerType"] = worker_type

    def set_request_id(self, request_id):
        self.id_obj["id"] = request_id

    def get_params(self):
        return self.params_obj.copy()

    def to_string(self):
        json_rpc_request = self.id_obj
        json_rpc_request["params"] = self.get_params()

        return json.dumps(json_rpc_request, indent=4)
