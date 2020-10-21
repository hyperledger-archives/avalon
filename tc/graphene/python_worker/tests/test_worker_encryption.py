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
import sys
import logging
import avalon_crypto_utils.worker_encryption as worker_encryption

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))


# Test file for worker encryption class
def main(argv):

    encrypt = worker_encryption.WorkerEncrypt()

    # Test session key Encryption and Decryption
    encrypt.generate_rsa_key()
    worker_rsa_public_key = encrypt.get_rsa_public_key()
    logger.info("worker_rsa_public_key = {}".format(worker_rsa_public_key))

    session_key = encrypt.generate_session_key()
    encrypted_session_key = encrypt.encrypt_session_key(session_key)
    decrypted_session_key = encrypt.decrypt_session_key(encrypted_session_key)
    if session_key == decrypted_session_key:
        logger.info("Session key Encryption and Decryption Success")
    else:
        logger.error("Session key Encryption and Decryption Success")

    # Test Encryption and Decryption
    message = "Hello world"
    session_key = encrypt.generate_session_key()
    session_key_iv = encrypt.generate_iv()
    encrypt_msg_bytes = encrypt.encrypt_data(
        message.encode("utf-8"), session_key, session_key_iv)
    decrypt_message = encrypt.decrypt_data(
        encrypt_msg_bytes, session_key, session_key_iv)
    decrypt_message = decrypt_message.decode("utf-8")

    if message == decrypt_message:
        logger.info("Message Encryption and Decryption Success")
    else:
        logger.error("Message Encryption and Decryption Success")

    # Test inData Encryption and Decryption
    input_json = dict()
    input_json["jsonrpc"] = "2.0"
    input_json["method"] = "WorkOrderSubmit"
    input_json["id"] = "1"
    input_json["params"] = dict()

    inData = dict()
    inData["index"] = 0
    inData["dataHash"] = ""
    inData["data"] = message.encode("utf-8")
    inData["encryptedDataEncryptionKey"] = "null"
    inData["iv"] = ""
    input_json["params"]["inData"] = [inData]

    # Encrypt inData (will be done at client end)
    encrypt.encrypt_work_order_data_json(input_json["params"]["inData"],
                                         session_key, session_key_iv)
    # Decrypt inData
    encrypt.decrypt_work_order_data_json(input_json["params"]["inData"],
                                         session_key, session_key_iv)
    for item in input_json["params"]["inData"]:
        decrypted_data_bytes = item["data"]
        decrypted_data_str = decrypted_data_bytes.decode("UTF-8")
        logger.info("Decrypted data :{}".format(decrypted_data_str))

    if message == input_json["params"]["inData"][0]["data"].decode("UTF-8"):
        logger.info("inData Decryption Success")
    else:
        logger.error("inData Decryption Success")

    # Encrypt outData
    outData = inData
    out_message = "Received Hello world"
    outData["data"] = out_message.encode("UTF-8")
    input_json["params"]["outData"] = [outData]
    encrypt.encrypt_work_order_data_json(input_json["params"]["outData"],
                                         session_key, session_key_iv)

    # Decrypt outData (will be done at client end)
    encrypt.decrypt_work_order_data_json(input_json["params"]["outData"],
                                         session_key, session_key_iv)
    decrypted_out_bytes = input_json["params"]["outData"][0]["data"]
    decrypted_out_message = decrypted_out_bytes.decode("UTF-8")
    if out_message == decrypted_out_message:
        logger.info("outData Decryption Success")
    else:
        logger.error("outData Decryption Success")


if __name__ == '__main__':
    main(sys.argv[1:])
