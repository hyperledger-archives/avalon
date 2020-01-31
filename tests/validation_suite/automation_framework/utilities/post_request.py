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

import automation_framework.work_order_submit.work_order_submit_utility as \
    wo_utility
import automation_framework.work_order_get_result. \
    work_order_get_result_utility as wo_get_result
import automation_framework.worker.worker_utility as worker_utility
from automation_framework.utilities.workflow import submit_request, \
    check_for_variable_count

logger = logging.getLogger(__name__)


def post_request(request_tup):
    """
    Function to submit JSON-RPC requests and extracts parameters of
    APIs's requests from request_tup.
    request_tup :
        Parameter with required inputs to submit JSON-RPC requests.
    input_temp :
        File - Request can be provided as a json filename.
        String - request can be constructed and passed as a
                 string to the framework.
        Object - using respective API classes request can be constructed
                 in test case and passed to framework for submiting
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

    These are the common parameters for all the submit requests.
    For API specific parameters please refer below.
    """
    try:
        if check_for_variable_count(request_tup,
                                    lambda k: k is not len(request_tup)):
            logger.info("------ Request input variables are proper. ------\n")
    except Exception:
        logger.info("------ Request input variables are not proper. ------\n")

    (input_temp, request_mode, tamper, output_json_file_name,
     uri_client, request_method) = request_tup[:6]

    if request_mode == "file":
        # read json input file for the test case
        logger.info("------ Input file name: %s ------\n", input_temp)
        with open(input_temp, "r") as file:
            input_json = file.read().rstrip('\n')
    elif request_mode == "string":
        input_json = input_temp
        logger.info("------ Loaded string data: %s ------\n", input_request)
    try:
        if request_mode != "object":
            input_request = json.loads(input_json)
    except Exception:
        logger.info('Invalid Json Input. Submitting to Avalon listener \
                       without modifications to test response')

    if request_mode == "object":
        input_method = request_method
        input_request = input_temp
    else:
        input_method = input_request["method"]

    if input_method == "WorkOrderSubmit":
        """
        worker_obj :  Worker object to submit the work order request.
        private_key : Private key used to submit the request.
        err_cd : Status of previous request (worker retrieve), Success or Fail.
        """
        worker_obj, private_key, err_cd, check_result_1 = request_tup[6:10]

        response_tup = wo_utility.submit_work_order(
            input_request, request_mode, tamper,
            output_json_file_name, uri_client,
            worker_obj, input_method, private_key,
            err_cd)

    elif input_method is "WorkOrderGetResult":
        """
        err_cd : Status of previous request (work order submit).
        work_order_id : Same work order id as in work order submit.
        request_id : Unique requester id.
        """
        err_cd, work_order_id, request_id = request_tup[6:9]

        response_tup = wo_get_result.submit_work_order_get_result(
            input_request, request_mode, tamper, output_json_file_name,
            uri_client, err_cd, work_order_id, request_id)

    elif input_method in ("WorkerUpdate", "WorkerLookUp", "WorkerRetrieve",
                          "WorkerRegister", "WorkerSetStatus"):
        """
        worker_obj : Worker object to submit the worker request.
        request_id : Unique requester id.
        """
        worker_obj, request_id = request_tup[6:8]

        response_tup = worker_utility.submit_worker_actions(
            input_request, request_mode, tamper, output_json_file_name,
            uri_client, input_method, worker_obj, request_id)

    return response_tup
