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
import zmq
import logging
import random
import json
import secrets
import hashlib
import avalon_crypto_utils.worker_encryption as worker_encryption
import avalon_crypto_utils.worker_signing as worker_signing
import avalon_crypto_utils.worker_hash as worker_hash
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# -------------------------------------------------------------------------


# Test file to send work orders to Graphene python worker
def main(argv):
    if len(argv) >= 1:
        work_order_json_file = str(argv[0])
    else:
        work_order_json_file = None
    # create zmq socket context
    context = zmq.Context()
    # zmq_url hardcoded to docker container host url
    # TODO: Read it from config file
    zmq_url = "tcp://process-work-order:7777"
    socket = context.socket(zmq.REQ)
    socket.connect(zmq_url)
    # Get worker details
    json_request = _create_json_request("ProcessWorkerSignup",
                                        None)
    worker_signup = _send_request_zmq(socket,
                                      json.dumps(json_request))
    logger.info("worker_signup = {}".format(worker_signup))
    worker_signup_json = json.loads(worker_signup)
    # Generate work orders.
    work_orders = _generate_work_orders(work_order_json_file)
    if work_orders is None:
        logger.warn("No work orders to execute")
    else:
        # Execute work orders.
        for wo in work_orders:
            workload_id, input_data_str = wo
            # Send work order request.
            _send_work_order_request(workload_id, input_data_str,
                                     worker_signup_json, socket)
            # sleep for 3 sec
            logger.info("Sleeping for 3 seconds")
            time.sleep(3)

    # Destroy zmq context
    socket.disconnect(zmq_url)
    context.destroy()

# -------------------------------------------------------------------------


def _generate_work_orders(wo_file):
    try:
        if wo_file is None:
            # use default work order file.
            wo_file = "test_work_orders.json"
        logger.info("work order json file : {}".format(wo_file))
        # Read work orders from file.
        with open(wo_file, "rb") as file:
            work_orders_json = json.load(file)
    except Exception as e:
        logger.error("Loading work orders failed" + str(e))
        return None
    if "workOrders" not in work_orders_json:
        logger.warn("No work orders present in file {}".format(wo_file))
        return None
    work_orders = work_orders_json["workOrders"]
    work_order_list = []
    for wo in work_orders:
        if "workloadId" not in wo:
            # skip this work order.
            continue
        workload_id = wo["workloadId"]
        if "params" in wo:
            param_str = wo["params"]
        else:
            param_str = None
        # Each item in a list is a tuple (workload_id, work_load_param).
        work_order_list.append((workload_id, param_str))
    # Return work order list.
    return work_order_list

# -------------------------------------------------------------------------


def _send_work_order_request(workload_id, input_data_str,
                             worker_signup_json, socket):
    # Generate session key and iv
    (session_key, session_key_iv) = _generate_session_key_iv()
    # Create work order request
    input_json_str = _create_work_order_request(workload_id,
                                                input_data_str,
                                                session_key,
                                                session_key_iv,
                                                worker_signup_json)
    json_request = _create_json_request("ProcessWorkOrder",
                                        input_json_str)
    # Send work order
    logger.info("Send work order request via zmq\n")
    response = _send_request_zmq(socket, json.dumps(json_request))
    # Parse response
    response_json = json.loads(response)
    # check work order response
    if "result" in response_json:
        # Verify response signature
        sign = worker_signing.WorkerSign()
        worker_verify_key = worker_signup_json["verifying_key"]
        worker_verify_key_bytes = worker_verify_key.encode("UTF-8")
        verify = sign._verify_wo_response_signature(
            response_json['result'], worker_verify_key_bytes)
        if verify:
            logger.info("Work order result verification success")
            decrypt_out_message = _get_work_order_result(response_json,
                                                         session_key,
                                                         session_key_iv)
            logger.info("Work order result : {}".format(decrypt_out_message))
        else:
            logger.error("Work order result verification fail")
    elif "error" in response_json:
        logger.error("Work order execution failed")

# -------------------------------------------------------------------------


def _send_request_zmq(socket, data_str):
    try:
        # socket = context.socket(zmq.REQ)
        # socket.connect(zmq_url)
        socket.send_string(data_str, flags=0, encoding='utf-8')
        # wait for reply
        replymessage = socket.recv_string(flags=0, encoding='utf-8')
        # socket.disconnect(zmq_url)
    except Exception as ex:
        replymessage = "Error while processing work order"
        logger.error("Exception: {} args {} details {}"
                     .format(type(ex), ex.args, ex))
    return replymessage

# -------------------------------------------------------------------------


def _create_json_request(method_name, params):
    json_request = {}
    json_request["jsonrpc"] = "2.0"
    json_request["id"] = random.randint(0, 100000)
    json_request["method"] = method_name
    json_request["params"] = params
    return json_request

# -------------------------------------------------------------------------


def _generate_session_key_iv():
    encrypt = worker_encryption.WorkerEncrypt()
    session_key = encrypt.generate_session_key()
    session_key_iv = encrypt.generate_iv()
    return (session_key, session_key_iv)

# -------------------------------------------------------------------------


def _create_work_order_request(workload_id, input_data_str,
                               session_key, session_key_iv,
                               worker_signup_json):
    worker_enc_key_str = worker_signup_json["encryption_key"]

    encrypt = worker_encryption.WorkerEncrypt()
    encrypted_session_key = encrypt.encrypt_session_key(
        session_key, worker_enc_key_str)

    msg_bytes = input_data_str.encode('UTF-8')

    input_json = dict()
    input_json["jsonrpc"] = "2.0"
    input_json["method"] = "WorkOrderSubmit"
    input_json["id"] = "1"
    input_json["params"] = dict()
    input_json["params"]["encryptedSessionKey"] = encrypted_session_key.hex()
    if session_key_iv:
        input_json["params"]["sessionKeyIv"] = session_key_iv.hex()
    input_json["params"]["workloadId"] = workload_id.encode("UTF-8").hex()
    input_json["params"]["workOrderId"] = secrets.token_hex(32)
    worker_id = hashlib.sha256("graphene-hello".encode("UTF-8")).hexdigest()
    input_json["params"]["workerId"] = worker_id
    input_json["params"]["requesterId"] = secrets.token_hex(32)
    input_json["params"]["requesterNonce"] = secrets.token_hex(32)

    in_data = dict()
    in_data["index"] = 0
    in_data["dataHash"] = ""
    in_data["data"] = msg_bytes
    in_data["encryptedDataEncryptionKey"] = "null"
    in_data["iv"] = ""
    input_json["params"]["inData"] = [in_data]

    # Encrypt inData
    encrypt.encrypt_work_order_data_json(input_json["params"]["inData"],
                                         session_key, session_key_iv)

    req_hash = worker_hash.WorkerHash().calculate_request_hash(
        input_json["params"])
    encrypted_req_hash = encrypt.encrypt_data(req_hash,
                                              session_key, session_key_iv)
    input_json["params"]["encryptedRequestHash"] = encrypted_req_hash.hex()

    return json.dumps(input_json)

# -------------------------------------------------------------------------


def _get_work_order_result(response_json, session_key, session_key_iv):
    encrypt = worker_encryption.WorkerEncrypt()
    encrypt.decrypt_work_order_data_json(response_json["result"]["outData"],
                                         session_key, session_key_iv)
    decrypted_out_bytes = response_json["result"]["outData"][0]["data"]
    decrypted_out_msg = decrypted_out_bytes.decode("UTF-8")
    return decrypted_out_msg

# -------------------------------------------------------------------------


if __name__ == '__main__':
    main(sys.argv[1:])
