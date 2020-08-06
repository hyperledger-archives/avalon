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

import json
import logging
import secrets
from generic_client_interface import GenericClientInterface
from avalon_sdk.work_order.work_order_params import WorkOrderParams
import avalon_crypto_utils.signature as signature
import avalon_crypto_utils.crypto_utility as crypto_utility
import verify_report.verify_attestation_report as attestation_util
from error_code.error_status import SignatureStatus

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class BaseGenericClient(GenericClientInterface):
    """
    Abstract class for generic client
    It has common functions which are common to both
    direct and proxy model.
    """

    def __init__(self):
        super().__init__()
        self._worker_registry_list_instance = None
        self._worker_instance = None
        self._work_order_instance = None
        self._work_order_receipt_instance = None

    def do_worker_verification(self, worker_obj, mr_enclave):
        """
        Do worker verification on proof data if it exists
        Proof data exists in SGX hardware mode.
        """
        encryption_key_signature = worker_obj.encryption_key_signature
        if encryption_key_signature is not None:
            encryption_key = worker_obj.encryption_key
            verify_key = worker_obj.verification_key

            # Verify worker encryption key signature
            # using worker verification key
            sig_obj = signature.ClientSignature()
            sig_status = sig_obj.verify_encryption_key_signature(
                encryption_key_signature, encryption_key, verify_key)
            if (sig_status != SignatureStatus.PASSED):
                logger.error(
                    "Failed to verify worker encryption key signature")
                return False

        if not worker_obj.proof_data:
            logging.info("Proof data is empty. " +
                         "Skipping verification of attestation report")
        else:
            # Construct enclave sign-up info json
            enclave_info = {
                'verifying_key': worker_obj.verification_key,
                'encryption_key': worker_obj.encryption_key,
                'proof_data': worker_obj.proof_data,
                'enclave_persistent_id': ''
            }

            logging.info("Perform verification of attestation report")
            verify_report_status = attestation_util.verify_attestation_report(
                enclave_info, mr_enclave)
            if verify_report_status is False:
                logging.error("Verification of enclave sign-up info failed")
                return False
            else:
                logging.info("Verification of enclave sign-up info passed")
                return True

    def create_work_order_params(self, worker_id, workload_id,
                                 in_data, worker_encrypt_key,
                                 session_key, session_iv,
                                 enc_data_enc_key):
        """
        Create work order request params
        """
        work_load_id = workload_id.encode("UTF-8").hex()
        self._work_order_id = secrets.token_hex(32)
        self._session_key = session_key
        self._session_iv = session_iv
        requester_id = secrets.token_hex(32)
        requester_nonce = secrets.token_hex(16)
        # Create work order params
        try:
            wo_params = WorkOrderParams(
                self._work_order_id, worker_id, work_load_id, requester_id,
                self._session_key, self._session_iv, requester_nonce,
                worker_encryption_key=worker_encrypt_key,
                data_encryption_algorithm="AES-GCM-256"
            )
        except Exception as err:
            logging.error("Exception occurred while "
                          "creating work order request {}".format(err))
            return False, None
        # Add worker input data
        for value in in_data:
            wo_params.add_in_data(
                value,
                encrypted_data_encryption_key=enc_data_enc_key)

        # Encrypt work order request hash
        code, out_json = wo_params.add_encrypted_request_hash()
        if not code:
            logging.error("Creating encrypted request hash failed")
            return code, None

        return True, wo_params

    def get_work_order_result(self, work_order_id):
        """
        Retrieve work order result for given work order id
        """
        work_order_res = self._work_order_instance.work_order_get_result(
            work_order_id
        )
        logging.info("Work order get result {}".format(
            json.dumps(work_order_res, indent=4)))

        if work_order_res and "result" in work_order_res:
            return True, work_order_res
        return False, work_order_res

    def verify_wo_response_signature(self, work_order_res,
                                     worker_verification_key,
                                     requester_nonce):
        """
        Verify Work order response signature
        """
        sig_obj = signature.ClientSignature()
        status = sig_obj.verify_signature(
            work_order_res, worker_verification_key,
            requester_nonce)
        if status == SignatureStatus.PASSED:
            logging.info("Signature verification Successful")
            return True
        else:
            logging.error("Signature verification Failed")
            return False

    def decrypt_wo_response(self, wo_res):
        """
        Decrypt work order response
        """
        try:
            decrypted_res = crypto_utility.decrypted_response(
                wo_res, self._session_key, self._session_iv)
        except Exception as ex:
            logging.error("Error in decrypting response {}".format(ex))
            return None
        return decrypted_res
