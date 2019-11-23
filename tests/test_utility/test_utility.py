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
from utility.utility import (
    create_error_response,
    strip_begin_end_key,
    list_difference,
    encrypt_data,
    decrypt_data,
    decrypted_response,
    verify_data_hash,
    human_read_to_byte,
)


class UtilityTest(unittest.TestCase):
    def test_create_error_response(self):
        """Tests to verify create_error_response(code, jrpc_id, message) function
        """
        expected_response = {"jsonrpc": "2.0", "id": "id1",
            "error": {"code": 404, "message": "Page not found"}, }
        self.assertEquals(expected_response, create_error_response(404, "id1", "Page not found"))

        expected_response = {"jsonrpc": "2.0", "id": "id2",
             "error": {"code": "2", "message": "General error"}, }
        self.assertEquals(expected_response, create_error_response("2", "id2",
             "General error"))

    def test_strip_begin_end_key(self):
        """Tests to verify strip_begin_end_key(key) function
        """
        expected = "123456aghdfgasdasdkommkf"       # Positive case
        self.assertEquals(expected, strip_begin_end_key(
            "-----BEGIN PUBLIC KEY-----123456aghdfgas\n"
            "dasdkommkf-----END PUBLIC KEY-----"))

        expected = "123456aghdfgasdasdkommkf"       # Interspersed with '\n'
        self.assertEquals(expected, strip_begin_end_key(
            "\n-----BEGIN PUBLIC KEY\n"
            "-----123456aghdfgas\n"
            "dasdkommkf\n"
            "-----END PUBLIC KEY-----\n"))

        expected = "123456+/aghdfgasdasdkommkf==="  # Other base64 characters
        self.assertEquals(expected, strip_begin_end_key(
            "-----BEGIN PUBLIC KEY-----123456+/aghdfgasdasdkommkf==="
            "-----END PUBLIC KEY-----"))

    def test_list_difference(self):
        """Tests to verify list_difference(list_1, list_2) function
        """
        expected = [1, 3, 5, 7, 9]
        list1 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        list2 = [2, 4, 6, 8]
        self.assertEquals(expected, list_difference(list1, list2))

        list1 = [1, 3, 5, 7, 9]
        list2 = [2, 4, 6, 8]
        self.assertEquals(expected, list_difference(list1, list2))

        expected = []
        list1 = [1, 3, 5, 7, 9]
        list2 = [1, 3, 5, 7, 9]
        self.assertEquals(expected, list_difference(list1, list2))

        expected = []
        list1 = []
        list2 = [1, 3, 5, 7, 9]
        self.assertEquals(expected, list_difference(list1, list2))

        expected = []
        list1 = []
        list2 = []
        self.assertEquals(expected, list_difference(list1, list2))

    def test_human_read_to_byte(self):
        """Tests to verify human_read_to_byte(size) function
        """
        self.assertRaises(Exception, human_read_to_byte, "1KB")

        expected = 1024
        self.assertEquals(expected, human_read_to_byte("1 KB"))

        expected = 4096
        self.assertEquals(expected, human_read_to_byte("4 KB"))

        expected = 10240000
        self.assertEquals(expected, human_read_to_byte("10000 KB"))

        expected = 10240
        self.assertEquals(expected, human_read_to_byte("10 kb"))

        self.assertRaises(Exception, human_read_to_byte, "1 MD")
