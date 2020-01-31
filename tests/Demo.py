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


import crypto_utils.signature as signature
import avalon_sdk.worker.worker_details as worker
import crypto_utils.crypto_utility as enclave_helper
import utility.file_utils as futils
from error_code.error_status import SignatureStatus
from avalon_sdk.worker.worker_details import WorkerType
from avalon_sdk.direct.jrpc.jrpc_worker_registry import \
    JRPCWorkerRegistryImpl
from avalon_sdk.direct.jrpc.jrpc_work_order import \
    JRPCWorkOrderImpl
from error_code.error_status import WorkOrderStatus


# Remove duplicate loggers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
LOGGER = logging.getLogger(__name__)

TCFHOME = os.environ.get("TCF_HOME", "../../")


# -----------------------------------------------------------------
# -----------------------------------------------------------------
def local_main(config):
    if not input_json_str and not input_json_dir:
        LOGGER.error("JSON input file is not provided")
        exit(1)

    if not output_json_file_name:
        LOGGER.error("JSON output file is not provided")
        exit(1)

    if not config["tcf"]["json_rpc_uri"]:
        LOGGER.error("URI is not provided")
        exit(1)

    LOGGER.info("Execute work order")
    response = None
    wo_id = None
    if input_json_dir:
        directory = os.fsencode(input_json_dir)
        files = os.listdir(directory)

        for file in sorted(files):
            LOGGER.info("---------------- Input file name: %s -------------\n",
                        file.decode("utf-8"))
            input_json_str1 = futils.read_json_file(
                (directory.decode("utf-8") + file.decode("utf-8")))
            # -----------------------------------------------------------------

            # If Client request is WorkOrderSubmit, a requester payload's
            # signature with the requester private signing key is generated.
            if "WorkOrderSubmit" in input_json_str1:
                # Update workOrderId , workerId and workloadId
                input_json_obj = json.loads(input_json_str1)
                wo_id = hex(random.randint(1, 2**64 - 1))
                input_json_obj["params"]["workOrderId"] = wo_id
                input_json_obj["params"]["workerId"] = worker_obj.worker_id
                # Convert workloadId to a hex string and update the request
                workload_id = input_json_obj["params"]["workloadId"]
                workload_id_hex = workload_id.encode("UTF-8").hex()
                input_json_obj["params"]["workloadId"] = workload_id_hex
                input_json_str1 = json.dumps(input_json_obj)

                # Generate session iv an encrypted session key
                session_iv = enclave_helper.generate_iv()
                session_key = enclave_helper.generate_key()
                encrypted_session_key = enclave_helper.generate_encrypted_key(
                    session_key, worker_obj.encryption_key)

                input_json_str1, status = sig_obj.generate_client_signature(
                    input_json_str1, worker_obj, private_key, session_key,
                    session_iv, encrypted_session_key)
                if status != SignatureStatus.PASSED:
                    LOGGER.info("Generate signature failed\n")
                    exit(1)
                if input_json_str1 is None:
                    continue

                # Submit work order
                input_json_obj = json.loads(input_json_str1)
                work_order_params = input_json_obj["params"]
                work_order_request = json.dumps(work_order_params)
                work_order = JRPCWorkOrderImpl(config)
                jrpc_req_id = input_json_obj['id']
                jrpc_req_id += 1
                work_order_id = input_json_obj["params"]["workOrderId"]
                requester_id = input_json_obj["params"]["requesterId"]
                worker_id = input_json_obj["params"]["workerId"]

                response = work_order.work_order_submit(
                    work_order_id,
                    worker_id,
                    requester_id,
                    work_order_request,
                    id=jrpc_req_id
                )

                LOGGER.info("Work order submit response : {}\n ".format(
                    json.dumps(response, indent=2)
                ))

            # -----------------------------------------------------------------
            # Update the worker ID
            if response:
                if "workerId" in input_json_str1:
                    # Retrieve the worker id from the "WorkerRetrieve"
                    # response and update the worker id information for
                    # further json requests.
                    if "result" in response and \
                            "ids" in response["result"].keys():
                        input_json_final = json.loads(input_json_str1)
                        worker_id = response["result"]["ids"][0]
                        input_json_final["params"]["workerId"] = worker_id
                        input_json_str1 = json.dumps(input_json_final)
                        LOGGER.info("********** Worker details Updated with "
                                    "Worker ID*********\n%s\n",
                                    input_json_str1)
                        # Retrieve worker details
                        LOGGER.info("****Request Json**** \n%s\n",
                                    input_json_str1)
                        worker_registry = JRPCWorkerRegistryImpl(config)
                        jrpc_req_id = input_json_final['id']
                        jrpc_req_id += 1
                        response = worker_registry.worker_retrieve(
                            worker_id, jrpc_req_id
                        )
                        LOGGER.info("******Received Response******\n%s\n",
                                    response)
            # -----------------------------------------------------------------

            # Worker details are loaded into Worker_Obj
            if "WorkerRetrieve" in input_json_str1 and "result" in response:
                worker_obj.load_worker(response)
            # -----------------------------------------------------------------
            if "WorkOrderGetResult" in input_json_str1 or \
                    "WorkOrderReceiptRetrieve" in input_json_str1:
                input_json_obj = json.loads(input_json_str1)
                input_json_obj["params"]["workOrderId"] = wo_id
                input_json_str1 = json.dumps(input_json_obj)
                input_json_obj = json.loads(input_json_str1)
                jrpc_req_id = input_json_obj['id']
                jrpc_req_id += 1
                wo_id = input_json_obj["params"]["workOrderId"]
                LOGGER.info("*********Request Json********* \n%s\n",
                            input_json_str1)
                work_order = JRPCWorkOrderImpl(config)
                response = work_order.work_order_get_result(wo_id, jrpc_req_id)
                LOGGER.info("*******Received Response*******: %s, \n \n ",
                            response)
            # -----------------------------------------------------------------
            if "WorkerLookUp" in input_json_str1:
                input_json_obj = json.loads(input_json_str1)
                # Prepare worker
                # Read JRPC ID from JSON
                LOGGER.info("********Request Json********* \n%s\n",
                            input_json_str1)
                jrpc_req_id = input_json_obj['id']
                worker_registry = JRPCWorkerRegistryImpl(config)
                # Get first worker from worker registry
                response = worker_registry.worker_lookup(
                    worker_type=WorkerType.TEE_SGX, id=jrpc_req_id
                )
                LOGGER.info("**********Received Response*********\n%s\n",
                            response)

            # -----------------------------------------------------------------

            # Poll for "WorkOrderGetResult" and break when you get the result
            while("WorkOrderGetResult" in input_json_str1 and
                    "result" not in response):
                if response["error"]["code"] != WorkOrderStatus.PENDING:
                    break

                input_json_obj = json.loads(input_json_str1)
                jrpc_req_id = input_json_obj['id']
                jrpc_req_id += 1
                wo_id = input_json_obj["params"]["workOrderId"]
                work_order = JRPCWorkOrderImpl(config)
                response = work_order.work_order_get_result(wo_id, jrpc_req_id)
                LOGGER.info("Received Response: %s, \n \n ", response)
                time.sleep(3)

            # -----------------------------------------------------------------

            # Verify the signature
            if "WorkOrderGetResult" in input_json_str1:
                if "error" in response:
                    # Response has error, hence skip Signature verification
                    LOGGER.info("Work order response has error; "
                                "skipping signature verification")
                    continue
                sig_bool = sig_obj.verify_signature(
                    response, worker_obj.verification_key)
                try:
                    if sig_bool > 0:
                        LOGGER.info("Signature Verified")
                        enclave_helper.decrypted_response(
                            response, session_key, session_iv)
                    else:
                        LOGGER.info("Signature verification Failed")
                        exit(1)
                except Exception as e:
                    LOGGER.error("ERROR: Failed to analyze " +
                                 "Signature Verification")
                    exit(1)

            # -----------------------------------------------------------------
    else:
        LOGGER.info("Input Request cannot be processed %s", input_json_str)

    exit(0)


# -----------------------------------------------------------------------------
def parse_command_line(config, args):
    LOGGER.info('************** TRUSTED COMPUTE FRAMEWORK (TCF) *************')
    global input_json_str
    global input_json_dir
    global server_uri
    global output_json_file_name
    global consensus_file_name
    global sig_obj
    global worker_obj
    global private_key
    global encrypted_session_key
    global session_iv

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

    input_json_str = None
    input_json_dir = None

    if options.connect_uri:
        config["tcf"]["json_rpc_uri"] = options.connect_uri
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
        private_key = enclave_helper.generate_signing_keys()

    # Initializing Signature object, Worker Object
    sig_obj = signature.ClientSignature()
    worker_obj = worker.SGXWorkerDetails()


# -----------------------------------------------------------------------------
def Main(args=None):
    import config.config as pconfig
    import utility.logger as plogger

    # parse out the configuration file first
    conffiles = [TCFHOME + "/sdk/avalon_sdk/tcf_connector.toml"]
    confpaths = ["."]

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

    # setup logging
    config["Logging"] = {
        "LogFile": "__screen__",
        "LogLevel": "INFO"
    }
    plogger.setup_loggers(config.get("Logging", {}))
    sys.stdout = plogger.stream_to_logger(logging.getLogger("STDOUT"),
                                          logging.DEBUG)
    sys.stderr = plogger.stream_to_logger(logging.getLogger("STDERR"),
                                          logging.WARN)

    parse_command_line(config, remainder)
    local_main(config)


# -----------------------------------------------------------------------------
Main()
