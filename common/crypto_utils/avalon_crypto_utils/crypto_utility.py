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

import base64
import utility.hex_utils as hex_utils
import secrets
import string

import logging

logger = logging.getLogger(__name__)


def strip_begin_end_public_key(key):
    """
    Strips off newline chars, BEGIN PUBLIC KEY and END PUBLIC KEY.
    """
    return key.replace("\n", "")\
        .replace("-----BEGIN PUBLIC KEY-----", "").replace(
        "-----END PUBLIC KEY-----", "")


# -----------------------------------------------------------------------------
def byte_array_to_hex(byte_array):
    hex_value = hex_utils.byte_array_to_hex_str(byte_array)
    return hex_value.upper()


# -----------------------------------------------------------------------------
def string_to_byte_array(in_str):
    return bytearray(in_str, 'utf-8')


# -----------------------------------------------------------------------------
def byte_array_to_string(byte_array):
    return byte_array.decode('utf-8')


# -------------------------------------------------------------------------

def base64_to_byte_array(b64_str):
    """
    Decode Base64 string to bytes.

    Parameters :
        b64_str: Base64 encoded string
    Returns :
        base64 decoded data in bytes.
    """
    try:
        b64_bytes = b64_str.encode('UTF-8')
        b64_dec_bytes = base64.b64decode(b64_bytes)
        return b64_dec_bytes
    except Exception as e:
        err_msg = "base64 string decode to byte array failed: " + str(e)
        logger.error(err_msg)
        raise


# -------------------------------------------------------------------------
def byte_array_to_base64(data_bytes):
    """
    Converts bytes to Base64 encoded string.

    Parameters :
        data_bytes: data to be encoded in bytes
    Returns :
        Base64 encoded string.
    """
    try:
        b64 = base64.b64encode(data_bytes)
        b64_str = b64.decode('UTF-8')
        return b64_str
    except Exception as e:
        err_msg = "byte array to base64 encode string failed: " + str(e)
        logger.error(err_msg)
        raise


# -----------------------------------------------------------------------------
def generate_random_string(num_of_bytes):
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                   for i in range(num_of_bytes))
