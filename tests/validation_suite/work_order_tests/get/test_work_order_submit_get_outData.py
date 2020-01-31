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
from work_order_tests.work_order_tests import work_order_get_result_params, \
    work_order_request_params
from automation_framework.work_order_submit.work_order_submit_utility \
    import verify_work_order_signature, decrypt_work_order_response
from automation_framework.utilities.request_args import TestStep
from automation_framework.utilities.workflow import validate_response_code

logger = logging.getLogger(__name__)


def test_work_order_with_empty_indata_outdata(setup_config):
    """ Testing work order request by passing
     empty indata and outdata. """

    # input file name
    request = 'work_order_tests/input' \
              '/work_order_with_empty_indata_outdata.json'

    work_order_response, generic_params = (work_order_request_params
                                           (setup_config, request))
    err_cd, work_order_get_result_response = (work_order_get_result_params
                                              (work_order_response[:6],
                                               generic_params))

    # WorkOrderGetResult API Response validation with key parameters
    assert (validate_response_code(work_order_get_result_response) is
            TestStep.SUCCESS.value)
    logger.info('\t\t!!! Test completed !!!\n\n')
