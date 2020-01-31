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
from automation_framework.utilities.workflow import submit_request
from automation_framework.utilities.workflow import validate_response_code
from automation_framework.work_order_submit.work_order_submit_params \
    import WorkOrderSubmit
import crypto_utils.crypto_utility as enclave_helper
import crypto_utils.signature as signature

logger = logging.getLogger(__name__)


def submit_work_order(input_request, request_mode, tamper,
                      output_json_file_name,
                      uri_client, worker_obj,
                      request_method, private_key, err_cd):
    """ Function to submit work order
        Read input request from string or object and submit request.
        Uses WorkOrderSubmit class definition to initialize work order object.
        Triggers submit_request, validate_response_code,
        Returns - error code, input_json_str1, response,
        worker_obj, sig_obj, encrypted_session_key. """

    response = {}

    if err_cd == 0:
        # --------------------------------------------------------------------
        logger.info("------ Testing WorkOrderSubmit ------")

        if request_mode == "object":
            input_work_order = json.loads(input_request.to_string())
        else:
            # create work order request
            wo_obj = WorkOrderSubmit()
            wo_obj.add_json_values(input_request, worker_obj, private_key,
                                   tamper)
            input_work_order = wo_obj.compute_signature(tamper)
            logger.info('Compute Signature complete \n')

        input_json_str1 = json.loads(input_work_order)
        response = submit_request(uri_client, input_json_str1,
                                  output_json_file_name)
        err_cd = validate_response_code(response)

    else:
        logger.info('ERROR: No Worker Retrieved from system.\
                   Unable to proceed to submit work order.')

    response_tup = (err_cd, input_json_str1, response,
                    wo_obj.session_key, wo_obj.session_iv,
                    wo_obj.get_encrypted_session_key())

    return response_tup


def verify_work_order_signature(response, worker_obj):
    verify_key = worker_obj.verification_key

    try:
        verify_obj = signature.ClientSignature()
        sig_bool = verify_obj.verify_signature(response, verify_key)

        if sig_bool is SignatureStatus.PASSED:
            err_cd = 0
            logger.info('Success: Work Order Signature Verified.')
        else:
            err_cd = 1
            logger.info('ERROR: Work Order Signature Verification Failed')
    except Exception:
        err_cd = 1
        logger.error('ERROR: Failed to analyze Signature Verification')

    return err_cd


def decrypt_work_order_response(response, session_key, session_iv):
    decrypted_data = ""
    try:
        decrypted_data = enclave_helper.decrypted_response(response,
                                                           session_key,
                                                           session_iv)
        err_cd = 0
        logger.info('Success: Work Order Response Decrypted.\n\n')
    except Exception:
        err_cd = 1
        logger.info('ERROR: Work Order Response Decryption Failed')

    return err_cd, decrypted_data
