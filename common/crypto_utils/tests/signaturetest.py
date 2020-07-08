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

# Test hash calculation, signature generation and verification in
# in signature.py

import json
import logging
import secrets
from utility.file_utils import read_json_file

import avalon_crypto_utils.signature as signature
import avalon_crypto_utils.crypto_utility as crypto_utility
import avalon_sdk.worker.worker_details as worker
from error_code.error_status import SignatureStatus

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

sig_obj = signature.ClientSignature()

# client values
worker_id = secrets.token_hex(32)
work_order_id = secrets.token_hex(32)
requester_id = secrets.token_hex(32)
requester_nonce = secrets.token_hex(16)

session_key = crypto_utility.generate_key()
session_iv = crypto_utility.generate_iv()
session_key_iv = crypto_utility.byte_array_to_hex(session_iv)

client_private_key = crypto_utility.generate_signing_keys()
client_public_key = crypto_utility.get_verifying_key(client_private_key)

# worker values
worker_nonce = secrets.token_hex(16)
worker_enc_key = rsa_public_key

worker_signing_key = crypto_utility.generate_signing_keys()
worker_verifying_key = crypto_utility.get_verifying_key(worker_signing_key)


# -----------------------------------------------------------------------------
def test_calculate_datahash():
    read_json = read_json_file("wo_request.json", ["./"])
    wo_request = json.loads(read_json)["params"]["inData"]

    try:
        result_hash = sig_obj.calculate_datahash(wo_request)
        logging.info("PASSED: calculate_datahash")
        return 0
    except Exception as err:
        logging.info("FAILED: calculate_datahash")
        return 1


# -----------------------------------------------------------------------------
def test_generate_signature():

    msg = "Hyperledger avalon"
    hash = crypto_utility.compute_message_hash(msg.encode("utf-8"))

    try:
        status, signature = \
            sig_obj.generate_signature(hash, client_private_key)
        if status is True:
            logging.info("PASSED: generate_signature")
            return 0
        else:
            logging.info("FAILED: generate_signature")
            return 1
    except Exception as err:
        logging.info("FAILED: generate_signature")
        return 1


# -----------------------------------------------------------------------------
def test_calculate_request_hash():

    read_json = read_json_file("wo_request.json", ["./"])
    wo_request = json.loads(read_json)["params"]
    wo_request["workOrderId"] = work_order_id
    wo_request["workerId"] = worker_id
    wo_request["requesterId"] = requester_id
    wo_request["sessionKeyIv"] = session_key_iv
    wo_request["requesterNonce"] = requester_nonce

    try:
        resp_hash = sig_obj.calculate_request_hash(wo_request)
        logging.info("PASSED: calculate_request_hash")
        return 0
    except Exception as err:
        logging.info("FAILED: calculate_request_hash")
        return 1


# -----------------------------------------------------------------------------
def test_calculate_response_hash():

    read_json = read_json_file(
            "wo_response.json", ["./"])
    wo_response = json.loads(read_json)["result"]
    wo_response["workOrderId"] = work_order_id
    wo_response["workerId"] = worker_id
    wo_response["requesterId"] = requester_id
    wo_response["workerNonce"] = worker_nonce

    try:
        resp_hash = sig_obj.calculate_response_hash(wo_response)
        logging.info("PASSED: calculate_response_hash")
        return 0
    except Exception as err:
        logging.info("FAILED: calculate_response_hash")
        return 1


# -----------------------------------------------------------------------------
def test_verify_encryption_key_signature():

    enc_key_sig_byte = crypto_utility.string_to_byte_array(worker_enc_key)
    enc_key_hash = crypto_utility.compute_message_hash(enc_key_sig_byte)

    try:
        # sign encryption key
        status, enc_key_signature = \
                sig_obj.generate_signature(enc_key_hash, worker_signing_key)
        enc_key_signature = \
            crypto_utility.base64_to_byte_array(enc_key_signature)
        enc_key_signature_hex = \
            crypto_utility.byte_array_to_hex(enc_key_signature)

        status = sig_obj.verify_encryption_key_signature(
            enc_key_signature_hex, worker_enc_key, worker_verifying_key)
        if status == SignatureStatus.PASSED:
            logging.info("PASSED: verify_encryption_key_signature")
            return 0
        else:
            logging.info("FAILED: verify_encryption_key_signature")
            return 1
    except Exception as err:
        logging.info("FAILED: verify_encryption_key_signature")
        return 1


# -----------------------------------------------------------------------------
def test_verify_create_receipt_signature():

    read_json = read_json_file("wo_receipt_request.json", ["./"])
    wo_receipt_request = json.loads(read_json)
    wo_receipt_req_params = wo_receipt_request["params"]
    wo_receipt_req_params["workOrderId"] = work_order_id
    wo_receipt_req_params["workerId"] = worker_id
    wo_receipt_req_params["requesterNonce"] = requester_nonce
    wo_receipt_req_params["receiptVerificationKey"] = client_public_key

    # generate hash
    wo_receipt_str = wo_receipt_req_params["workOrderId"] + \
        wo_receipt_req_params["workerServiceId"] + \
        wo_receipt_req_params["workerId"] + \
        wo_receipt_req_params["requesterId"] + \
        str(wo_receipt_req_params["receiptCreateStatus"]) + \
        wo_receipt_req_params["workOrderRequestHash"] + \
        wo_receipt_req_params["requesterGeneratedNonce"]
    wo_receipt_bytes = bytes(wo_receipt_str, "UTF-8")
    wo_receipt_hash = crypto_utility.compute_message_hash(wo_receipt_bytes)

    try:
        # sign hash
        status, wo_receipt_sign = sig_obj.generate_signature(
            wo_receipt_hash, client_private_key)
        wo_receipt_req_params["requesterSignature"] = wo_receipt_sign

        # test verify signature
        status = sig_obj.verify_create_receipt_signature(wo_receipt_request)
        if status == SignatureStatus.PASSED:
            logging.info("PASSED: verify_create_receipt_signature")
            return 0
        else:
            logging.info("FAILED: verify_create_receipt_signature")
            return 1
    except Exception as err:
        logging.info("FAILED: verify_create_receipt_signature")
        return 1


# -----------------------------------------------------------------------------
def test_verify_update_receipt_signature():

    # update the payload
    updater_id = crypto_utility.strip_begin_end_public_key(client_public_key)

    read_json = read_json_file("wo_receipt_update_response.json", ["./"])
    wo_receipt_update_response = json.loads(read_json)["result"]
    wo_receipt_update_response["workOrderId"] = work_order_id
    wo_receipt_update_response["updaterId"] = updater_id
    wo_receipt_update_response["receiptVerificationKey"] = client_public_key

    wo_receipt_str = wo_receipt_update_response["workOrderId"] + \
        str(wo_receipt_update_response["updateType"]) + \
        wo_receipt_update_response["updateData"]
    wo_receipt_bytes = bytes(wo_receipt_str, "UTF-8")
    wo_receipt_hash = crypto_utility.compute_message_hash(wo_receipt_bytes)

    try:
        status, wo_receipt_sign = sig_obj.generate_signature(
                wo_receipt_hash, client_private_key)
        wo_receipt_update_response["updateSignature"] = wo_receipt_sign

        # test verify update receipt
        status = sig_obj.verify_update_receipt_signature(
                wo_receipt_update_response)
        if status == SignatureStatus.PASSED:
            logging.info("PASSED: verify_update_receipt_signature")
            return 0
        else:
            logging.info("FAILED: verify_update_receipt_signature")
            return 1
    except Exception as err:
        logging.info("FAILED: verify_update_receipt_signature")
        return 1


# -----------------------------------------------------------------------------
def test_verify_signature():
    err_cnt = 0
    read_json = read_json_file(
            "wo_response.json", ["./"])
    wo_response = json.loads(read_json)["result"]
    wo_response["workOrderId"] = work_order_id
    wo_response["workerId"] = worker_id
    wo_response["requesterId"] = requester_id
    wo_response["workerNonce"] = worker_nonce

    try:
        # imitate worker signature SHA-256/RSA-OAEP-4096
        response_hash = sig_obj.calculate_response_hash(wo_response)
        status, sign = sig_obj.generate_signature(
            response_hash, worker_signing_key)
        wo_response["workerSignature"] = sign

        # test 1 step verification
        status = sig_obj.verify_signature(
            wo_response, worker_verifying_key, requester_nonce)
        if status == SignatureStatus.PASSED:
            logging.info("PASSED: verify_signature (1 step)")
        else:
            logging.info("FAILED: verify_signature (1 step)")
            err_cnt += 1
    except Exception as err:
        logging.info("FAILED: verify_signature (1 step)")
        err_cnt += 1

    # generate extVerificationKey
    ext_private_key = crypto_utility.generate_signing_keys()
    ext_public_key = crypto_utility.get_verifying_key(ext_private_key)
    wo_response["extVerificationKey"] = ext_public_key

    # sign extVerificationKey with worker private key
    concat_string = wo_response["extVerificationKey"] + requester_nonce
    v_key_hash = crypto_utility.compute_message_hash(
        bytes(concat_string, 'UTF-8'))

    try:
        status, sign = \
            sig_obj.generate_signature(v_key_hash, worker_signing_key)
        wo_response["extVerificationKeySignature"] = sign

        # Sign wo_response with extVerificationKey
        response_hash = sig_obj.calculate_response_hash(wo_response)
        status, sign = \
            sig_obj.generate_signature(response_hash, ext_private_key)
        wo_response["workerSignature"] = sign

        # test 2 step verification
        status = sig_obj.verify_signature(
            wo_response, worker_verifying_key, requester_nonce)
        if status == SignatureStatus.PASSED:
            logging.info("PASSED: verify_signature (2 step)")
        else:
            logging.info("FAILED: verify_signature (2 step)")
            err_cnt += 1
    except Exception as err:
        logging.info("FAILED: verify_signature (2 step)")
        err_cnt += 1

    return err_cnt


# -----------------------------------------------------------------------------
def test_generate_client_signature():

    logging.info("Testing generate_client_signature...")

    worker_obj = worker.SGXWorkerDetails()
    worker_obj.encryption_key = worker_enc_key
    encrypted_session_key = crypto_utility.generate_encrypted_key(
                   session_key, worker_obj.encryption_key)
    encrypted_session_key_hex = \
        crypto_utility.byte_array_to_hex(encrypted_session_key)

    read_json = read_json_file("wo_request.json", ["./"])
    wo_submit_request = json.loads(read_json)
    wo_request = wo_submit_request["params"]
    wo_request["workOrderId"] = work_order_id
    wo_request["workerId"] = worker_id
    wo_request["requesterId"] = requester_id
    wo_request["sessionKeyIv"] = session_key_iv
    wo_request["encryptedSessionKey"] = encrypted_session_key_hex
    wo_request["requesterNonce"] = requester_nonce

    try:
        input_json_str = json.dumps(wo_submit_request)
        input_json_str, status = sig_obj.generate_client_signature(
            input_json_str, worker_obj, client_private_key, session_key,
            session_iv, encrypted_session_key)

        if status == SignatureStatus.PASSED:
            logging.info("PASSED: generate_client_signature")
            return 0
        else:
            logging.info("FAILED: generate_client_signature")
            return 1
    except Exception as err:
        return 1


# -----------------------------------------------------------------------------
def main():

    logging.info("\n\n****Executing unit tests for signature.py****")
    err_cnt = 0

    err_cnt += test_calculate_datahash()
    err_cnt += test_generate_signature()
    err_cnt += test_calculate_request_hash()
    err_cnt += test_calculate_response_hash()
    err_cnt += test_verify_encryption_key_signature()
    err_cnt += test_verify_create_receipt_signature()
    err_cnt += test_verify_update_receipt_signature()
    err_cnt += test_verify_signature()
    err_cnt += test_generate_client_signature()

    # summarize
    logging.info("\n****Finished executing unit test****")
    if err_cnt == 0:
        logging.info("Signature PASSED all tests")
    else:
        logging.info("Signature FAILED %d tests" % err_cnt)


if __name__ == "__main__":
    main()
