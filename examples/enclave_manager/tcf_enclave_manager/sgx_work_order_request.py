# Copyright 2018 Intel Corporation
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
import os
import json
import logging

import crypto.crypto as crypto

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------
class SgxWorkOrderRequest(object):

    def __init__(self, enclave_service, work_order):
        self.enclave_service = enclave_service
        self.work_order = work_order

    # Execute work order in SGX worker enclave
    def execute(self):
        serialized_byte_array = crypto.string_to_byte_array(self.work_order)
        encrypted_request = crypto.byte_array_to_base64(serialized_byte_array)

        try:
            encoded_encrypted_response = self.enclave_service.send_to_sgx_worker(encrypted_request)
            assert encoded_encrypted_response
        except:
            logger.exception('workorder request invocation failed')
            raise

        try:
            decrypted_response = crypto.base64_to_byte_array(encoded_encrypted_response)
            response_string = crypto.byte_array_to_string(decrypted_response)
            response_parsed = json.loads(response_string[0:-1])
        except:
            logger.exception('workorder response is invalid')
            raise

        return response_parsed
