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

import logging
import avalon_crypto_utils.crypto.crypto as crypto
import avalon_crypto_utils.crypto_utility as crypto_utility

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def test_encrypt_session_key(iv):
    worker_enc_key = "MIIBCgKCAQEAwocGo"
    enc_sess_key = \
        crypto_utility.generate_encrypted_session_key(iv, worker_enc_key)
    if enc_sess_key:
        logging.info("Test case: test_encrypt_session_key PASS...")
    else:
        logging.info("Test case: test_encrypt_session_key FAIL...")
    return enc_sess_key


def test_encrypt_data(iv, enc_sess_key, data):
    data_bytes = bytes(data, 'ascii')
    enc_req_hash = crypto_utility.encrypt_data(data_bytes, enc_sess_key, iv)
    if enc_req_hash:
        logging.info("Test case: test_encrypt_data PASS...")
    else:
        logging.info("Test case: test_encrypt_data FAIL...")
    return enc_req_hash


def test_decrypt_data(iv, enc_sess_key, plain_data, enc_data):
    dec_data = crypto_utility.decrypt_data(enc_sess_key, iv, enc_data)
    if dec_data == plain_data:
        logging.info("Test case: test_decrypt_data PASS..")
    else:
        logging.info("Test case: test_decrypt_data FAIL..")


def main():
    logging.info("Executing Unit test cases for encryption at client")
    msg = "This is client request"
    iv = crypto_utility.generate_sessioniv()
    enc_sess_key = test_encrypt_session_key(iv)
    if enc_sess_key:
        enc_data = test_encrypt_data(iv, enc_sess_key[:16], msg)
        if enc_data:
            b64_enc_data = crypto.byte_array_to_base64(enc_data)
            iv_hex = crypto.byte_array_to_hex(iv)
            test_decrypt_data(iv_hex, enc_sess_key[:16], msg, b64_enc_data)
    logging.info(
        "Unit test case execution for encryption/decryption complete.")


if __name__ == "__main__":
    main()
