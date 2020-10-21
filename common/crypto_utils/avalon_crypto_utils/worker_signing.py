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
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from ecdsa.util import sigencode_der, sigdecode_der
import avalon_crypto_utils.crypto_utility as crypto_utility
from utility.hex_utils import hex_to_byte_array
import avalon_crypto_utils.worker_hash as worker_hash


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# -------------------------------------------------------------------------


class WorkerSign():
    """
    Worker Signing key class.
    """

# -------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor for WorkerSign.
        """
        self.sign_private_key = None
        self.sign_public_key = None

# -------------------------------------------------------------------------

    def generate_signing_key(self):
        """
        Generate ECDSA (SECP256k1 curve) signing key pair.
        """
        sk = SigningKey.generate(curve=SECP256k1)
        vk = sk.get_verifying_key()
        self.sign_private_key = sk
        self.sign_public_key = vk

# -------------------------------------------------------------------------

    def get_public_sign_key(self):
        """
        Get ECDSA Public (Verifiying) key as serialized PEM bytes.
        generate_signing_key() should be called before calling
        this function.

        Returns :
            ECDSA Public (Verifiying) key as serialized PEM bytes.
        """
        if self.sign_public_key:
            return self.sign_public_key.to_pem()
        else:
            return None

# -------------------------------------------------------------------------

    def sign_message(self, message_hash_bytes):
        """
        Sign message hash using ECDSA private key.

        Parameters :
            message_hash_bytes: Message hash to sign in bytes
        Returns :
            signed message in bytes.
            Raises exception in case of error.
        """
        try:
            private_key = self.sign_private_key
            signed = \
                private_key.sign_digest_deterministic(
                    message_hash_bytes,
                    sigencode=sigencode_der)
        except Exception as e:
            err_msg = "Sign message failed: " + str(e)
            logger.error(err_msg)
            raise
        return signed

# -------------------------------------------------------------------------

    def verify_signature_from_pubkey(self, signature_bytes,
                                     message_hash_bytes,
                                     pub_key_pem_bytes):
        """
        Verifies signature using ECDSA public(verifying) key.

        Parameters :
            signature_bytes : Signed message in bytes
            message_hash_bytes: Message hash in bytes to verify the signature
            pub_key_pem_bytes: ECDSA public key as serialized PEM bytes.
        Returns :
            Boolean.
        """
        try:
            vk = VerifyingKey.from_pem(pub_key_pem_bytes)
            return vk.verify_digest(signature_bytes, message_hash_bytes,
                                    sigdecode=sigdecode_der)
        except Exception as e:
            err_msg = "Verify signature failed: " + str(e)
            logger.error(err_msg)
            return False

# -------------------------------------------------------------------------

    def _verify_wo_response_signature(self, wo_response,
                                      wo_res_verification_key):
        """
        Function to verify the work order response signature
        Parameters:
            @param wo_response - dictionary contains work order response
            as per Trusted Compute EEA API 6.1.2 Work Order Result Payload
            @param wo_res_verification_key - ECDSA/SECP256K1 public key
            used to verify work order response signature.
        Returns enum type SignatureStatus
        """
        if "workerSignature" not in wo_response:
            logger.error("workerSignature not present in reponse json")
            return False
        signature = wo_response['workerSignature']
        response_hash = worker_hash.WorkerHash().calculate_response_hash(
            wo_response)
        decoded_signature = crypto_utility.base64_to_byte_array(signature)

        return self.verify_signature_from_pubkey(decoded_signature,
                                                 response_hash,
                                                 wo_res_verification_key)

# -------------------------------------------------------------------------

    def _verify_wo_verification_key_signature(self,
                                              wo_response,
                                              wo_verification_key,
                                              requester_nonce):
        """
        Function to verify the work order response signature
        Parameters:
            @param wo_response - dictionary contains work order response
            as per Trusted Compute EEA API 6.1.2 Work Order Result Payload
            @param wo_verification_key - ECDSA/SECP256K1 public key used
            to verify work order verification key signature.
            @param requester_nonce - requester generated nonce passed in work
            order request. Required in 2 step verification.
        Returns enum type SignatureStatus
        """
        if requester_nonce is None:
            logger.error("Missing requester_nonce argument")
            return SignatureStatus.FAILED

        concat_string = wo_response["extVerificationKey"] + requester_nonce
        v_key_sig = wo_response["extVerificationKeySignature"]
        v_key_hash = crypto_utility.compute_message_hash(
            bytes(concat_string, 'UTF-8'))
        decoded_v_key_sig = crypto_utility.base64_to_byte_array(v_key_sig)
        return self.verify_signature_from_pubkey(decoded_v_key_sig,
                                                 v_key_hash,
                                                 wo_verification_key)

# -----------------------------------------------------------------------------
    def verify_signature(self, wo_response, wo_res_verification_key,
                         requester_nonce=None):
        """
        Function to verify the signature received from the enclave
        Parameters:
            @param wo_response - dictionary contains work order response
            as per Trusted Compute EEA API 6.1.2 Work Order Result Payload
            @param wo_res_verification_key - worker ECDSA/SECP256K1
            public key used to verify work order response signature.
            @param requester_nonce - requester generated nonce passed in work
            order request. Required in 2 step verification.
        Returns enum type SignatureStatus
        """
        # if verification_key present in work order response
        # then do 2 step verification
        # step1 - The verification key signature from the
        # response is verified using worker’s public verification key
        # (aka KME's verification key)
        if "extVerificationKey" in wo_response:
            status = self._verify_wo_verification_key_signature(
                wo_response,
                wo_res_verification_key,
                requester_nonce)
            if status == SignatureStatus.PASSED:
                # step2 : work order response signature is verified
                # using the verification key in the response
                return self._verify_wo_response_signature(
                    wo_response,
                    wo_response["extVerificationKey"])
            else:
                return status
        else:
            # In case of singleton worker, it is 1 step
            # verification. Verify work order response signature
            # using singleton worker public verification key.
            return self._verify_wo_response_signature(
                wo_response,
                wo_res_verification_key)

# -----------------------------------------------------------------------------
    def verify_update_receipt_signature(self, input_json):
        """
        Function to verify the signature of work order receipt update
        Parameters:
            - input_json is dictionary contains payload returned by the
              WorkOrderReceiptUpdateRetrieve API as define EEA spec 7.2.7
        Returns enum type SignatureStatus
        """
        input_json_params = input_json

        concat_string = input_json_params["workOrderId"] + \
            str(input_json_params["updateType"]) + \
            input_json_params["updateData"]
        concat_hash = bytes(concat_string, 'UTF-8')
        final_hash = crypto_utility.compute_message_hash(concat_hash)
        signature = input_json_params["updateSignature"]
        verification_key = \
            input_json_params["receiptVerificationKey"].encode("ascii")

        decoded_signature = crypto_utility.base64_to_byte_array(signature)

        return self.verify_signature_from_pubkey(decoded_signature,
                                                 final_hash,
                                                 verification_key)

# -----------------------------------------------------------------------------
    def verify_create_receipt_signature(self, input_json):
        """
        Function to verify the signature of work order receipt create
        Parameters:
            - input_json is dictionary contains request payload of
              WorkOrderReceiptRetrieve API as define EEA spec 7.2.2
        Returns enum type SignatureStatus
        """
        input_json_params = input_json['params']

        concat_string = input_json_params["workOrderId"] + \
            input_json_params["workerServiceId"] + \
            input_json_params["workerId"] + \
            input_json_params["requesterId"] + \
            str(input_json_params["receiptCreateStatus"]) + \
            input_json_params["workOrderRequestHash"] + \
            input_json_params["requesterGeneratedNonce"]
        concat_hash = bytes(concat_string, "UTF-8")
        final_hash = bytes(crypto_utility.compute_message_hash(concat_hash))
        signature = input_json_params["requesterSignature"]
        verification_key = \
            input_json_params["receiptVerificationKey"].encode("ascii")

        decoded_signature = crypto_utility.base64_to_byte_array(signature)
        return self.verify_signature_from_pubkey(decoded_signature,
                                                 final_hash,
                                                 verification_key)

# -----------------------------------------------------------------------------
    def verify_encryption_key_signature(
            self, encryption_key_signature, encryption_key, verifying_key):
        """
        Utils function to verify integrity of worker encryption key using
        worker verification key
        @params encryption_key_signature - Signature computed on hash
                                           of encryption key
        @params encryption_key - Public encryption key of the worker
        @params verifying_key - Public signing key or verification key
                                of the worker
        returns SignatureStatus.PASSED in case of successful verification
                SignatureStatus.FAILED in case of verification failure
        """

        encrypt_key_sig_bytes = hex_to_byte_array(encryption_key_signature)
        encrypt_key_bytes = crypto_utility.string_to_byte_array(encryption_key)
        encryption_key_hash = worker_hash.WorkerHash().compute_message_hash(
            encrypt_key_bytes)

        return self.verify_signature_from_pubkey(encrypt_key_sig_bytes,
                                                 encryption_key_hash,
                                                 verifying_key)
