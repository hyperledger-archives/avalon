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
utility.py -- general helper function
"""
import base64
import os
import json
import utility.file_utils as putils
import crypto.crypto as crypto
import config.config as pconfig
import logging
import toml

logger = logging.getLogger(__name__)

TCFHOME = os.environ.get("TCF_HOME", "../../")
# No of bytes of encrypted session key to encrypt data
NO_OF_BYTES = 16

def read_toml_file(input_file, config_name = None, confpaths = [".", TCFHOME + "/" + "config"]):
    """
    Function to read toml file and returns the toml content as a list
    Parameters:
        - input_file is any toml file which need to be read
        - config_name is particular configuration to pull
        - data_dir is the directory structure in which the toml file exists
    """
    conffiles = [input_file]
    config = pconfig.parse_configuration_files(conffiles, confpaths)
    if config_name is None:
        return config
    else :
        result = config.get(config_name)
        if result is None:
            logger.error("%s is missing in toml file %s", config_name, input_file )
            return None
        else :
            return result

#---------------------------------------------------------------------------------------------
def read_json_file(input_file, data_dir = ['./', '../', '/']) :
    """
    Function to read json file and returns the json content as a string
    Parameters:
        - input_file is any json file which need to be read
        - data_dir is the directory structure in which the json file exists
    """

    file_name = putils.find_file_in_path(input_file, data_dir)
    with open(file_name, "r") as input_json_file :
        input_json = input_json_file.read()
    return input_json

#---------------------------------------------------------------------------------------------
def write_json_file(file_name,input_data, data_dir ='./') :
    """
    Function to store data as json file
    Parameters:
        - file_name is the name in which the file should be stored
        - input_data is any data which needs to be stored in a file
        - data_dir is the directory path to store the file
    """

    logger.debug('Data file is stored at %s with name %s.json',data_dir, file_name)
    result_info = dict()
    result_info['Result'] = input_data.result
    filename = os.path.realpath(os.path.join(data_dir, file_name + ".json"))
    logger.debug('save result data to %s', filename)
    with open(filename, "w") as file :
        json.dump(result_info, file)

#---------------------------------------------------------------------------------------------
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

#---------------------------------------------------------------------------------------------
def strip_begin_end_key(key) :
    """
    Strips off newline chars, BEGIN PUBLIC KEY and END PUBLIC KEY.
    """
    return key.replace("\n", "")\
            .replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "")

#---------------------------------------------------------------------------------------------
def generate_signing_keys():
    """
    Function to generate private key object
    """

    signing_key = crypto.SIG_PrivateKey()
    signing_key.Generate()
    return signing_key

#---------------------------------------------------------------------------------------------
def generate_iv():
    """
    Function to generate random initialization vector
    """

    return crypto.SKENC_GenerateIV()

#---------------------------------------------------------------------------------------------
def generate_encrypted_key(key, encryption_key):
    """
    Function to generate session key for the client
    Parameters:
    - encryption_key is a one-time encryption used to encrypt the passed key
    - key that needs to be encrypted
    """

    pub_enc_key = crypto.PKENC_PublicKey(encryption_key)
    return pub_enc_key.EncryptMessage(key)

#-----------------------------------------------------------------
def generate_key():
    """
    Function to generate symmetric key
    """
    return crypto.SKENC_GenerateKey()

# -----------------------------------------------------------------
def list_difference(list_1, list_2):
    """
    Function to generate find the difference between two list. Result is list1 - list2
    Parameters:
    - list_1 / list_2 any list of integers.
    """
    list_dif = [i for i in list_1 + list_2 if i not in list_2]
    return list_dif
# -----------------------------------------------------------------
def encrypt_data(data, encryption_key, iv=None):
    """
    Function to encrypt data based on encryption key and iv
    Parameters:
        - data is each item in inData or outData part of workorder request
          as per TCF API 6.1.7 Work Order Data Formats
        - encryption_key is the key used to encrypt the data
        - iv is an initialization vector if required by the data encryption algorithm.
          The default is all zeros.iv must be a unique random number for every
          encryption operation.
    """
    logger.debug("encrypted_session_key: %s", encryption_key)
    if iv is not None:
        encrypted_data = crypto.SKENC_EncryptMessage(encryption_key, iv, data)
    else:
        encrypted_data = crypto.SKENC_EncryptMessage(encryption_key, data)
    return encrypted_data

# -----------------------------------------------------------------
def decrypt_data(encryption_key, data, iv=None):
    """
    Function to decrypt the outData in the result
    Parameters:
        - encryption_key is the key used to decrypt the encrypted data of response.
        - iv is an initialization vector if required by the data encryption algorithm.
          The default is all zeros.
        - data is the parameter data in outData part of workorder request as per
          TCF API 6.1.7 Work Order Data Formats
    Returns decrypted data as a string
    """
    if not data:
        logger.debug("Outdata is empty, nothing to decrypt")
        return data
    data_byte = crypto.base64_to_byte_array(data)
    logger.debug("encryption_key: %s", encryption_key)
    if iv is not None:
        decrypt_result = crypto.SKENC_DecryptMessage(encryption_key,
                             iv, data_byte)
    else:
        decrypt_result = crypto.SKENC_DecryptMessage(encryption_key, data_byte)
    result = crypto.byte_array_to_string(decrypt_result)
    logger.info("Decryption result at client - %s", result)
    return result

#---------------------------------------------------------------------------------------------

def decrypted_response(input_json_str, session_key, session_iv, data_key=None, data_iv=None):
    """
    Function iterate through the out data items and decrypt the data using
    encryptedDataEncryptionKey and returns json object.
    Parameters:
        - input_json_params is a collection of parameters as per TCF API 6.1.2
          Work Order Response Payload
        - session_key is the key used to decrypt the encrypted data of response.
        - session_iv is an initialization vector corresponding to session_key.
        - data_key is a one time key generated by participant used to encrypt
          work order indata
        - data_iv is an initialization vector used along with data_key.
          Default is all zeros.
    returns out data json object in response after decrypting output data
    """
    input_json = json.loads(input_json_str)
    input_json_params = input_json['result']
    i = 0
    do_decrypt = True
    data_objects = input_json_params['outData']
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
            input_json_params['outData'][i]['data'] = data
            logger.debug("Work order response data not encrypted, data in plain is %s",
                base64.b64decode(data))
        else:
            logger.debug("encrypted_key: %s", data_encryption_key_byte)
            # Decrypt output data
            data_in_plain = decrypt_data(
                    data_encryption_key_byte, item['data'], iv)
            input_json_params['outData'][i]['data'] = data_in_plain
        i = i + 1
    return input_json_params['outData']

#---------------------------------------------------------------------------------------------

def human_read_to_byte(size):
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    size = size.split() # divide '1 GB' into ['1', 'GB']
    if len(size) !=2 or int(size[0]) <= 0:
        raise Exception("Invalid size")
    num, unit = int(size[0]), size[1]
    idx = size_name.index(unit)
    factor = 1024 ** idx
    return num * factor
