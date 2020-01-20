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
# ------------------------------------------------------------------------------

import unittest
from utility.jrpc_utility import (
    create_error_response,
)


class UtilityTest(unittest.TestCase):
    def test_create_error_response(self):
        """Tests to verify create_error_response(code, jrpc_id, message) function
        """
        expected_response = {
            "jsonrpc": "2.0", "id": "id1",
            "error": {"code": 404, "message": "Page not found"}, }
        self.assertEquals(expected_response, create_error_response(
            404, "id1", "Page not found"))

        expected_response = {"jsonrpc": "2.0", "id": "id2",
                             "error":
                             {"code": "2", "message": "General error"}, }
        self.assertEquals(expected_response, create_error_response("2", "id2",
                          "General error"))
