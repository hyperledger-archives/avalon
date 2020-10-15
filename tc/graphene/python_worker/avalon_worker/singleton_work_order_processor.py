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
import argparse
import json
import avalon_worker.receive_request as receive_request
import avalon_worker.crypto.worker_hash as worker_hash
from avalon_worker.base_work_order_processor import BaseWorkOrderProcessor
from avalon_worker.error_code import WorkerError
import avalon_worker.utility.jrpc_utility as jrpc_utility

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# -------------------------------------------------------------------------


def main(args=None):
    """
    Graphene worker main function.
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
    wo_processor = SingletonWorkOrderProcessor(workload_json_file)
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

# -------------------------------------------------------------------------


class SingletonWorkOrderProcessor(BaseWorkOrderProcessor):
    """
    Graphene work order processing class.
    """

# -------------------------------------------------------------------------

    def __init__(self, workload_json_file):
        super().__init__(workload_json_file)

# -------------------------------------------------------------------------

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
        try:
            input_json = json.loads(input_json_str)
        except Exception as ex:
            err_code = WorkerError.INVALID_PARAMETER_FORMAT_OR_VALUE
            err_msg = "Error loading JSON: " + str(ex)
            error_json = jrpc_utility.create_error_response(err_code,
                                                            0,
                                                            err_msg)
            return json.dumps(error_json)
        # Decrypt session key
        encrypted_session_key_hex = \
            input_json["params"]["encryptedSessionKey"]
        encrypted_session_key = bytes.fromhex(encrypted_session_key_hex)
        session_key = \
            self.encrypt.decrypt_session_key(encrypted_session_key)
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
            error_json = jrpc_utility.create_error_response(err_code,
                                                            jrpc_id,
                                                            err_msg)
            return json.dumps(error_json)
        else:
            logger.info("Verify work order request success")
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
            output_json = self._create_work_order_response(input_json,
                                                           out_data,
                                                           session_key,
                                                           session_key_iv)
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
        res_hash_sign = self.sign.sign_message(res_hash)
        res_hash_sign_b64 = self.encrypt.byte_array_to_base64(res_hash_sign)
        output_json["result"]["workerSignature"] = res_hash_sign_b64

        return output_json

# -------------------------------------------------------------------------


main()
