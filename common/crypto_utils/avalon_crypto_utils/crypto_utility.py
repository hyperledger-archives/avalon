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
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from Cryptodome.Hash import SHA256
from ecdsa import SigningKey, SECP256k1

import logging

# 96 bits of randomness is recommended to prevent birthday attacks
IV_SIZE = 12
# Key size for authenticated encryption is 256 bits and tag size is 128 bits
KEY_SIZE = 32
TAG_SIZE = 16

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
def generate_signing_keys():
    """
    Function to generate private key object
    """
    return SigningKey.generate(curve=SECP256k1)


# -----------------------------------------------------------------------------
def get_verifying_key(private_key):
    """
    Function to return serialized verifying key from the private key
    """
    return private_key.get_verifying_key().to_pem().decode('ascii')


# -----------------------------------------------------------------
def generate_iv():
    """
    Function to generate random initialization vector
    """

    return get_random_bytes(IV_SIZE)


# -----------------------------------------------------------------
def generate_encrypted_key(key, encryption_key):
    """
    Function to generate session key for the client
    Parameters:
    - encryption_key is a one-time encryption used to encrypt the passed key
    - key that needs to be encrypted
    """
    pub_enc_key = RSA.importKey(encryption_key)
    # RSA encryption protocol according to PKCS#1 OAEP
    cipher = PKCS1_OAEP.new(pub_enc_key)
    return cipher.encrypt(key)


# -----------------------------------------------------------------
def generate_key():
    """
    Function to generate symmetric key
    """
    return get_random_bytes(KEY_SIZE)


# -----------------------------------------------------------------
def compute_data_hash(data):
    '''
    Computes SHA-256 hash of data
    '''
    data_hash = compute_message_hash(data.encode("UTF-8"))
    return data_hash


# -----------------------------------------------------------------
def encrypt_data(data, encryption_key, iv=None):
    """
    Function to encrypt data based on encryption key and iv
    Parameters:
        - data is each item in inData or outData part of workorder request
          as per Trusted Compute EEA API 6.1.7 Work Order Data Formats
        - encryption_key is the key used to encrypt the data
        - iv is an initialization vector if required by the data encryption
          algorithm.
          The default is all zeros.iv must be a unique random number for every
          encryption operation.
    """
    # Generate a random iv
    if iv is None:
        iv = get_random_bytes(IV_SIZE)
        generate_iv = True
        iv_length = IV_SIZE
    else:
        generate_iv = False
        iv_length = len(iv)
    cipher = AES.new(encryption_key, AES.MODE_GCM, iv)
    ciphered_data, tag = cipher.encrypt_and_digest(bytes(data))
    if generate_iv:
        # if iv passed by user is None, random iv generated
        # above is prepended in encrypted data
        # iv + Cipher + Tag
        result = iv + ciphered_data + tag
    else:
        # Cipher + Tag
        result = ciphered_data + tag
    return result


# -----------------------------------------------------------------
def decrypt_data(encryption_key, data, iv=None):
    """
    Function to decrypt the outData in the result
    Parameters:
        - encryption_key is the key used to decrypt the encrypted data of the
          response.
        - iv is an initialization vector if required by the data encryption
          algorithm.
          The default is all zeros.
        - data is the parameter data in outData part of workorder request as
          per Trusted Compute EEA API 6.1.7 Work Order Data Formats.
    Returns decrypted data as a string
    """
    if not data:
        logger.debug("Outdata is empty, nothing to decrypt")
        return data
    # if iv is None the it's assumed that 12 bytes iv is
    # prepended in encrypted data
    data_byte = base64_to_byte_array(data)
    if iv is None:
        iv_length = IV_SIZE
        iv = data_byte[:iv_length]
        data_contains_iv = True
    else:
        iv_length = len(iv)
        data_contains_iv = False

    cipher = AES.new(encryption_key, AES.MODE_GCM, iv)
    # Split data into iv, tag and ciphered data
    if data_contains_iv:
        ciphertext_len = len(data_byte) - iv_length - TAG_SIZE
        ciphered_data = data_byte[iv_length: iv_length + ciphertext_len]
        tag = data_byte[-TAG_SIZE:]
    else:
        ciphertext_len = len(data_byte) - TAG_SIZE
        ciphered_data = data_byte[: ciphertext_len]
        tag = data_byte[-TAG_SIZE:]

    result = cipher.decrypt_and_verify(ciphered_data, tag).decode("utf-8")
    logger.info("Decryption result at client - %s", result)
    return result


# -----------------------------------------------------------------------------
def decrypted_response(input_json, session_key, session_iv, data_key=None,
                       data_iv=None):
    """
    Function iterate through the out data items and decrypt the data using
    encryptedDataEncryptionKey and returns json object.
    Parameters:
        - input_json is a dictionary object containing the work order response
          payload
          as per Trusted Compute EEA API 6.1.2
        - session_key is the key used to decrypt the encrypted data of the
          response.
        - session_iv is an initialization vector corresponding to session_key.
        - data_key is a one time key generated by participant used to encrypt
          work order indata
        - data_iv is an initialization vector used along with data_key.
          Default is all zeros.
    returns out data json object in response after decrypting output data
    """
    i = 0
    do_decrypt = True
    data_objects = input_json['outData']
    for item in data_objects:
        data = item['data'].encode('UTF-8')
        iv = item['iv'].encode('UTF-8')
        e_key = item['encryptedDataEncryptionKey'].encode('UTF-8')
        if not e_key or (e_key == "null".encode('UTF-8')):
            data_encryption_key_byte = session_key
            iv = session_iv
        elif e_key == "-".encode('UTF-8'):
            do_decrypt = False
        else:
            data_encryption_key_byte = data_key
            iv = data_iv
        if not do_decrypt:
            input_json['outData'][i]['data'] = data
            logger.info(
                "Work order response data not encrypted, data in plain - %s",
                base64.b64decode(data).decode('UTF-8'))
        else:
            logger.debug("encrypted_key: %s", data_encryption_key_byte)
            # Decrypt output data
            data_in_plain = decrypt_data(
                    data_encryption_key_byte, item['data'], iv)
            input_json['outData'][i]['data'] = data_in_plain
        i = i + 1
    return input_json['outData']


# -----------------------------------------------------------------------------
def verify_data_hash(msg, data_hash):
    '''
    Function to verify data hash
    msg - Input text
    data_hash - hash of the data in hex format
    '''
    verify_success = True
    msg_hash = compute_data_hash(msg)
    # Convert both hash hex string values to upper case
    msg_hash_hex = hex_utils.byte_array_to_hex_str(msg_hash).upper()
    data_hash = data_hash.upper()
    if msg_hash_hex == data_hash:
        logger.info("Computed hash of message matched with data hash")
    else:
        logger.error("Computed hash of message does not match with data hash")
        verify_success = False
    return verify_success


# -----------------------------------------------------------------------------
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
def compute_message_hash(message_bytes):
    """
    Compute SHA256 hash of message_bytes.

    Parameters:
        message_bytes Data to hash
    Returns:
        binary hash of data
    """
    hash_obj = SHA256.new()
    hash_obj.update(message_bytes)
    return hash_obj.digest()


# -----------------------------------------------------------------------------
def base64_to_byte_array(b64_str):
    b64_arr = bytearray(b64_str, 'utf-8')
    b_arr = base64.b64decode(b64_arr)
    return b_arr


# -----------------------------------------------------------------------------
def byte_array_to_base64(byte_array):
    b_arr = bytearray(byte_array)
    b64_arr = base64.b64encode(b_arr)
    b64_str = str(b64_arr, 'utf-8')
    return b64_str
