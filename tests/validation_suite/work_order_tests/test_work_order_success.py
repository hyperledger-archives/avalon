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
from automation_framework.utilities.process_api_request import \
                                    process_api_request
import automation_framework.work_order_submit.work_order_submit_utility as \
                                                             wo_utility
import automation_framework.work_order_get_result.work_order_get_result_utility \
                                                               as wo_get_result
from automation_framework.utilities.request_args import TestStep

logger = logging.getLogger(__name__)

def test_work_order_success(setup_config):
    """ Testing work order request with all valid parameter values. """

    # retrieve values from conftest session fixture
    worker_obj = setup_config[0]
    uri_client = setup_config[1]
    private_key = setup_config[2]
    err_cd = setup_config[3]

    # input file name
    input_json_file = 'work_order_tests/input/work_order_success.json'
    # input type - file, string or object
    input_type = 'file'
    # output filename
    output_json_file_name = 'work_order_success'
    # tamper parameters
    tamper = {"params": {}}
    # request method to be used when processing object input type
    request_method = ""

    # expected response
    check_submit = {"error": {"code": 5}}
    check_result = '''{"result": {"workOrderId": "", "workloadId": "",
                       "workerId": "", "requesterId": "", "workerNonce": "",
                       "workerSignature": "", "outData": ""}}'''
    check_get_result = json.loads(check_result)

    request_tup=(input_json_file, input_type, tamper, output_json_file_name,
                 uri_client, request_method, worker_obj, private_key, err_cd,
                 check_submit, check_get_result)
    response_tup = process_api_request(request_tup)

    # extract response values
    err_cd = response_tup[0]
    input_json_str1 = response_tup[1]
    response = response_tup[2]
    session_key = response_tup[3]
    session_iv = response_tup[4]
    encrypted_session_key = response_tup[5]

    # input parameters for processing work order get result
    work_order_id = input_json_str1["params"]["workOrderId"]
    request_id = input_json_str1["id"] + 1
    input_request = {}
    input_type = "object"
    tamper = {}
    output_json_file_name = "work_order_get_result"
    request_method = "WorkOrderGetResult"

    # process work order get result
    request_get_result = (input_request, input_type, tamper,
                          output_json_file_name, uri_client, request_method,
                          err_cd, work_order_id, request_id, check_get_result)
    response_get_result = process_api_request(request_get_result)

    # extract response values
    err_cd = response_get_result[0]
    response = response_get_result[1]

    if err_cd == TestStep.SUCCESS.value:
        # verify signature if work order processed as expected
        err_cd = wo_utility.verify_work_order_signature(response,
                 worker_obj)

    if err_cd == TestStep.SUCCESS.value:
        # decrypt signature if verify signature is successful
        (err_cd, decrypted_data) = (wo_utility.
        decrypt_work_order_response(response, session_key, session_iv))

    if err_cd == TestStep.SUCCESS.value:
        logger.info('''Test Case Success : Work Order Processed successfully
                   with Signature Verification and Decrypted Response \n''')
    else:
        logger.info('''Test Case Failed : Work Order Not Processed successfully
                   with Signature Verification and Decrypted Response''')

    assert err_cd == TestStep.SUCCESS.value
