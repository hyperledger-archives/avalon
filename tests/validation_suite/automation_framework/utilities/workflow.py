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
import time
import json

from avalon_client_sdk.http_client.http_jrpc_client import HttpJrpcClient
from error_code.error_status import WorkOrderStatus
logger = logging.getLogger(__name__)


def submit_request(uri_client, input_json_str1, output_json_file_name):
    """ Function to submit request to Avalon listener,
    retrieve response and write files of input and output.
    Input Parameters : uri_client, input_json_str1, output_json_file_name
    Returns : response"""

    import json
    req_time = time.strftime("%Y%m%d_%H%M%S")
    input_json_str = json.dumps(input_json_str1)
    # write request to file
    signed_input_file = ('./results/' + output_json_file_name + '_' + req_time
                         + '_request.json')
    with open(signed_input_file, 'w') as req_file:
        req_file.write(json.dumps(input_json_str, ensure_ascii=False))
        # json.dump(input_json_str1, req_file)

    logger.info('**********Received Request*********\n%s\n', input_json_str)
    # submit request and retrieve response
    response = uri_client._postmsg(input_json_str)
    logger.info('**********Received Response*********\n%s\n', response)

    # write response to file
    response_output_file = ('./results/' + output_json_file_name + '_'
                            + req_time + '_response.json')
    with open(response_output_file, 'w') as resp_file:
        resp_file.write(json.dumps(response, ensure_ascii=False))

    return response


def check_for_variable_count(request_elements, keys_count=None):
    """
    Function to check the variable's count in request.
    """
    if keys_count:
        request_keys = sum(keys_count(elem) for elem in request_elements)
    return request_keys


def validate_response_code(response):
    """ Function to validate work order response.
        Input Parameters : response, check_result
        Returns : err_cd"""
    # check expected key of test case
    check_result = {"error": {"code": 5}}
    check_result_key = list(check_result.keys())[0]
    # check response code
    if check_result_key in response:
        if "code" in check_result[check_result_key].keys():
            if "code" in response[check_result_key].keys():
                if (response[check_result_key]["code"] ==
                        check_result[check_result_key]["code"]):
                    err_cd = 0
                    logger.info('SUCCESS: WorkOrderSubmit response'
                                ' key (%s) and status (%s)!!\
                                 \n', check_result_key,
                                check_result[check_result_key]["code"])
                elif (response[check_result_key]["code"] ==
                        WorkOrderStatus.INVALID_PARAMETER_FORMAT_OR_VALUE):
                    err_cd = 0
                    logger.info('Invalid parameter format in response "%s".',
                                response[check_result_key]["message"])
                elif (response[check_result_key]["code"] ==
                        WorkOrderStatus.SUCCESS):
                    err_cd = 0
                    logger.info('SUCCESS: Worker API response "%s"!!',
                                response[check_result_key]["message"])
                else:
                    err_cd = 1
                    logger.info('ERROR: Response did not contain expected \
                            %s code %s. \n', check_result_key,
                                check_result[check_result_key]["code"])
            else:
                err_cd = 1
                logger.info('ERROR: Response did not contain %s code \
                           where expected. \n', check_result_key)
    else:
        check_get_result = '''{"result": {"workOrderId": "", "workloadId": "",
                        "workerId": "", "requesterId": "", "workerNonce": "",
                               "workerSignature": "", "outData": ""}}'''

        check_result = json.loads(check_get_result)

        check_result_key = list(check_result.keys())[0]

        if check_result_key == "result":
            if (set(check_result["result"].keys()).issubset
               (response["result"].keys())):

                # Expected Keys : check_result["result"].keys()
                # Actual Keys : response["result"].keys()
                err_cd = 0
                logger.info('SUCCESS: WorkOrderGetResult '
                            'response has keys as expected!!')
            else:
                err_cd = 1
                logger.info('ERROR: Response did not contain keys \
                as expected in for test case. ')
        else:
            err_cd = 0
            logger.info('No validation performed for the expected result \
            in validate response. ')

    return err_cd
