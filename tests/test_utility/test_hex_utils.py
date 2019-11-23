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
from utility.hex_utils import (
    byte_array_to_hex_str,
    hex_to_utf8,
    is_valid_hex_str,
    pretty_ids,
)


class HexUtilsTest(unittest.TestCase):
    def test_byte_array_to_hex_str(self):
        """Tests to verify byte_array_to_hex_str(in_byte_array) function
        """
        bytearr = b'teststring'  # positive case
        hexstr = byte_array_to_hex_str(bytearr)
        self.assertEqual(hexstr, "74657374737472696e67")

        bytearr = b''           # empty array case
        hexstr = byte_array_to_hex_str(bytearr)
        self.assertEqual(hexstr, "")

    def test_hex_to_utf8(self):
        """Tests to verify hex_to_utf8(binary) function
        """
        binhex = b'\xab\xec\x2c\x5f'    # random input case
        utfstr = hex_to_utf8(binhex)
        self.assertEqual(utfstr, "abec2c5f")

        binhex = b'abec2c5f'            # random input case
        utfstr = hex_to_utf8(binhex)
        self.assertEqual(utfstr, "6162656332633566")

        binhex = b''                    # empty input case
        utfstr = hex_to_utf8(binhex)
        self.assertEqual(utfstr, "")

    def test_is_valid_hex_str(self):
        """Tests to verify is_valid_hex_str(hex_str) function
        """
        str = 'ase234cds'		# random input case
        self.assertFalse(is_valid_hex_str(str))

        str = 'aae234cdb'		# random input case
        self.assertTrue(is_valid_hex_str(str))

        str = ''			# empty input case
        self.assertFalse(is_valid_hex_str(str))

        str = '0x'			# empty input case
        self.assertFalse(is_valid_hex_str(str))

        str = '0xae234cd'		# prepended by 0x
        self.assertTrue(is_valid_hex_str(str))

        str = '0XAECD1234'		# prepended by 0X
        self.assertTrue(is_valid_hex_str(str))

        str = '0x#aecd234'		# invalid character interpolated
        self.assertFalse(is_valid_hex_str(str))

        str = 'aecd0x234'		# 0x misplaced
        self.assertFalse(is_valid_hex_str(str))

    def test_pretty_ids(self):
        """Tests to verify pretty_ids(ids) function
        """
        ids = [b'abec2c5f', b'\xab\xec\x2c\x5f']
        expected_pretty_ids = ["6162656332633566", "abec2c5f"]
        self.assertTrue(pretty_ids(ids) == expected_pretty_ids)
