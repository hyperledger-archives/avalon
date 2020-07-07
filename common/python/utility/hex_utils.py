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
import hashlib
import logging
import re

logger = logging.getLogger(__name__)

# Return list of binary hex ids as list of UTF strings


def pretty_ids(ids):
    pretty_list = []
    for id in ids:
        pretty_list.append(hex_to_utf8(id))
    return pretty_list


# Return binary hex as UTF string
def hex_to_utf8(binary):
    return binascii.hexlify(binary).decode("UTF-8")


def hex_to_byte_array(hex_str):
    """
    Convert a hex string (i.e., a string of characters with values
    between '0'-'9', 'A'-'F') to an array of bytes

    @param hex_str - hex string to be converted to bytearray
    @returns - array of bytes on successful conversion, otherwise return None
    """
    try:
        return bytearray(binascii.unhexlify(hex_str))
    except binascii.Error as err:
        logger.error(
            "Caught exception while converting hex string to bytearray - %s",
            err)
        return None
    except TypeError as err:
        logger.error(
            "Caught exception while converting hex string to bytearray - %s",
            err)
        return None


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
    except (ValueError, TypeError):
        # Throws TypeError for None else ValueError
        return False


def is_valid_hex_of_length(hex_str, length=None):
    """
    Function to check whether a string is a valid hex of specific length

    Parameter:
        @param hex_str - Input string to check
        @param length - Length of string; Default - None
    Returns:
        @returns True - If the string is valid
                        False, otherwise
    """
    if length is None:
        return is_valid_hex_str(hex_str)
    if not str(length).isdigit():
        logger.error("Non-negative integer expected as length.")
        return False
    pattern = re.compile("^(0[x|X])?[a-fA-F0-9]{"+str(length)+"}$")
    if pattern.match(hex_str) is None:
        return False
    return True


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


def get_worker_id_from_name(worker):
    """
    Converts a readable name string to a string of hex
    character which is 64 characters long.

    Parameters:
        @param worker - Plain text string representing name of worker
    Returns:
        @returns worker_id - 64 characters long hex str
    """
    # Calculate sha256 of worker id to get 32 bytes. The TC spec proxy
    # model contracts expect byte32. Then take a hexdigest for hex str.
    return hashlib.sha256(worker.encode("UTF-8")).hexdigest()
