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

from abc import ABC, abstractmethod


class GenericClientInterface(ABC):
    """
    Generic client interface
    """
    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_worker_details(self, worker_id):
        """
        Fetch worker details for given worker id
        @param worker_id is identifier of worker
        returns worker details object
        """
        pass

    @abstractmethod
    def do_worker_verification(self, worker_obj):
        """
        Do worker verification on proof data if it exists
        Proof data exists in SGX hardware mode.
        @param worker_obj is workerDetails object
        return True if worker verification success
        otherwise return False
        """
        pass

    @abstractmethod
    def create_work_order_params(self, worker_id, workload_id,
                                 in_data, worker_encrypt_key,
                                 session_key, session_iv,
                                 enc_data_enc_key):
        """
        Create work order request using work order
        params class.
        @param worker_id - worker id
        @param workload_id work load id
        @param in_data in data
        @param worker_encrypt_key worker public encryption key
        @param session_key session key
        @param session_iv session iv
        @param enc_data_enc_key data encryption key
        Returns work order params object
        """
        pass

    @abstractmethod
    def submit_work_order(self, worker_id, worker_encrypt_key,
                          session_key, session_iv,
                          verification_key):
        """
        Submit work order request
        @param worker_id is identifier for worker
        @param worker_encrypt_key is encryption key of worker
        @param session_key is session key of work order request
        @param session_iv is session iv
        @param verification_key is verification key
        returns True on successfully submit work order request
        otherwise False
        """
        pass

    @abstractmethod
    def get_work_order_result(self, work_order_id):
        """
        Retrieve work order result for given work order id
        returns work order response
        """
        pass

    @abstractmethod
    def verify_wo_response_signature(self, work_order_res,
                                     worker_verification_key,
                                     requester_nonce):
        """
        Verify Work order response signature
        @param work_order_res - work order response
        @param worker_verification_key is verification key
        @param requester_nonce - requester nonce
        returns True on success False on failure
        """
        pass

    @abstractmethod
    def decrypt_wo_response(self, wo_res):
        """
        Decrypt work order response
        @param wo_res - work order response
        returns decrypted response
        """
        pass

    @abstractmethod
    def create_work_order_receipt(self, wo_params,
                                  client_private_key):
        """
        Create a work order receipt object using
        WorkOrderReceiptRequest class.
        @param wo_params work order params object
        @param client_private_key private key to sign the receipt
        request
        Returns True if receipt create is success otherwise False
        """
        pass

    @abstractmethod
    def retrieve_work_order_receipt(self, work_order_id):
        """
        Retrieve work order receipt
        @param work_order_id - work order identifier
        Returns work order receipt retrieve response
        """
        pass

    @abstractmethod
    def verify_receipt_signature(self, receipt_update_retrieve_res):
        """
        Verify work order receipt signature

        @param receipt_update_retrieve_res - receipt update retrieve
        response
        Returns True on success, False otherwise
        """
        pass
