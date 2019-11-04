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

import worker.worker_details as worker
from automation_framework.utilities.process_api_request import \
                                    process_api_request
from automation_framework.utilities.request_args import TestStep

logger = logging.getLogger(__name__)

def test_worker_update(setup_config):
    """ Testing worker update request with all valid parameter values. """

    # retrieve values from conftest session fixture
    worker_obj = setup_config[0]
    uri_client = setup_config[1]
    private_key = setup_config[2]
    err_cd = setup_config[3]

    # input and output names
    input_json_file = './worker_tests/input/worker_update.json'
    input_type = 'file'
    output_json_file_name = 'worker_update'
    tamper = {"params": {}}
    request_method = ""
    request_id = 0

    # expected response
    check_update_result = {"error": {"code": 0}}

    # process worker update
    request_tup = (input_json_file, input_type, tamper, output_json_file_name,
                   uri_client, request_method, worker_obj,
                   request_id, check_update_result)

    response_tup = process_api_request(request_tup)

    err_cd = response_tup[0]
    input_update = response_tup[1]
    response = response_tup[2]

    if err_cd == TestStep.SUCCESS.value:
        logger.info('''Test Case Success : Worker Update request
                    Processed successfully \n''')
    else:
        logger.info('''Test Case Failure : Worker Update request
                    failed to process successfully \n''')

    assert err_cd == TestStep.SUCCESS.value

def test_worker_update_invalid_parameter(setup_config):
    """ Testing worker update request with all valid parameter values. """

    # retrieve values from conftest session fixture
    worker_obj = setup_config[0]
    uri_client = setup_config[1]
    private_key = setup_config[2]
    err_cd = setup_config[3]

    # input and output names
    input_json_file = './worker_tests/input/worker_update_invalid_parameter.json'
    input_type = 'file'
    output_json_file_name = 'worker_update_invalid_parameter'
    tamper = {"params": {}}
    request_method = ""
    request_id = 0

    # expected response
    check_update_result = {"error": {"code": 2}}

    # process worker update
    request_tup = (input_json_file, input_type, tamper, output_json_file_name,
                   uri_client, request_method, worker_obj,
                   request_id, check_update_result)

    response_tup = process_api_request(request_tup)

    err_cd = response_tup[0]
    input_update = response_tup[1]
    response = response_tup[2]

    if err_cd == TestStep.SUCCESS.value:
        logger.info('''Test Case Success : Worker Update request
                    Processed successfully \n''')
    else:
        logger.info('''Test Case Failure : Worker Update request
                    failed to process successfully \n''')

    assert err_cd == TestStep.SUCCESS.value

def test_worker_update_unknown_parameter(setup_config):
    """ Testing worker update request with all valid parameter values. """

    # retrieve values from conftest session fixture
    worker_obj = setup_config[0]
    uri_client = setup_config[1]
    private_key = setup_config[2]
    err_cd = setup_config[3]

    # input and output names
    input_json_file = './worker_tests/input/worker_update.json'
    input_type = 'file'
    output_json_file_name = 'worker_update_unknown_parameter'
    tamper = {"params": {"details": {"name": "TEST"}}}
    request_method = ""
    request_id = 0

    # expected response
    check_update_result = {"error": {"code": 2}}

    # process worker update
    request_tup = (input_json_file, input_type, tamper, output_json_file_name,
                   uri_client, request_method, worker_obj,
                   request_id, check_update_result)

    response_tup = process_api_request(request_tup)

    err_cd = response_tup[0]
    input_update = response_tup[1]
    response = response_tup[2]

    if err_cd == TestStep.SUCCESS.value:
        logger.info('''Test Case Success : Worker Update request
                    Processed successfully \n''')
    else:
        logger.info('''Test Case Failure : Worker Update request
                    failed to process successfully \n''')

    assert err_cd == TestStep.SUCCESS.value
