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
import time
import json
import logging

from error_code.error_status import SignatureStatus
from automation_framework.utilities.workflow import process_request
from automation_framework.utilities.workflow import validate_response_code
from automation_framework.work_order_get_result.work_order_get_result_params \
                                                   import WorkOrderGetResult
import worker.worker_details as worker
from automation_framework.utilities.request_args import GetResultWaitTime

logger = logging.getLogger(__name__)

def process_work_order_get_result(input_request, input_type, tamper,
              output_json_file_name, uri_client, err_cd, work_order_id,
              request_id, check_get_result) :
    """ Function to process work order get result request.
    Uses WorkOrderGetResult class to initialize request object.
    Triggers process_request and validate_response_code
    Return err_cd, response."""

    logger.info("------ Testing WorkOrderGetResult ------")

    processing_time = ""

    if err_cd == 0 :
        if input_type == "object" :
            # process work order get result and retrieve response
            logger.info("----- Constructing WorkOrderGetResult -----")
            request_obj = WorkOrderGetResult()
            request_obj.set_work_order_id(work_order_id)
            request_obj.set_request_id(request_id)
            input_get_result = json.loads(request_obj.to_string())
        else :
            request_obj = WorkOrderGetResult()
            request_obj.set_work_order_id(work_order_id)
            request_obj.set_request_id(request_id)
            input_get_result = json.loads(request_obj.to_string())

        logger.info("----- Validating WorkOrderGetResult Response ------")
        response = {}

        response_timeout_start = time.time()
        response_timeout_multiplier = ((6000/3600) + 6) * 3
        while("result" not in response):
            if "error" in response:
                if response["error"]["code"] != 5:
                    logger.info('''WorkOrderGetResult -
                               Response received with error code. ''')
                    err_cd = 1
                    break

            response_timeout_end = time.time()
            if ((response_timeout_end - response_timeout_start) >
                (response_timeout_multiplier)):
                logger.info('''ERROR: WorkOrderGetResult response is not
                           received within expected time.''')
                break

            # submit work order get result request and retrieve response
            response = process_request(uri_client, input_get_result,
                       output_json_file_name)
            time.sleep (GetResultWaitTime.LOOP_WAIT_TIME.value)

        # validate work order get result code response error or result code
        err_cd = validate_response_code(response, check_get_result)

    else:
        logger.info('''ERROR: WorkOrderGetResult not performed -
                    Expected response not received for
                    WorkOrderSubmit.''')

    response_tup = (err_cd, response, processing_time)
    return response_tup
