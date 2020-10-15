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
import random
import string
import json
from hashlib import sha256
from abc import ABC, abstractmethod
import avalon_crypto_utils.worker_encryption as worker_encryption
import avalon_crypto_utils.worker_signing as worker_signing
import avalon_crypto_utils.worker_hash as worker_hash
import avalon_crypto_utils.crypto_utility as crypto_utility
import avalon_worker.workload.workload_processor as workload_processor
from avalon_worker.error_code import WorkerError
import avalon_worker.utility.jrpc_utility as jrpc_utility
from avalon_worker.attestation.sgx_attestation_factory \
    import SgxAttestationFactory

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# -------------------------------------------------------------------------


class BaseWorkOrderProcessor(ABC):
    """
    Graphene work order processing abstract base class.
    """

# -------------------------------------------------------------------------

    def __init__(self, workload_json_file):
        """
        Constructor to generate worker signing and encryption keys.

        Parameters :
            workloads_json_file: JSON file which has workload module details.
        """
        self.workload_json_file = workload_json_file
        self._generate_worker_keys()
        self._generate_worker_signup()
        # Create workload processor.
        self.wl_processor = \
            workload_processor.WorkLoadProcessor(self.workload_json_file)

# -------------------------------------------------------------------------

    def _generate_worker_keys(self):
        """
        Generates worker signing and encryption keys.
        """
        # Generate worker signing key
        logger.info("Generate worker signing and encryption keys")
        self.sign = worker_signing.WorkerSign()
        self.sign.generate_signing_key()
        self.worker_public_sign_key = self.sign.get_public_sign_key()
        # Generate worker encryption key
        self.encrypt = worker_encryption.WorkerEncrypt()
        self.encrypt.generate_rsa_key()
        self.worker_public_enc_key = self.encrypt.get_rsa_public_key()
        # Sign worker encryption key hash
        hash_obj = worker_hash.WorkerHash()
        hash_val = hash_obj.compute_message_hash(self.worker_public_enc_key)
        self.worker_public_enc_key_sign = self.sign.sign_message(hash_val)

# -------------------------------------------------------------------------

    def _generate_worker_signup(self):
        """
        Generate worker signup.
        """
        signup_data_json = {}
        signup_data_json["sealed_data"] = ""
        signup_data_json["verifying_key"] = \
            self.worker_public_sign_key.decode("utf-8")
        signup_data_json["encryption_key"] = \
            self.worker_public_enc_key.decode("utf-8")
        signup_data_json["encryption_key_signature"] = \
            self.worker_public_enc_key_sign.hex()
        # Create Graphene SGX Attestation instance.
        self.sgx_attestation = \
            SgxAttestationFactory().create(SgxAttestationFactory.GRAPHENE)
        signup_data_json["mrenclave"] = \
            self._get_mrenclave()
        signup_data_json["quote"] = \
            self._get_quote()

        self.signup_data_json_str = json.dumps(signup_data_json)

# -------------------------------------------------------------------------

    def process_work_order(self, msg):
        """
        Process Avalon work order or signup request.

        Parameters :
            msg: JSON formatted string containing the request to execute.
        Returns :
            JSON RPC response containing result or error.
        """
        try:
            json_msg = json.loads(msg)
            method_name = json_msg["method"]
            params = json_msg["params"]
        except Exception as ex:
            err_code = WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE
            err_msg = "JSON Error: " + str(ex)
            error_json = jrpc_utility.create_error_response(err_code,
                                                            0,
                                                            err_msg)
            return json.dumps(error_json)
        # Process worker signup/work order
        try:
            if (method_name == "ProcessWorkerSignup"):
                output = self._process_worker_signup()
            elif (method_name == "ProcessWorkOrder"):
                output = self._process_work_order(params)
            else:
                err_code = WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE
                err_msg = "Unsupported method"
                error_json = jrpc_utility.create_error_response(err_code,
                                                                0,
                                                                err_msg)
                output = json.dumps(error_json)
            return output
        except Exception as ex:
            err_code = WorkerError.UNKNOWN_ERROR
            err_msg = "Error processing work order: " + str(ex)
            error_json = jrpc_utility.create_error_response(err_code,
                                                            0,
                                                            err_msg)
            return json.dumps(error_json)

# -------------------------------------------------------------------------

    def _process_worker_signup(self):
        """
        Process signup request and returns worker details.

        Returns :
            JSON signup response containing worker details.
        """
        return self.signup_data_json_str

# -------------------------------------------------------------------------

    @abstractmethod
    def _process_work_order(self, input_json_str):
        """
        Process Avalon work order and returns JSON RPC response

        Parameters :
            input_json_str: JSON formatted work order request string.
                            work order JSON is formatted as per
                            TC spec ver 1.1 section 6.
        Returns :
            JSON RPC response containing result or error.
        """
        pass

# -------------------------------------------------------------------------

    def _verify_work_order_request(self, input_json, session_key,
                                   session_key_iv):
        """
        Verify work order request integrity.
        Verifies work order request hash.

        Parameters :
            input_json: JSON work order request
            session_key: Session key of the client which submitted
                        this work order
            session_key_iv: iv corresponding to the session key
        Returns :
            True on successful verification. False, otherwise.
        """
        # Decrypt request hash
        encrypted_req_hash_hex = input_json["params"]["encryptedRequestHash"]
        encrypted_req_hash = bytes.fromhex(encrypted_req_hash_hex)
        try:
            decrypt_req_hash = self.encrypt.decrypt_data(encrypted_req_hash,
                                                         session_key,
                                                         session_key_iv)
        except Exception as e:
            logger.error("Decryption of request hash: %s", e)
            return False
        # Compute work order request hash
        req_hash = worker_hash.WorkerHash().calculate_request_hash(
            input_json["params"])
        # Compare decrypted request hash with expected value
        if decrypt_req_hash.hex() == req_hash.hex():
            return True
        else:
            return False

# -------------------------------------------------------------------------

    def _create_work_order_response(self, input_json, out_data,
                                    session_key, session_key_iv):
        """
        Creates work order response JSON object.

        Parameters :
            input_json: JSON work order request
            out_data: output data dictionary which has data in plain text
            session_key: Session key of the client which submitted
                        this work order
            session_key_iv: iv corresponding to teh session key
        Returns :
            JSON RPC response containing result.
        """
        output_json = dict()
        output_json["jsonrpc"] = "2.0"
        output_json["id"] = input_json["id"]
        output_json["result"] = dict()
        output_json["result"]["workloadId"] = \
            input_json["params"]["workloadId"]
        output_json["result"]["workOrderId"] = \
            input_json["params"]["workOrderId"]
        output_json["result"]["workerId"] = \
            input_json["params"]["workerId"]
        output_json["result"]["requesterId"] = \
            input_json["params"]["requesterId"]
        workerNonce = ''.join(random.choices(string.ascii_uppercase +
                                             string.digits, k=16))
        output_json["result"]["workerNonce"] = \
            crypto_utility.byte_array_to_base64(
            workerNonce.encode("UTF-8"))
        output_json["result"]["outData"] = [out_data]

        return self._encrypt_and_sign_response(
            session_key, session_key_iv, output_json)

# -------------------------------------------------------------------------

    @abstractmethod
    def _encrypt_and_sign_response(self, session_key,
                                   session_key_iv, output_json):
        """
        Encrypt outdata and compute worker signature.

        Parameters :
            session_key: Session key of the client which submitted
                        this work order
            session_key_iv: iv corresponding to teh session key
            output_json: Pre-populated response json
        Returns :
            JSON RPC response with worker signature

        """
        pass

# -------------------------------------------------------------------------

    def _get_mrenclave(self):
        """
        Get SGX mrenclave value of worker enclave.

        Returns :
            mrenclave value of worker enclave as hex string.
            If Intel SGX environment is not present returns empty string.
        """
        mrenclave = self.sgx_attestation.get_mrenclave()
        return mrenclave

# -------------------------------------------------------------------------

    def _get_quote(self):
        """
        Get SGX quote of worker enclave.

        Returns :
            SGX quote value of worker enclave as base64 encoded string.
            If Intel SGX environment is not present returns empty string.
        """
        # Write user report data.
        # First 32 bytes of report data has SHA256 hash of worker's
        # public signing key. Next 32 bytes is filled with Zero.
        hash_pub_key = sha256(self.worker_public_sign_key).digest()
        user_data = hash_pub_key + bytearray(32)
        ret = self.sgx_attestation.write_user_report_data(user_data)
        # Get quote
        if ret:
            quote_str = self.sgx_attestation.get_quote()
        else:
            quote_str = ""
        # Return quote.
        return quote_str

# -------------------------------------------------------------------------
