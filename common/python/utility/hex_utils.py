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

import binascii


# Return list of binary hex ids as list of UTF strings
def pretty_ids(ids):
    pretty_list = []
    for id in ids:
        pretty_list.append(hex_to_utf8(id))
    return pretty_list


# Return binary hex as UTF string
def hex_to_utf8(binary):
    return binascii.hexlify(binary).decode("UTF-8")


def is_valid_hex_str(hex_str):
    """
    Function to check given string is valid hex string or not
    Parameter
        - hex_str is string
    Returns True if valid hex string otherwise False
    """
    try:
        int(hex_str, 16)
        return True
    except ValueError:
        return False


def mrenclave_hex_string(enclave_metadata_file):
    """
    Function to extract the MREnclave value from a file
    Parameter
        - enclave_metadata_file is a file
    Returns MRENCALVE value converted to hex string
    """
    with open(enclave_metadata_file, "r") as file:
        hexlist = file.read().rstrip('\r\n ').split(' ')
        hexbytes = bytes([int(x, 0) for x in hexlist])
        hexstring = hexbytes.hex()
    return hexstring


def byte_array_to_hex_str(in_byte_array):
    '''
    Converts tuple of bytes to hex string
    '''
    return ''.join(format(i, '02x') for i in in_byte_array)
