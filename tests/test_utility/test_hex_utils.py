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
    is_valid_hex_of_length,
    byte_array_to_hex_str,
    hex_to_utf8,
    hex_to_byte_array,
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

    def test_hex_to_byte_arrary(self):
        """
        Tests to verify hex_to_byte_array(hex_str) function
        """
        hex_str = "abcd1234"
        bin_hex = hex_to_byte_array(hex_str)
        self.assertEqual(bin_hex, b'\xab\xcd\x124')

        hex_str = "ccddba4321"
        bin_hex = hex_to_byte_array(hex_str)
        self.assertEqual(bin_hex, b'\xcc\xdd\xbaC!')

        hex_str = "aabb6789ccdd"
        bin_hex = hex_to_byte_array(hex_str)
        self.assertEqual(bin_hex, b'\xaa\xbbg\x89\xcc\xdd')

        # Negative test cases
        hex_str = "hello"
        bin_hex = hex_to_byte_array(hex_str)
        self.assertEqual(bin_hex, None)

        hex_str = None
        bin_hex = hex_to_byte_array(hex_str)
        self.assertEqual(bin_hex, None)

    def test_is_valid_hex_of_length(self):
        """Tests to verify is_valid_hex_of_length(hex_str, length) function
        """
        str = 'ase234cds'		# random input case
        self.assertFalse(is_valid_hex_of_length(str))

        str = 'aae234cdb'		# random input case
        self.assertTrue(is_valid_hex_of_length(str))
        self.assertFalse(is_valid_hex_of_length(str, 16))

        str = ''			# empty input case
        self.assertFalse(is_valid_hex_of_length(str))

        str = '0x'			# empty input case
        self.assertFalse(is_valid_hex_of_length(str))

        str = '0xae234cd'		# prepended by 0x
        self.assertTrue(is_valid_hex_of_length(str))
        self.assertFalse(is_valid_hex_of_length(str, 16))

        str = '0XAECD1234'		# prepended by 0X
        self.assertTrue(is_valid_hex_of_length(str))
        self.assertFalse(is_valid_hex_of_length(str, 16))

        str = '0x#aecd234'		# invalid character interpolated
        self.assertFalse(is_valid_hex_of_length(str))

        str = 'aecd0x234'		# 0x misplaced
        self.assertFalse(is_valid_hex_of_length(str))

        str = None              # None
        self.assertFalse(is_valid_hex_of_length(str))

        str = "0X12345ab"  # Positive case for length (<)
        self.assertFalse(is_valid_hex_of_length(str, 16))

        str = "0X12345abcde12345a"  # Positive case for length (==)
        self.assertTrue(is_valid_hex_of_length(str, 16))

        str = "0X12345abcde12345a"  # Positive case for length as string
        self.assertTrue(is_valid_hex_of_length(str, '16'))

        str = "0X12345abcde12345a"  # Negative case for length (>)
        self.assertFalse(is_valid_hex_of_length(str, 8))

        str = "0X12345abcde12345a"  # Negative case for inappropriate length
        self.assertFalse(is_valid_hex_of_length(str, -2))

        str = "0X12345abcde12345a"  # Negative case for inappropriate length
        self.assertFalse(is_valid_hex_of_length(str, "asdf"))

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

        str = None              # None
        self.assertFalse(is_valid_hex_str(str))

    def test_pretty_ids(self):
        """Tests to verify pretty_ids(ids) function
        """
        ids = [b'abec2c5f', b'\xab\xec\x2c\x5f']
        expected_pretty_ids = ["6162656332633566", "abec2c5f"]
        self.assertTrue(pretty_ids(ids) == expected_pretty_ids)
