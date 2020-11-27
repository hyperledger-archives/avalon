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

import argparse
import sys
import logging
import base64
import json
from hashlib import sha256

from utility.hex_utils import byte_array_to_hex_str, hex_to_byte_array
import avalon_worker.receive_request as receive_request
import avalon_crypto_utils.crypto_utility as crypto_utility
from avalon_worker.base_work_order_processor import BaseWorkOrderProcessor
from avalon_worker.error_code import WorkerError
import avalon_crypto_utils.worker_hash as worker_hash
import avalon_crypto_utils.worker_signing as worker_signing
import avalon_worker.utility.jrpc_utility as jrpc_utility
from utility.hex_utils import byte_array_to_hex_str, hex_to_byte_array

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# -------------------------------------------------------------------------


def main(args=None):
    """
    Graphene WPE worker main function.
    """
    # Parse command line parameters.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--bind', help='URI to listen for requests ', type=str)
    parser.add_argument(
        '--workload', help='JSON file which has workload module details',
        type=str)
    (options, remainder) = parser.parse_known_args(args)
    # Get the workload JSON file name passed in command line.
    if options.workload:
        workload_json_file = options.workload
    else:
        # Default file name.
        workload_json_file = "workloads.json"
    # Create work order processor object.
    wo_processor = WPEWorkOrderProcessor(workload_json_file)
    # Setup ZMQ channel to receive work order.
    if options.bind:
        zmq_bind_url = options.bind
    else:
        # default url. "*" means bind on all available interfaces.
        zmq_bind_url = "tcp://*:7777"
    zmq_socket = receive_request.ZmqSocket(zmq_bind_url, wo_processor)
    logger.info("Listening for requests at url {}".format(zmq_bind_url))
    # Start listener and wait for new request.
    zmq_socket.start_zmq_listener()


class WPEWorkOrderProcessor(BaseWorkOrderProcessor):
    """
    Graphene work order processing class.
    """

# -------------------------------------------------------------------------

    def __init__(self, workload_json_file):
        super().__init__(workload_json_file)

# -------------------------------------------------------------------------

    def _process_work_order(self, input_json_str, pre_processed_json_str):
        """
        Process Avalon work order and returns JSON RPC response

        Parameters :
            input_json_str: JSON formatted work order request string.
                            work order JSON is formatted as per
                            TC spec ver 1.1 section 6.
            pre_processed_json_str: JSON formatted work order request
                            pre-processed by KME worker. The keys present in
                            the json will be used to process original
                            work order request by WPE worker.
        Returns :
            JSON RPC response containing result or error.
        """
        try:
            input_json = json.loads(input_json_str)
            pre_proc_json = json.loads(
                pre_processed_json_str.split('\x00', 1)[0])
        except Exception as ex:
            err_code = WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE
            err_msg = "Error loading JSON: " + str(ex)
            error_json = jrpc_utility.create_error_response(
                err_code, 0, err_msg)
            return json.dumps(error_json)

        try:
            # Process pre-processed work order keys
            self.pre_proc_wo_keys = \
                self.process_pre_proc_work_order_keys(pre_proc_json)
        except Exception as ex:
            err_code = WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE
            err_msg = "Error Parsing pre-processed work order keys: " + str(ex)
            error_json = jrpc_utility.create_error_response(
                err_code, 0, err_msg)
            return json.dumps(error_json)

        # Decrypt session key
        session_key = self.pre_proc_wo_keys['session_key']
        session_key_iv = None
        if "sessionKeyIv" in input_json["params"]:
            session_key_iv_hex = input_json["params"]["sessionKeyIv"]
            session_key_iv = bytes.fromhex(session_key_iv_hex)
        # Verify work order integrity
        res = self._verify_work_order_request(input_json, session_key,
                                              session_key_iv)
        if res is False:
            err_code = WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE
            err_msg = "Work order integrity check failed"
            logger.error(err_msg)
            jrpc_id = input_json["id"]
            error_json = jrpc_utility.create_error_response(
                err_code, jrpc_id, err_msg)
            return json.dumps(error_json)
        else:
            logger.info("Verify work order request success")

        # Replace in-data and out-data keys in the client work order request
        # with decrypted keys from pre-processed work order keys
        index = 0
        in_data_keys = self.pre_proc_wo_keys['input-data-keys']
        for in_data in input_json["params"]["inData"]:
            if 'encryptedDataEncryptionKey' in in_data:
                e_key = in_data['encryptedDataEncryptionKey']
                if e_key and e_key != "null" and e_key != "-":
                    in_data['encryptedDataEncryptionKey'] = \
                        in_data_keys[index]['data-key']
                    index += 1

        # Decrypt work order inData
        in_data_array = input_json["params"]["inData"]
        self.encrypt.decrypt_work_order_data_json(in_data_array,
                                                  session_key,
                                                  session_key_iv)
        # Process workload
        workload_id_hex = input_json["params"]["workloadId"]
        workload_id = bytes.fromhex(workload_id_hex).decode("UTF-8")
        in_data_array = input_json["params"]["inData"]
        result, out_data = self.wl_processor.execute_workload(workload_id,
                                                              in_data_array)
        # Generate work order response
        if result is True:
            output_json = self._create_work_order_response(
                input_json, out_data, session_key, session_key_iv)
            output_json = self._encrypt_and_sign_response(
                session_key, session_key_iv, output_json)
        else:
            jrpc_id = input_json["id"]
            err_code = WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE
            err_msg = "Error processing work load"
            output_json = jrpc_utility.create_error_response(err_code,
                                                             jrpc_id,
                                                             err_msg)
        # return json str
        output_json_str = json.dumps(output_json)
        return output_json_str

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
        output_json = super()._create_work_order_response(
            input_json, out_data, session_key, session_key_iv)
        output_json["result"]["extVerificationKey"] = \
            self.pre_proc_wo_keys['verification_key']
        output_json["result"]["extVerificationKeySignature"] = \
            self.pre_proc_wo_keys['verification_key_sig']
        return output_json


# -------------------------------------------------------------------------
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
        # Encrypt outData
        self.encrypt.encrypt_work_order_data_json(
            output_json["result"]["outData"],
            session_key,
            session_key_iv)
        # Compute worker signature
        res_hash = worker_hash.WorkerHash().calculate_response_hash(
            output_json["result"])
        # Get PEM encoded signing key from bytes
        signing_key_str = self.pre_proc_wo_keys['signing_key'].decode('utf-8')
        self.sign = worker_signing.WorkerSign()
        res_hash_sign = self.sign.sign_message(res_hash, signing_key_str)
        res_hash_sign_b64 = crypto_utility.byte_array_to_base64(res_hash_sign)
        output_json["result"]["workerSignature"] = res_hash_sign_b64

        return output_json

# -------------------------------------------------------------------------

    def unpack(self, wo_key, sym_key):
        index = wo_key['index']
        encrypted_data_key = wo_key['encrypted-data-key']

        if not encrypted_data_key or encrypted_data_key == '-'\
                or encrypted_data_key == 'null':
            return
        data_key = self.encrypt.decrypt_data(
            base64.b64decode(encrypted_data_key), sym_key)
        return index, data_key

# -------------------------------------------------------------------------

    def process_pre_proc_work_order_keys(self, pre_proc_json):
        """
        Process work order keys in pre-processed JSON(by KME worker)

        Parameters:
            pre_proc_json: Pre processed JSON(by KME worker) having work order
                           keys needed in encrypted format to process client
                           work order request
        Returns:
            processed_wo_keys: JSON object with all necessary
                               work order keys in plain
        """
        self.processed_wo_keys = {}
        try:
            # Parse and decrypt encrypted one-time symmetric key generated
            # by KME per work order request
            self.encrypted_sym_key = base64.b64decode(
                pre_proc_json['encrypted-sym-key'])
            sym_key = self.encrypt.decrypt_session_key(self.encrypted_sym_key)

            # Parse and decrypt work order session_key
            # encrypted by KME using sym_key
            self.encrypted_wo_key = base64.b64decode(
                pre_proc_json['encrypted-wo-key'])
            self.processed_wo_keys['session_key'] = self.encrypt.decrypt_data(
                self.encrypted_wo_key, sym_key)

            # Parse and decrypt encrypted_signing_key
            self.encrypted_sig_key = base64.b64decode(
                pre_proc_json['encrypted-wo-signing-key'])
            self.processed_wo_keys['signing_key'] = self.encrypt.decrypt_data(
                self.encrypted_sig_key, sym_key)

            # Parse verification_key corresponding to signing_key to
            # verify final work order response
            self.processed_wo_keys['verification_key'] = \
                pre_proc_json['wo-verification-key']

            # Parse verification key signature obtained by signing
            # verification_key using KME private signing key
            self.processed_wo_keys['verification_key_sig'] = \
                pre_proc_json['wo-verification-key-sig']

            signature = base64.b64decode(pre_proc_json['signature'])

            # Parse and decrypt work order in-data keys and out-data keys
            in_data_keys = pre_proc_json['input-data-keys']
            wo_in_data_keys = []
            for key in in_data_keys:
                wo_in_data_key = {}
                wo_in_data_key['index'], wo_in_data_key['data-key'] = \
                    self.unpack(key, sym_key)
                wo_in_data_keys.append(wo_in_data_key)
            self.processed_wo_keys['input-data-keys'] = wo_in_data_keys

            out_data_keys = pre_proc_json['output-data-keys']
            wo_out_data_keys = []
            for key in out_data_keys:
                wo_out_data_key = {}
                wo_out_data_key['index'], wo_out_data_key['data-key'] = \
                    self.unpack(key, sym_key)
                wo_out_data_keys.append(wo_out_data_key)
            self.processed_wo_keys['output-data-keys'] = wo_out_data_keys
        except Exception as ex:
            logger.exception("Failed to parse and decrypt"
                             + " pre-processed work order keys %s", ex)
            err_code = WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE
            err_msg = "Error loading JSON: " + str(ex)
            error_json = jrpc_utility.create_error_response(err_code,
                                                            0,
                                                            err_msg)
            return json.dumps(error_json)
        try:
            result = self.verify_wo_keys_signature(signature, pre_proc_json)
            if result != 0:
                logger.error("Failed to verify signature of"
                             + " pre-processed work order keys")
                raise Exception("Failed to verify signature of " +
                                "pre-processed work order keys")
        except Exception as ex:
            logger.exception("Failed to verify signature of"
                             + " pre-processed work order keys %s", ex)
            raise ex
        return self.processed_wo_keys

# -------------------------------------------------------------------------

    def calculate_wo_pre_proc_keys_hash(self, pre_proc_json):
        """
        Computes hash on pre-processed work order keys(by KME worker)

        Parameters:
            pre_proc_json: Pre processed JSON(by KME worker) having work order
                           keys needed in encrypted format to process client
                           work order request
        Returns:
            Computed hash of pre-processed work order keys in bytes
        """
        concat_hash = crypto_utility.byte_array_to_base64(
            self.encrypted_sym_key) + \
            crypto_utility.byte_array_to_base64(self.encrypted_wo_key) + \
            crypto_utility.byte_array_to_base64(self.encrypted_sig_key)
        hash_1 = worker_hash.WorkerHash().compute_message_hash(
            concat_hash.encode("utf-8"))
        hash_1_str = crypto_utility.byte_array_to_base64(hash_1)

        # Compute hash of input-data-keys
        in_data_key_hash_str = ""
        for key in pre_proc_json['input-data-keys']:
            in_data_key_hash_str += crypto_utility.byte_array_to_base64(
                worker_hash.WorkerHash().compute_message_hash(
                    crypto_utility.base64_to_byte_array(
                        key['encrypted-data-key'])))

        # Compute hash on output-data-keys
        out_data_key_hash_str = ""
        for key in pre_proc_json['output-data-keys']:
            out_data_key_hash_str += crypto_utility.byte_array_to_base64(
                worker_hash.WorkerHash().compute_message_hash(
                    crypto_utility.base64_to_byte_array(
                        key['encrypted-data-key'])))

        final_hash = hash_1_str.encode("utf-8") + \
            in_data_key_hash_str.encode("utf-8") + \
            out_data_key_hash_str.encode("utf-8")
        return worker_hash.WorkerHash().compute_message_hash(final_hash)


# -------------------------------------------------------------------------

    def verify_wo_keys_signature(self, signature, pre_proc_json):
        """
        Verifies signature of pre-processed work order keys(by KME worker)

        Parameters:
            signature: Digital signature in bytes computed on
                       pre-processed work order keys
            pre_proc_json: Pre processed JSON(by KME worker) having work order
                           keys needed in encrypted format to process client
                           work order request
        Returns:
            0 on successful signature verification, -1 on failure
        """
        wo_keys_hash = self.calculate_wo_pre_proc_keys_hash(pre_proc_json)
        uid_pem_bytes = hex_to_byte_array(self.uid)
        result = self.sign.verify_signature_from_pubkey(
            signature, wo_keys_hash, uid_pem_bytes)
        return 0 if result is True else -1

# -------------------------------------------------------------------------

    def _handle_methods(self, method_name, params):
        """
        Invoke request handling as per method name.

        Parameters :
            method_name: name of method received in request
            params: Parameters received in request
        Returns :
            JSON RPC response containing result or None for method not found.
        """
        output = None
        # Process worker signup/work order
        if (method_name == "ProcessWorkerSignup"):
            output = self._process_worker_signup(
                params["uniqueVerificationKey"])
            # Save Unique ID useful while verifying the signature of
            # preprocessed work order keys
            self.uid = params["uniqueVerificationKey"]
        elif (method_name == "ProcessWorkOrder"):
            output = self._process_work_order(params[0], params[1])
        elif (method_name == "GenerateNonce"):
            output = self._generate_nonce(params)
        elif (method_name == "VerifyUniqueIdSignature"):
            output = self._verfify_uid_signature(params)

        return output


# -------------------------------------------------------------------------

    def _generate_nonce(self, params):
        """
        Generate nonce of length specified in params.

        Parameters :
            params: Parameters received in request
        Returns :
            JSON RPC response containing requested nonce.
        """
        nonce_size = params["nonce_size"]
        # Generate random bytes of size equivalent to nonce_size/2,
        # so that when encoded to hex string results in string of
        # size equal to nonce_size
        nonce_bytes = crypto_utility.generate_random_bytes(int(nonce_size/2))
        # Convert nonce to hex string and persist in the EnclaveData
        self._nonce = byte_array_to_hex_str(nonce_bytes)
        return json.dumps({"nonce": self._nonce})


# -------------------------------------------------------------------------

    def _verfify_uid_signature(self, params):
        """
        Verify uid signature received from KME.

        Parameters :
            params: Parameters received in request
        Returns :
            JSON RPC response containing uid signature verification result.
        """
        # Public key generated by KME to be used for registration
        verify_key = params["uniqueVerificationKey"]
        # Digital signature computed on  hash of concatenated
        # string of unique id and nonce
        verify_key_sig = params["uniqueVerificationKeySignature"]

        verify_key_sig_bytes = hex_to_byte_array(verify_key_sig)
        verify_key_bytes = hex_to_byte_array(verify_key)
        b64_verify_key = verify_key_bytes.decode("utf-8")
        concat_str = b64_verify_key + self._nonce
        str_hash = worker_hash.WorkerHash().compute_message_hash(
            concat_str.encode("utf-8"))

        result = self.sign.verify_signature_from_pubkey(
            verify_key_sig_bytes, str_hash, verify_key_bytes)
        verification_result = 0 if result is True else -1
        return json.dumps({"verification_result": verification_result})

# -------------------------------------------------------------------------

    def _get_quote(self, unique_id):
        """
        Get SGX quote of worker enclave.

        Parameters:
            unique_id : Unique identifier retrived from KME worker
        Returns :
            SGX quote value of worker enclave as base64 encoded string.
            If Intel SGX environment is not present returns empty string.
        """
        # Write user report data.
        # First 32 bytes of report data has SHA256 hash of worker's
        # public signing key. Next 32 bytes is filled with Zero.
        pub_enc_key_hash = sha256(self.worker_public_enc_key).digest()
        unique_id_hash = sha256(unique_id.encode('utf-8')).digest()
        user_data = pub_enc_key_hash + unique_id_hash
        ret = self.sgx_attestation.write_user_report_data(user_data)
        # Get quote
        if ret:
            quote_str = self.sgx_attestation.get_quote()
        else:
            quote_str = ""
        # Return quote.
        return quote_str


main()
