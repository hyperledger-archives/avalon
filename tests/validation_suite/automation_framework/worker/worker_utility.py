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
import logging
import json

from automation_framework.worker_lookup.worker_lookup_params import WorkerLookUp
from automation_framework.worker_retrieve.worker_retrieve_params \
                                             import WorkerRetrieve
from automation_framework.worker_register.worker_register_params \
                                             import WorkerRegister
from automation_framework.worker_set_status.worker_set_status_params \
                                             import WorkerSetStatus
from automation_framework.worker_update.worker_update_params import WorkerUpdate
from automation_framework.utilities.workflow import process_request
from automation_framework.utilities.workflow import validate_response_code
import worker.worker_details as worker

logger = logging.getLogger(__name__)

def process_worker_actions(input_request, input_type, tamper,
               output_json_file_name, uri_client, request_method, worker_obj,
               request_id, check_action_result) :
    ''' Function to process worker actions.
        Reads input json file of the test case.
        Triggers create worker request, process request and validate response.
        Input Parameters : input_json_file, id_gen, output_json_file_name,
        worker_obj, uri_client, check_worker_result
        Returns : err_cd, worker_obj, input_json_str1, response. '''

    logger.info("----- Testing Worker Actions -----")

    if input_type == "object" :
        # process work order get result and retrieve response
        logger.info("----- Constructing Request from input object -----")

        input_action = json.loads(action_obj.to_string())
    else :
        logger.info("----- Constructing Request from input json -----")
        if request_method == "WorkerUpdate" :
            action_obj = WorkerUpdate()
        elif request_method == "WorkerSetStatus" :
            action_obj = WorkerSetStatus()
        elif request_method == "WorkerRegister" :
            action_obj = WorkerRegister()
        elif request_method == "WorkerLookUp" :
            action_obj = WorkerLookUp()
        elif request_method == "WorkerRetrieve" :
            action_obj = WorkerRetrieve()
        else :
            logger.info("----- Invalid Request method -----")

        action_obj.add_json_values(input_request, worker_obj, tamper)
        input_action = json.loads(action_obj.to_string())

    # submit work order request and retrieve response
    response = process_request(uri_client, input_action,
                              output_json_file_name)
    # validate work order response and get error code
    err_cd = validate_response_code(response, check_action_result)

    response_tup = (err_cd, input_action, response, worker_obj)
    return response_tup
