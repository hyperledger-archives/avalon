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

"""
jrpc_utility.py -- general jrpc helper function
"""


def create_error_response(code, jrpc_id, message):
    """
    Function to create error response
    Parameters:
        - code: error code enum which corresponds to error response
        - jrpc_id: JRPC id of the error response
        - message: error message which corresponds to error response
    """
    error_response = {}
    error_response["jsonrpc"] = "2.0"
    error_response["id"] = jrpc_id
    error_response["error"] = {}
    error_response["error"]["code"] = code
    error_response["error"]["message"] = message
    return error_response
