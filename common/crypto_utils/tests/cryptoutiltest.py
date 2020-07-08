#!/usr/bin/env python3

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

# Test crypto utilities in crypto_utility.py
# To run: "python cryptoutiltest.py"

import logging
import avalon_crypto_utils.crypto_utility as crypto_utility

logging.basicConfig(format='%(message)s', level=logging.INFO)

rsa_public_key = "-----BEGIN PUBLIC KEY-----\n"\
    "MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAviXPKQtoVclvf18iWD1c\n"\
    "m6xiNei4pl+m6EpMb9RM2S++/iC1ex7irJWjamFiWsVfh8xsFhByq/suH1vvGWnH\n"\
    "oPGrCNNfTjlt6r9mCKHbVMbZ0eTW2TVGJqfdJHWqAd6CVQB0RPdN4nXJ/zzr4/j7\n"\
    "0wm7vCqEtsIFo6yJsqX5ac8AFUb9rO/OXlVG9a076Jwqm7Lzod3SVX0FTC2LDI6I\n"\
    "/CK0blOX4gAPS/8jfpZYPHFQbXERCo0PwgXXJZJ2EWXDlhVIFYgfKiFITlXljIoM\n"\
    "8xp1HC9F+LhsKwK0GUVfU7D7kYEVNmV7dWHsQPWbae2BPSmR/w8tSDQDsDeffgOf\n"\
    "/OxXUsqWdi83EKqe/xsCkaseujjvKxtkwm/MzMhZMb36piyfBoHUjUqwSgh23jEK\n"\
    "D7NjawxG/zuji1+w8a6qt9P4uXzc44jIG4stYcoD+/UF6Jh6teWMnWyYLfcTf2Ec\n"\
    "gEwdXQbJCl8z1p2N5eVHPZSh7lVD0euOIhhJRVwNWHVnoR4GALIgLOkqECV3RSjZ\n"\
    "gTVuC8crfJBUt+zOpiXUv8DaD+kVdAdDdZlgHBW2K9gcivXDegAz84WPbhDrQ3CM\n"\
    "M9SJ22B99CR1eG/ez/wzY0GiAZOCIB31IWk34Ehc8tTKjm8fVnXWvYJnXKxACnYd\n"\
    "3isoueUA1x01+U0HDnY5ZR0CAwEAAQ==\n"\
    "-----END PUBLIC KEY-----\n"

b64_test_cases = [
    {"plain": "Hyperledger Avalon", "encoded": "SHlwZXJsZWRnZXIgQXZhbG9u"},
    {"plain": "Hyperledger", "encoded": "SHlwZXJsZWRnZXI="},
    {"plain": "Hype", "encoded": "SHlwZQ=="},
    {"plain": "H", "encoded": "SA=="},
    {"plain": "", "encoded": ""}
]

hash_test_cases = [
    {"plain": "Hyperledger Avalon",
        "encoded": "22hKjT4z7yvB8D3Ros2/QykiYzXwkJIfJO89Df5xOtQ="},
    {"plain": "",
        "encoded": "47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU="}
]

outdata_0 = {
    'index': 0,
    'dataHash': "",
    'data': "",
    'encryptedDataEncryptionKey': "",
    'iv': ""
}


# -----------------------------------------------------------------------------
def test_generate_signing_keys():
    try:
        private_key = crypto_utility.generate_signing_keys()
        logging.info("PASSED: generate_signing_keys()")
        return 0, private_key
    except Exception as err:
        logging.info("FAILED: generate_signing_keys()")
        return 1, None


# -----------------------------------------------------------------------------
def test_get_verifying_key(private_key):
    err_cnt = 0
    try:
        public_key = crypto_utility.get_verifying_key(private_key)
        logging.info("PASSED: get_verifying_key()")

        # must begin with BEGIN PUBLIC KEY LINE
        if public_key.find("-----BEGIN PUBLIC KEY-----") != 0:
            logging.info("FAILED: BEGIN PUBLIC KEY header line test")
            err_cnt += 1
        else:
            logging.info("PASSED: BEGIN PUBLIC KEY header line test")

        return err_cnt, public_key
    except Exception as err:
        logging.info("FAILED: get_verifying_key()")
        return 1, None


# -----------------------------------------------------------------------------
def test_strip_begin_end_public_key(public_key):
    try:
        stripped = crypto_utility.strip_begin_end_public_key(public_key)
        if ("-----BEGIN PUBLIC KEY-----" in stripped) or \
                ("-----END PUBLIC KEY-----" in stripped) or ("\n" in stripped):
            logging.info("FAILED: strip_begin_end_public_key()")
            return 1
        else:
            logging.info("PASSED: strip_begin_end_public_key()")
            return 0
    except Exception as err:
        logging.info("FAILED: strip_begin_end_public_key()")
        return 1


# -----------------------------------------------------------------------------
def test_generate_iv():
    try:
        iv = crypto_utility.generate_iv()
        logging.info("PASSED: generate_iv()")
        return 0, iv
    except Exception as err:
        logging.info("FAILED: generate_iv()")
        return 1, None


# -----------------------------------------------------------------------------
def test_generate_key():
    try:
        enc_key = crypto_utility.generate_key()
        logging.info("PASSED: generate_key()")
        return 0, enc_key
    except Exception as err:
        logging.info("FAILED: generate_key()")
        return 1, None


# -----------------------------------------------------------------------------
def test_byte_array_to_hex():
    b_arr = b'teststring'
    hex_str = crypto_utility.byte_array_to_hex(b_arr)

    if hex_str == "74657374737472696E67":
        logging.info("PASSED: byte_array_to_hex()")
        return 0
    else:
        logging.info("FAILED: byte_array_to_hex()")
        return 1


# -----------------------------------------------------------------------------
def test_generate_random_string():
    rand_length = 32
    try:
        rand_string = crypto_utility.generate_random_string(rand_length)
        logging.info("PASSED: generate_random_string()")
        return 0
    except Exception as err:
        logging.info("FAILED: generate_random_string()")
        return 1


# -----------------------------------------------------------------------------
def test_encode():
    err_cnt = 0

    logging.info("Testing avalon encode...")

    for i in range(len(b64_test_cases)):

        encoded = b64_test_cases[i]["encoded"]
        plain_txt = b64_test_cases[i]["plain"]

        b_arr = crypto_utility.string_to_byte_array(plain_txt)
        b64hash = crypto_utility.byte_array_to_base64(b_arr)

        if b64hash != encoded:
            logging.info("FAILED: plain: %s" % plain_txt)
            logging.info("         expected encoded %s" % encoded)
            logging.info("         actual result: %s" % b64hash)
            err_cnt += c1
        else:
            logging.info("PASSED: %s --> %s, length %u --> len %lu"
                         % (plain_txt, b64hash, len(plain_txt), len(b64hash)))
    return err_cnt


# -----------------------------------------------------------------------------
def test_decode():
    err_cnt = 0

    logging.info("Testing avalon decode...")

    for i in range(len(b64_test_cases)):
        encoded = b64_test_cases[i]["encoded"]
        plain_txt = b64_test_cases[i]["plain"]

        v = crypto_utility.base64_to_byte_array(encoded)
        v = crypto_utility.byte_array_to_string(v)

        if v != plain_txt:
            logging.info("FAILED: encoded: %s" % plain_txt)
            logging.info("        expected plain %s" % encoded)
            logging.info("        actual result: %s" % v)
            err_cnt += 1
        else:
            logging.info("PASSED: %s --> %s, length %lu --> len %d"
                         % (encoded, v, len(encoded), len(v)))
    return err_cnt


# -----------------------------------------------------------------------------
def test_compute_hash():
    err_cnt = 0

    for i in range(len(hash_test_cases)):
        plain_txt = hash_test_cases[i]["plain"]
        encoded = hash_test_cases[i]["encoded"]

        hash = crypto_utility.compute_data_hash(plain_txt)
        b64hash = crypto_utility.byte_array_to_base64(hash)

        hash2 = crypto_utility.compute_message_hash(plain_txt.encode("utf-8"))
        b64hash2 = crypto_utility.byte_array_to_base64(hash2)

        if b64hash == encoded:
            logging.info('PASSED: compute_data_hash("%s")' % plain_txt)
        else:
            logging.info('FAILED: compute_data_hash("%s"):' % plain_txt)
            err_cnt += 1

        if b64hash2 == encoded:
            logging.info('PASSED: compute_message_hash("%s")' % plain_txt)
        else:
            logging.info('FAILED: compute_message_hash("%s"):' % plain_txt)
            err_cnt += 1

    return err_cnt


# -----------------------------------------------------------------------------
def test_verify_data_hash():
    err_cnt = 0
    msg = "Hyperledger"
    msg_hash = \
        "70443919C5F22A3E942CD287ED5EE0FDC8FDFDD246EEB64CB58615518102C6A2"

    if crypto_utility.verify_data_hash(msg, msg_hash):
        logging.info('PASSED: verify_data_hash()')
    else:
        logging.info('FAILED: verify_data_hash()')
        err_cnt += 1

    # negative verify hash
    msg_encoded = "Incorrect data hash"
    if not crypto_utility.verify_data_hash(msg, msg_encoded):
        logging.info('PASSED: verify_data_hash() (negative case)')
    else:
        logging.info('FAILED: verify_data_hash() (negative case)')
        err_cnt += 1

    return err_cnt


# -----------------------------------------------------------------------------
def test_encrypt_decrypt(enc_key, iv):
    err_cnt = 0

    # test random iv
    test_data = "Hyperledger Avalon"
    encrypted_data = \
        crypto_utility.encrypt_data(test_data.encode('utf-8'), enc_key)
    encrypted_data_str = crypto_utility.byte_array_to_base64(encrypted_data)
    decrypted_data = crypto_utility.decrypt_data(enc_key, encrypted_data_str)

    if decrypted_data == test_data:
        logging.info("PASSED: encrypt/decrypt (random iv)")
    else:
        logging.info("FAILED: encrypt/decrypt (random iv)")
        err_cnt += 1

    # test encrypt/decrypt user provided IV
    test_data = "Confidential Computing"
    encrypted_data = \
        crypto_utility.encrypt_data(test_data.encode('utf-8'), enc_key, iv)
    encrypted_data_str = crypto_utility.byte_array_to_base64(encrypted_data)
    decrypted_data = \
        crypto_utility.decrypt_data(enc_key, encrypted_data_str, iv)

    if decrypted_data == test_data:
        logging.info("PASSED: encrypt/decrypt (user provided iv)")
    else:
        logging.info("FAILED: encrypt/decrypt (user provided iv)")
        err_cnt += 1

    # test empty decryption message
    empty_data = bytearray()
    decrypted_data = crypto_utility.decrypt_data(enc_key, empty_data)
    if empty_data == decrypted_data:
        logging.info("PASSED: decrypt_data (empty data)")
    else:
        logging.info("FAILED: decrypt_data (empty data)")
        err_cnt += 1

    return err_cnt


# -----------------------------------------------------------------------------
def test_decrypted_response_session_key():

    session_key = crypto_utility.generate_key()
    session_iv = crypto_utility.generate_iv()

    response = dict()
    response['outData'] = [outdata_0]

    # test decrypt data with session key
    b64_test_data = "SHlwZXJsZWRnZXIgQXZhbG9u"   # "Hyperledger Avalon"
    encrypted_data = crypto_utility.encrypt_data(b64_test_data.encode('utf-8'),
                                                 session_key, session_iv)
    encrypted_data_str = crypto_utility.byte_array_to_base64(encrypted_data)

    outdata_0['iv'] = crypto_utility.byte_array_to_hex(session_iv)
    outdata_0['data'] = encrypted_data_str

    result = \
        crypto_utility.decrypted_response(response, session_key, session_iv)
    if result[0]['data'] == b64_test_data:
        logging.info(
            "PASSED decrypted_response() (encrypted with session key)")
        return 0
    else:
        logging.info(
            "FAILED decrypted_response() (encrypted with session key)")
        return 1


def test_generate_encrypted_key(data_key):

    worker_enc_key = crypto_utility.string_to_byte_array(rsa_public_key)
    try:
        encrypted_key = crypto_utility.generate_encrypted_key(
                        data_key, worker_enc_key)
        logging.info("PASSED: generate_encrypted_key()")
        return 0, encrypted_key
    except Exception as err:
        logging.info("FAILED: generate_encrypted_key()")
        return 1, None


# -----------------------------------------------------------------------------
def test_decrypted_response_data_key():

    response = dict()
    response['outData'] = [outdata_0]

    session_key = crypto_utility.generate_key()
    session_iv = crypto_utility.generate_iv()
    data_key = crypto_utility.generate_key()
    data_iv = crypto_utility.generate_iv()

    # test decrypt data one time data key
    b64_test_data = "SHlwZXJsZWRnZXIgQXZhbG9u"   # "Hyperledger Avalon"
    encrypted_data = crypto_utility.encrypt_data(b64_test_data.encode('utf-8'),
                                                 data_key, data_iv)
    encrypted_data_str = crypto_utility.byte_array_to_base64(encrypted_data)

    err_cnt, encrypted_key = test_generate_encrypted_key(data_key)
    encrypted_data_encryption_key = crypto_utility.encrypt_data(
        encrypted_key, session_key)

    outdata_0['data'] = encrypted_data_str
    outdata_0['encryptedDataEncryptionKey'] = \
        crypto_utility.byte_array_to_hex(encrypted_data_encryption_key)

    result = crypto_utility.decrypted_response(
        response, session_key, session_iv, data_key, data_iv)

    if result[0]['data'] == b64_test_data:
        logging.info("PASSED decrypted_response() (encrypted with data key)")
    else:
        logging.info("FAILED decrypted_response() (encrypted with data key)")
        err_cnt += 1

    return err_cnt


# -----------------------------------------------------------------------------
def test_decrypted_response_no_encryption():

    response = dict()
    response['outData'] = [outdata_0]

    b64_test_data = "SHlwZXJsZWRnZXIgQXZhbG9u"   # "Hyperledger Avalon"

    outdata_0['data'] = b64_test_data
    outdata_0['encryptedDataEncryptionKey'] = "-"

    session_key = crypto_utility.generate_key()
    session_iv = crypto_utility.generate_iv()

    result = \
        crypto_utility.decrypted_response(response, session_key, session_iv)
    if result[0]['data'] == b64_test_data.encode('utf-8'):
        logging.info("PASSED decrypted_response() (not encrypted)")
        return 0
    else:
        logging.info("FAILED decrypted_response() (not encrypted)")
        return 1


# -----------------------------------------------------------------------------
def main():

    logging.info("****Executing unit test for crypto_utility.py****")
    err_cnt = 0

    err_cnt += test_byte_array_to_hex()
    err_cnt += test_generate_random_string()
    err_cnt += test_encode()
    err_cnt += test_decode()

    # SHA-256 test
    err_cnt += test_compute_hash()
    err_cnt += test_verify_data_hash()

    result, private_key = test_generate_signing_keys()
    err_cnt += result
    res, public_key = test_get_verifying_key(private_key)
    err_cnt += result
    err_cnt += test_strip_begin_end_public_key(public_key)

    # test symmetric encryption
    result, enc_key = test_generate_key()
    err_cnt += result
    result, session_iv = test_generate_iv()
    err_cnt += result
    result, test_encrypt_decrypt(enc_key, session_iv)
    err_cnt += result

    err_cnt += test_decrypted_response_session_key()
    err_cnt += test_decrypted_response_data_key()
    err_cnt += test_decrypted_response_no_encryption()

    # summarize
    logging.info("\n****Finished executing unit test****")
    if err_cnt == 0:
        logging.info("Crypto Utility PASSED tests")
    else:
        logging.info("Crypto Utility FAILED %d tests" % err_cnt)


if __name__ == "__main__":
    main()
