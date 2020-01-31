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

from automation_framework.worker_lookup.worker_lookup_params \
    import WorkerLookUp
from automation_framework.worker_retrieve.worker_retrieve_params \
    import WorkerRetrieve
from automation_framework.worker_register.worker_register_params \
    import WorkerRegister
from automation_framework.worker_set_status.worker_set_status_params \
    import WorkerSetStatus
from automation_framework.worker_update.worker_update_params \
    import WorkerUpdate
from automation_framework.utilities.workflow \
        import submit_request, validate_response_code

logger = logging.getLogger(__name__)


def submit_worker_actions(input_request, request_mode, tamper,
                          output_json_file_name, uri_client,
                          request_method, worker_obj,
                          request_id):
    ''' Function to submit worker actions.
        Reads input json file of the test case.
        Triggers create worker request and submit request.
        Input Parameters :
            input_request : input parameters required to submit request.
            request_mode :
                specifies whether input_temp is a file , string or object
                tamper : Dictionary specifying parameter : value pairs which
                need to added/tampered in the request. Complete tamper utility
                functionality updated in comments of tamper_utility.py.
                Based on method name respective API utilities are called to
                construct the request, tamper and submit to Avalon listener.
            output_json_file_name : For debugging purpose.
            uri_client : HttpJrpcClient class handles JSONs.
            request_method : JSON-RPC APIs request method.
            worker_obj : Worker object to submit the work order request.
            request_id : Unique requester id.
        Returns : worker_obj, input_json_str1, response.'''

    logger.info("----- Testing Worker Actions -----")

    if request_mode == "object":
        # submit work order get result and retrieve response
        logger.info("----- Constructing Request from input object -----")

        input_action = json.loads(action_obj.to_string())
    else:
        logger.info("----- Constructing Request from input json -----")
        if request_method == "WorkerUpdate":
            action_obj = WorkerUpdate()
        elif request_method == "WorkerSetStatus":
            action_obj = WorkerSetStatus()
        elif request_method == "WorkerRegister":
            action_obj = WorkerRegister()
        elif request_method == "WorkerLookUp":
            action_obj = WorkerLookUp()
        elif request_method == "WorkerRetrieve":
            action_obj = WorkerRetrieve()
        else:
            logger.info("----- Invalid Request method -----")

        action_obj.add_json_values(input_request, worker_obj, tamper)
        input_action = json.loads(action_obj.to_string())

    # submit work order request and retrieve response
    response = submit_request(uri_client, input_action,
                              output_json_file_name)

    response_tup = (input_action, response, worker_obj)
    return response_tup
