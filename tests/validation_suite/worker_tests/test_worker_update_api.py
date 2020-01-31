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
from automation_framework.utilities.request_args import TestStep
from automation_framework.utilities.workflow import validate_response_code

logger = logging.getLogger(__name__)


def test_worker_update(setup_config):
    """ Testing worker update request with all valid parameter values. """

    # retrieve values from conftest session fixture
    worker_obj, uri_client, private_key, err_cd = setup_config[:4]

    # input and output names
    request = './worker_tests/input/worker_update.json'
    request_mode = 'file'
    output_json_file_name = 'worker_update'
    tamper = {"params": {}}
    request_method = ""
    request_id = 0

    # submit worker update
    request_tup = (request, request_mode, tamper, output_json_file_name,
                   uri_client, request_method, worker_obj,
                   request_id)

    response_tup = post_request(request_tup)

    response = response_tup[1]

    # validate work order response and get error code
    err_cd = validate_response_code(response)

    assert err_cd == TestStep.SUCCESS.value
    logger.info('\t\t!!! Test completed !!!\n\n')
