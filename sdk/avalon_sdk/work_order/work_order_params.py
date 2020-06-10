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

import json
import logging

import avalon_crypto_utils.crypto.crypto as crypto
import avalon_crypto_utils.crypto_utility as crypto_utility
import avalon_crypto_utils.signature as signature

logger = logging.getLogger(__name__)


class WorkOrderParams():
    def __init__(
            self, work_order_id, worker_id, workload_id,
            requester_id, session_key, session_iv,
            requester_nonce, verifying_key=None, payload_format="JSON-RPC",
            response_timeout_msecs=6000, result_uri=None,
            notify_uri=None, worker_encryption_key=None,
            data_encryption_algorithm=None):
        self.params_obj = {}
        self.set_work_order_id(work_order_id)
        self.set_response_timeout_msecs(response_timeout_msecs)
        self.set_payload_format(payload_format)
        if result_uri:
            self.set_result_uri(result_uri)
        if notify_uri:
            self.set_notify_uri(notify_uri)
        self.set_worker_id(worker_id)
        self.set_workload_id(workload_id)
        self.set_requester_id(requester_id)
        if worker_encryption_key:
            self.set_worker_encryption_key(
                worker_encryption_key.encode("UTF-8").hex())
        if data_encryption_algorithm:
            self.set_data_encryption_algorithm(data_encryption_algorithm)

        encrypted_session_key = crypto_utility.generate_encrypted_key(
            session_key, worker_encryption_key)
        self.set_encrypted_session_key(
            crypto.byte_array_to_hex(encrypted_session_key)
        )

        self.session_iv = session_iv
        self.set_session_key_iv(
            crypto.byte_array_to_hex(session_iv)
        )
        self.set_requester_nonce(requester_nonce)
        self.params_obj["encryptedRequestHash"] = ""
        self.params_obj["requesterSignature"] = ""
        self.params_obj["inData"] = []
        self.session_key = session_key

    def set_response_timeout_msecs(self, response_timeout_msecs):
        """Set responseTimeoutMSecs work order parameter."""
        self.params_obj["responseTimeoutMSecs"] = \
            response_timeout_msecs

    def set_payload_format(self, payload_format):
        """Set payloadFormat work order parameter."""
        self.params_obj["payloadFormat"] = payload_format

    def set_result_uri(self, result_uri):
        """Set resultUri work order parameter."""
        self.params_obj["resultUri"] = result_uri

    def set_notify_uri(self, notify_uri):
        """Set notifyUri work order parameter."""
        self.params_obj["notifyUri"] = notify_uri

    def set_worker_id(self, worker_id):
        """Set workerId work order parameter."""
        self.params_obj["workerId"] = worker_id

    def set_work_order_id(self, work_order_id):
        """Set workOrderId work order parameter."""
        self.params_obj["workOrderId"] = work_order_id

    def set_workload_id(self, workload_id):
        """Set workloadId work order parameter."""
        self.params_obj["workloadId"] = workload_id

    def set_requester_id(self, requester_id):
        """Set requesterId work order parameter."""
        self.params_obj["requesterId"] = requester_id

    def set_worker_encryption_key(self, worker_encryption_key):
        """Set workerEncryptionKey work order parameter."""
        self.params_obj["workerEncryptionKey"] = worker_encryption_key

    def set_data_encryption_algorithm(self, data_encryption_algorithm):
        """Set dataEncryptionAlgorithm work order parameter."""
        self.params_obj["dataEncryptionAlgorithm"] = \
            data_encryption_algorithm

    def set_encrypted_session_key(self, encrypted_session_key):
        """Set encryptedSessionKey work order parameter."""
        self.params_obj["encryptedSessionKey"] = encrypted_session_key

    def set_session_key_iv(self, session_iv):
        """Set sessionKeyIv work order parameter."""
        self.params_obj["sessionKeyIv"] = session_iv

    def set_requester_nonce(self, requester_nonce):
        """Set requesterNonce work order parameter."""
        self.params_obj["requesterNonce"] = requester_nonce

    def add_encrypted_request_hash(self):
        """
        Calculates request hash based on EEA trusted-computing spec 6.1.8.1
        and set encryptedRequestHash parameter in the request.
        """
        sig_obj = signature.ClientSignature()
        concat_string = self.get_requester_nonce() + \
            self.get_work_order_id() + \
            self.get_worker_id() + \
            self.get_workload_id() + \
            self.get_requester_id()
        concat_bytes = bytes(concat_string, "UTF-8")
        # SHA-256 hashing is used
        hash_1 = crypto.byte_array_to_base64(
            crypto.compute_message_hash(concat_bytes)
        )
        hash_2 = sig_obj.calculate_datahash(self.get_in_data())
        hash_3 = ""
        out_data = self.get_out_data()
        if out_data and len(out_data) > 0:
            hash_3 = sig_obj.calculate_datahash(out_data)
        concat_hash = hash_1 + hash_2 + hash_3
        concat_hash = bytes(concat_hash, "UTF-8")
        self.final_hash = crypto.compute_message_hash(concat_hash)
        encrypted_request_hash = crypto_utility.encrypt_data(
            self.final_hash, self.session_key, self.session_iv)
        self.params_obj["encryptedRequestHash"] = crypto.byte_array_to_hex(
            encrypted_request_hash)

    def add_requester_signature(self, private_key):
        """
        Calculate the signature of the request
        as defined in Off-Chain Trusted Compute EEA spec 6.1.8.3
        and set the requesterSignature parameter in the request.
        """
        sig_obj = signature.ClientSignature()
        status, sign = sig_obj.generate_signature(
            self.final_hash,
            private_key
        )
        if status is True:
            self.params_obj["requesterSignature"] = sign
            # public signing key is shared to enclave manager to
            # verify the signature.
            # It is temporary approach to share the key with the worker.
            self.set_verifying_key(private_key.GetPublicKey().Serialize())
            return True
        else:
            logger.error("Signing request failed")
            return False

    def set_verifying_key(self, verifying_key):
        """Set verifyingKey work order parameter."""
        self.params_obj["verifyingKey"] = verifying_key

    def add_in_data(self, data, data_hash=None,
                    encrypted_data_encryption_key=None, data_iv=None):
        """Add inData work order parameter."""
        in_data_copy = self.params_obj["inData"]
        new_data_list = self.__add_data_params(
            in_data_copy, data, data_hash, encrypted_data_encryption_key,
            data_iv)

        self.params_obj["inData"] = new_data_list

    def add_out_data(self, data, data_hash=None,
                     encrypted_data_encryption_key=None, data_iv=None):
        """Add outData work order parameter."""
        if "outData" not in self.params_obj:
            self.params_obj["outData"] = []
        out_data_copy = self.params_obj["outData"]
        new_data_list = self.__add_data_params(
            out_data_copy, data, data_hash, encrypted_data_encryption_key,
            data_iv)
        self.params_obj["outData"] = new_data_list

    def __add_data_params(self, data_items, data, data_hash=None,
                          encrypted_data_encryption_key=None, data_iv=None):
        """
        Add data parameters data, dataHash encryptedDataEncryptionKey, and iv.
        """
        index = len(data_items)
        data_items.append({})
        data_items[index]["index"] = index
        data_items[index]["data"] = self.__encrypt_data(
            data,
            encrypted_data_encryption_key,
            data_iv
        )
        if data_hash:
            data_items[index]["dataHash"] = data_hash
        if encrypted_data_encryption_key:
            data_items[index]["encryptedDataEncryptionKey"] = \
                encrypted_data_encryption_key
        if data_iv:
            data_items[index]["iv"] = data_iv
        return data_items

    # Use these if you want to pass json to WorkOrderJRPCImpl
    def get_params(self):
        """Return a copy of work order parameters."""
        params_copy = self.params_obj.copy()
        params_copy.pop("inData")
        if "outData" in params_copy:
            params_copy.pop("outData")
        return params_copy

    def get_in_data(self):
        """Return inData work order parameter."""
        return self.params_obj["inData"]

    def get_out_data(self):
        """Return outData work order parameter."""
        if "outData" in self.params_obj:
            return self.params_obj["outData"]
        else:
            return None

    def get_requester_nonce(self):
        """Return requesterNonce work order parameter."""
        return self.params_obj["requesterNonce"]

    def get_worker_id(self):
        """Return workerId work order parameter."""
        return self.params_obj["workerId"]

    def get_workload_id(self):
        """Return workloadId work order parameter."""
        return self.params_obj["workloadId"]

    def get_requester_id(self):
        """Return requesterId work order parameter."""
        return self.params_obj["requesterId"]

    def get_session_key_iv(self):
        """Return sessionKeyIv work order parameter."""
        return self.params_obj["sessionKeyIv"]

    def get_work_order_id(self):
        """Return workOrderId work order parameter."""
        return self.params_obj["workOrderId"]

    def __encrypt_data(self, data, encrypted_data_encryption_key=None,
                       data_iv=None):
        """
        Encrypt data and encode in base64 format.
        If key is None or "" or null, use session key.
        If key is "-" skip encryption and just encode base64.

        Parameters:
        data                          Data to encrypt
        encrypted_data_encryption_key Encryption private key.
                                      Pass "-" for no encryption.
                                      Pass "" or None to encrypt with
                                      the session key
        data_iv                       IV for data

        Returns:
        Encrypted (if requested) and base64 encoded data.
        """
        data = data.encode("UTF-8")
        if encrypted_data_encryption_key is None or \
                encrypted_data_encryption_key == "" or \
                encrypted_data_encryption_key == "null":
            enc_data = crypto_utility.encrypt_data(
                data, self.session_key, self.session_iv
            )
            return crypto.byte_array_to_base64(enc_data)
        elif encrypted_data_encryption_key == "-":
            # Skip encryption and just encode workorder data to
                        # base64 format.
            enc_data = crypto.byte_array_to_base64(data)
            return enc_data
        else:
            enc_data = crypto_utility.encrypt_data(
                            data, encrypted_data_encryption_key, data_iv)
            return crypto.byte_array_to_base64(enc_data)

    def to_jrpc_string(self, id):
        """
        Create a JRPC request in string format using
        the work order params_obj.

        Parameters:
        id         JRPC request ID

        Returns:
        Work order JRPC request as a string.
        """
        json_request = {
            "jsonrpc": "2.0",
            "method": "WorkOrderSubmit",
            "id": id,
            "params": self.params_obj
        }
        return json.dumps(json_request, indent=4)

    def to_string(self):
        """
        Create work order request string.
        It is used to submit a work order.

        Returns:
        Work order request as a string
        """
        return json.dumps(self.params_obj, indent=4)
