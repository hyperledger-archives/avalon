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
from service_client.generic import GenericServiceClient

logger = logging.getLogger(__name__)

def process_request(uri_client, input_json_str1, output_json_file_name) :
    """ Function to submit request to enclave,
    retrieve response and write files of input and output.
    Input Parameters : uri_client, input_json_str1, output_json_file_name
    Returns : response"""

    import json
    req_time = time.strftime("%Y%m%d_%H%M%S")
    input_json_str = json.dumps(input_json_str1)
    # write request to file
    signed_input_file = ('./results/' + output_json_file_name + '_'+ req_time
                        + '_request.json')
    with open(signed_input_file, 'w') as req_file:
        req_file.write(json.dumps(input_json_str, ensure_ascii=False))
        # json.dump(input_json_str1, req_file)

    logger.info("**********Received Request*********\n%s\n", input_json_str)
    # submit request and retrieve response
    response = uri_client._postmsg(input_json_str)
    logger.info("**********Received Response*********\n%s\n", response)

    # write response to file
    response_output_file = ('./results/' + output_json_file_name + '_'+ req_time
                           + '_response.json')
    with open(response_output_file, 'w') as resp_file:
        resp_file.write(json.dumps(response, ensure_ascii=False))

    return response

def validate_response_code(response, check_result):
    """ Function to validate work order response.
        Input Parameters : response, check_result
        Returns : err_cd"""

    # check expected key of test case
    check_result_key = list(check_result.keys())[0]
    logger.info('''check_result_key in expected result: %s \n ''',
               check_result_key)

    # check response code
    if check_result_key in response:
        if "code" in check_result[check_result_key].keys():
            if "code" in response[check_result_key].keys():
                if (response[check_result_key]["code"] ==
                check_result[check_result_key]["code"]) :
                    err_cd = 0
                    logger.info('''SUCCESS: Response contains expected %s code
                               %s. \n''', check_result_key,
                               check_result[check_result_key]["code"])
                else:
                    err_cd = 1
                    logger.info('''ERROR: Response did not contain expected
                            %s code %s. \n''', check_result_key,
                            check_result[check_result_key]["code"])
            else:
                err_cd = 1
                logger.info('''ERROR: Response did not contain %s code
                           where expected. \n''', check_result_key)
        else:
            if check_result_key == "result" :
                if (set(check_result["result"].keys()).issubset
                (response["result"].keys())):
                    logger.info(''' Expected Keys in response: %s \n ''',
                               check_result["result"].keys())
                    logger.info(''' Actual Keys in response: %s \n ''',
                               response["result"].keys())
                    err_cd = 0
                    logger.info('''SUCCESS: Response has keys as expected
                    for test case. ''')
                else:
                    err_cd = 1
                    logger.info('''ERROR: Response did not contain keys
                    as expected in for test case. ''')
            else:
                err_cd = 0
                logger.info('''No validation performed for the expected result
                in validate response. ''')
    else:
        err_cd = 1
        logger.info('''ERROR: Response did not contain %s in expected response.
                   \n ''', check_result_key)

    return err_cd
