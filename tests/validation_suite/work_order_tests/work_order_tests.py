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
from automation_framework.utilities.post_request import \
    post_request

logger = logging.getLogger(__name__)


def work_order_get_result_params(wo_response, generic_params):
    uri_client = generic_params[1]

    # extract response values
    err_cd, input_json_str1 = wo_response[:2]
    work_order_id = input_json_str1["params"]["workOrderId"]
    request_id = input_json_str1["id"] + 1
    input_request = {}
    request_mode = "object"
    tamper = {}
    output_json_file_name = "work_order_get_result"
    request_method = "WorkOrderGetResult"

    # submit work order get result
    request_get_result = (input_request, request_mode, tamper,
                          output_json_file_name, uri_client, request_method,
                          err_cd, work_order_id, request_id)
    response_get_result = post_request(request_get_result)

    # extract response values
    err_cd, response = response_get_result[:2]
    return err_cd, response


def work_order_request_params(setup_config, request):
    worker_obj, uri_client, private_key, err_cd = setup_config
    # request mode - file, string or object
    request_mode = 'file'
    # output filename
    output_json_file_name = 'work_order_success'
    # tamper parameters
    tamper = {"params": {}}
    # request method to be used when submiting object input type
    request_method = ""

    # expected response
    check_submit = {"error": {"code": 5}}

    request_tup = (request, request_mode, tamper, output_json_file_name,
                   uri_client, request_method, worker_obj, private_key, err_cd,
                   check_submit)
    response_tup = post_request(request_tup)

    return response_tup, setup_config
