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

import os
import sys
import time
import argparse
import random
import json
import logging
import secrets

from http_client.http_jrpc_client import HttpJrpcClient

import avalon_crypto_utils.worker_encryption as worker_encryption
import avalon_crypto_utils.worker_signing as worker_signing
import avalon_crypto_utils.worker_hash as worker_hash
import avalon_crypto_utils.crypto_utility as crypto_utility

import avalon_sdk.worker.worker_details as worker
import utility.file_utils as futils
from error_code.error_status import SignatureStatus, WorkOrderStatus

LOGGER = logging.getLogger(__name__)

TCFHOME = os.environ.get("TCF_HOME", "../../")
NO_OF_BYTES = 16


# -----------------------------------------------------------------
def local_main(config):
    global input_json_str
    if not input_json_str and not input_json_dir:
        LOGGER.error("JSON input file is not provided")
        exit(1)

    if not output_json_file_name:
        LOGGER.error("JSON output file is not provided")
        exit(1)

    if not server_uri:
        LOGGER.error("Server URI is not provided")
        exit(1)

    LOGGER.info("Execute work order")
    uri_client = HttpJrpcClient(server_uri)
    response = None
    wo_id = None
    if input_json_dir:
        directory = os.fsencode(input_json_dir)
        files = os.listdir(directory)

        for file in sorted(files):
            LOGGER.info("---------------- Input file name: %s -------------\n",
                        file.decode("utf-8"))
            input_json_str = futils.read_json_file(
                (directory.decode("utf-8") + file.decode("utf-8")))
            # -----------------------------------------------------------------

            # If Client request is WorkOrderSubmit, a requester payload's
            # signature with the requester private signing key is generated.
            if "WorkOrderSubmit" in input_json_str:
                # Update workOrderId , workerId and workloadId
                input_json_obj = json.loads(input_json_str)
                wo_id = hex(random.randint(1, 2**64 - 1))
                input_json_obj["params"]["workOrderId"] = wo_id
                input_json_obj["params"]["workerId"] = worker_id

                # Convert workloadId to a hex string and update the request
                workload_id = input_json_obj["params"]["workloadId"]
                workload_id_hex = workload_id.encode("UTF-8").hex()
                input_json_obj["params"]["workloadId"] = workload_id_hex

                encrypt = worker_encryption.WorkerEncrypt()
                # Generate session key, session iv and encrypted session key
                session_key = encrypt.generate_session_key()
                session_iv = encrypt.generate_iv()
                encrypted_session_key = encrypt.encrypt_session_key(
                    session_key, worker_obj.encryption_key)

                input_json_obj["params"]["encryptedSessionKey"] = \
                    crypto_utility.byte_array_to_hex(encrypted_session_key)
                input_json_obj["params"]["sessionKeyIv"] = \
                    crypto_utility.byte_array_to_hex(session_iv)

                if "requesterNonce" in input_json_obj["params"]:
                    if len(input_json_obj["params"]["requesterNonce"]) == 0:
                        # [NO_OF_BYTES] 16 BYTES for nonce.
                        # This is the recommendation by NIST to
                        # avoid collisions by the "Birthday Paradox".
                        requester_nonce = secrets.token_hex(NO_OF_BYTES)
                        input_json_obj["params"]["requesterNonce"] = \
                            requester_nonce
                requester_nonce = input_json_obj["params"]["requesterNonce"]

                # Encode data in inData
                for data_obj in input_json_obj["params"]["inData"]:
                    encoded_data = data_obj["data"].encode('UTF-8')
                    data_obj["data"] = encoded_data

                # Encrypt inData
                encrypt.encrypt_work_order_data_json(
                    input_json_obj["params"]["inData"], session_key,
                    session_iv)
                req_hash = worker_hash.WorkerHash().calculate_request_hash(
                    input_json_obj["params"])
                encrypted_req_hash = encrypt.encrypt_data(
                    req_hash, session_key, session_iv)
                input_json_obj["params"]["encryptedRequestHash"] = \
                    encrypted_req_hash.hex()
                signer = worker_signing.WorkerSign()
                signer.generate_signing_key()
                wo_req_sig = signer.sign_message(req_hash)
                input_json_obj["params"]["requesterSignature"] = \
                    crypto_utility.byte_array_to_base64(wo_req_sig)
                input_json_obj["params"]["verifyingKey"] = \
                    signer.get_public_sign_key().decode('utf-8')
                input_json_str = json.dumps(input_json_obj)
                if input_json_str is None:
                    continue
            # -----------------------------------------------------------------

            # Update the worker ID
            if response:
                if "workerId" in input_json_str:
                    # Retrieve the worker id from the "WorkerRetrieve"
                    # response and update the worker id information for
                    # further json requests.
                    if "result" in response and \
                            "ids" in response["result"].keys() and \
                            len(response["result"]["ids"]) > 0:
                        input_json_final = json.loads(input_json_str)
                        worker_id = response["result"]["ids"][0]
                        input_json_final["params"]["workerId"] = worker_id
                        input_json_str = json.dumps(input_json_final)
                        LOGGER.info("********** Worker details Updated with "
                                    "Worker ID*********\n%s\n",
                                    input_json_str)

            # -----------------------------------------------------------------
            if "WorkOrderGetResult" in input_json_str or \
                    "WorkOrderReceiptRetrieve" in input_json_str:
                input_json_obj = json.loads(input_json_str)
                input_json_obj["params"]["workOrderId"] = wo_id
                input_json_str = json.dumps(input_json_obj)

            LOGGER.info("*********Request Json********* \n%s\n",
                        input_json_str)
            response = uri_client._postmsg(input_json_str)
            LOGGER.info("**********Received Response*********\n%s\n", response)

            # -----------------------------------------------------------------

            # Worker details are loaded into Worker_Obj
            if "WorkerRetrieve" in input_json_str and "result" in response:
                worker_obj.load_worker(response["result"]["details"])
            # -----------------------------------------------------------------

            # Poll for "WorkOrderGetResult" and break when you get the result
            while("WorkOrderGetResult" in input_json_str and
                    "result" not in response):
                if response["error"]["code"] != WorkOrderStatus.PENDING:
                    break
                response = uri_client._postmsg(input_json_str)
                LOGGER.info("Received Response: %s, \n \n ", response)
                time.sleep(3)

            # -----------------------------------------------------------------

            # Verify the signature
            if "WorkOrderGetResult" in input_json_str:
                if "error" in response:
                    # Response has error, hence skip Signature verification
                    LOGGER.info("Work order response has error; "
                                "skipping signature verification")
                    continue
                sig_bool = signer.verify_signature(
                    response['result'],
                    worker_obj.verification_key,
                    requester_nonce)
                try:
                    if sig_bool > 0:
                        LOGGER.info("Signature Verified")
                        encrypt.decrypt_work_order_data_json(
                            response['result']['outData'],
                            session_key, session_iv)
                    else:
                        LOGGER.info("Signature verification Failed")
                        exit(1)
                except Exception as e:
                    LOGGER.error("ERROR: Failed to verify signature of " +
                                 "work order response")
                    exit(1)

            # -----------------------------------------------------------------
    else:
        LOGGER.info("Input Request %s", input_json_str)
        response = uri_client._postmsg(input_json_str)
        LOGGER.info("Received Response: %s , \n \n ", response)

    exit(0)


# -----------------------------------------------------------------------------
def parse_command_line(config, args):
    LOGGER.info("***************** AVALON *****************")
    global input_json_str
    global input_json_dir
    global server_uri
    global output_json_file_name
    global worker_obj
    global worker_id
    global private_key
    global encrypted_session_key
    global session_iv
    global requester_nonce

    parser = argparse.ArgumentParser()
    parser.add_argument("--logfile", help="Name of the log file. " +
                        "Use __screen__ for standard output", type=str)
    parser.add_argument("-p", "--private_key",
                        help="Private Key of the Client",
                        type=str, default=None)
    parser.add_argument("--loglevel", help="Logging level", type=str)
    parser.add_argument("-i", "--input_file", help="JSON input file name",
                        type=str, default="input.json")
    parser.add_argument("--input_dir", help="Logging level", type=str,
                        default=[])
    parser.add_argument("-c", "--connect_uri",
                        help="URI to send requests to", type=str, default=[])
    parser.add_argument(
        "output_file",
        help="JSON output file name",
        type=str,
        default="output.json",
        nargs="?")

    options = parser.parse_args(args)

    if config.get("Logging") is None:
        config["Logging"] = {
            "LogFile": "__screen__",
            "LogLevel": "INFO"
        }
    if options.logfile:
        config["Logging"]["LogFile"] = options.logfile
    if options.loglevel:
        config["Logging"]["LogLevel"] = options.loglevel.upper()

    input_json_str = None
    input_json_dir = None

    if options.connect_uri:
        server_uri = options.connect_uri
    else:
        LOGGER.error("ERROR: Please enter the server URI")

    if options.input_dir:
        LOGGER.info("Load Json Directory from %s", options.input_dir)
        input_json_dir = options.input_dir
    elif options.input_file:
        try:
            LOGGER.info("load JSON input from %s", options.input_file)
            with open(options.input_file, "r") as file:
                input_json_str = file.read()
        except Exception as err:
            LOGGER.error("ERROR: Failed to read from file %s: %s",
                         options.input_file, str(err))
    else:
        LOGGER.info("No input found")

    if options.output_file:
        output_json_file_name = options.output_file
    else:
        output_json_file_name = None

    if options.private_key:
        private_key = options.private_key
    else:
        # Generating the private Key for the client
        private_key = worker_signing.WorkerSign().generate_signing_key()

    # Initializing Worker Object
    worker_obj = worker.SGXWorkerDetails()


# -----------------------------------------------------------------------------
def Main(args=None):
    import config.config as pconfig
    import utility.logger as plogger

    # parse out the configuration file first
    conffiles = ["tcs_config.toml"]
    confpaths = [".", TCFHOME + "/config", "../../etc"]

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="configuration file", nargs="+")
    parser.add_argument("--config-dir", help="configuration folder", nargs="+")
    (options, remainder) = parser.parse_known_args(args)

    if options.config:
        conffiles = options.config

    if options.config_dir:
        confpaths = options.config_dir

    try:
        config = pconfig.parse_configuration_files(conffiles, confpaths)
        json.dumps(config, indent=4)
    except pconfig.ConfigurationException as e:
        LOGGER.error(str(e))
        sys.exit(-1)

    plogger.setup_loggers(config.get("Logging", {}))
    sys.stdout = plogger.stream_to_logger(logging.getLogger("STDOUT"),
                                          logging.DEBUG)
    sys.stderr = plogger.stream_to_logger(logging.getLogger("STDERR"),
                                          logging.WARN)

    parse_command_line(config, remainder)
    local_main(config)


# -----------------------------------------------------------------------------
Main()
