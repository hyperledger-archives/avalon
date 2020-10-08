#!/usr/bin/python3

# Copyright 2020 Intel Corporation
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

# -------------------------------------------------------------------------


def create_error_response(code, jrpc_id, msg):
    """
    Creates JSON RPC error response.

    Parameters :
        code: Error code
        jrpc_id: JSON RPC id
        msg: Error message
    Returns :
        JSON RPC error response as JSON object.
    """
    error_response = {}
    error_response["jsonrpc"] = "2.0"
    error_response["id"] = jrpc_id
    error_response["error"] = {}
    error_response["error"]["code"] = code
    error_response["error"]["message"] = msg
    return error_response

# -------------------------------------------------------------------------
