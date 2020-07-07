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
import base64
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from ecdsa.util import sigencode_der, sigdecode_der
import avalon_worker.worker_hash as worker_hash


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

    def verify_response_signature(self, response_json, worker_verify_key):
        """
        Verifies work order response signature.

        Parameters :
            response_json : Work order Response JSON RPC
                            as per TC Spec v1.1 section 6.1
            worker_verify_key: worker ECDSA verifying key
                               as serialized PEM bytes.
        Returns :
            Boolean.
        """
        if "result" not in response_json:
            logger.error("result not present in reponse json")
            return False
        if "workerSignature" not in response_json["result"]:
            logger.error("workerSignature not present in reponse json")
            return False
        res_hash_bytes = worker_hash.WorkerHash().calculate_response_hash(
            response_json["result"])
        worker_sig = response_json["result"]["workerSignature"]
        worker_sig_bytes = base64.b64decode(worker_sig.encode("UTF-8"))

        verify = self.verify_signature_from_pubkey(worker_sig_bytes,
                                                   res_hash_bytes,
                                                   worker_verify_key)
        return verify

# -------------------------------------------------------------------------
