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

import pytest
import json
import logging

logger = logging.getLogger(__name__)

def tamper_request(input_json, tamper_instance, tamper):
    '''Function to tamper the input request at required instances.
       Valid instances used in test framework are :
       force, add, remove.
       force : used by API class definitions primarily to force null values to
               parameter values to replace default values and to add
               unknown parameter key, value pair to request parameters for the
               purpose of testing. code for the same coded in respective api
               classes
       add : can be used to add a parameter and value not in input json,
             also can be used to replace a value for parameter in input json
       remove : deletes the parameter from input json

       The function can be used for other instances also provided the instances
       are used in test framework and also value of tamper defined in test case

       A blank tamper dictionary is required for all test cases, in cases where
       tamper functionality is not required. Example : tamper{"params":{}}'''


    before_sign_keys = []
    after_sign_keys = []
    input_json_temp = json.loads(input_json)

    if tamper_instance in tamper["params"].keys() :
        tamper_instance_keys = tamper["params"][tamper_instance].keys()

        for tamper_key in tamper_instance_keys :
            for action_key in (
                    tamper["params"][tamper_instance][tamper_key].keys()) :
                if action_key == "add" :
                    input_json_temp["params"][tamper_key] = (
                    tamper["params"][tamper_instance][tamper_key]["add"])
                elif action_key == "remove" :
                    del input_json_temp["params"][tamper_key]

    tampered_json = json.dumps(input_json_temp)

    return tampered_json
