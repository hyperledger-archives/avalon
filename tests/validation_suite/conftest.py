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

import pytest
import time
import os
import sys
import argparse
import json
import logging

from automation_framework.worker_lookup.worker_lookup_params \
    import WorkerLookUp
from automation_framework.worker_retrieve.worker_retrieve_params \
    import WorkerRetrieve
from automation_framework.utilities.workflow import submit_request

import avalon_client_sdk.worker.worker_details as worker
import config.config as pconfig
from avalon_client_sdk.http_client.http_jrpc_client \
        import HttpJrpcClient
import utility.logger as plogger
import crypto_utils.crypto.crypto as crypto
import crypto_utils.crypto_utility as enclave_helper
import crypto_utils.crypto_utility as crypto_utils
from avalon_client_sdk.utility.tcf_types import WorkerType, WorkerStatus

TCFHOME = os.environ.get("TCF_HOME", "../../")
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def setup_config(args=None):
    """ Fixture to setup initial config for pytest session. """

    # parse out the configuration file first
    conffiles = ["tcs_config.toml"]
    confpaths = [".", TCFHOME + "/config"]

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="configuration file", nargs="+")
    parser.add_argument("--config-dir", help="configuration folder", nargs="+")
    parser.add_argument("--connect_uri", action="store",
                        default="http://localhost:1947",
                        help="server uri")
    (options, remainder) = parser.parse_known_args(args)

    if options.config:
        conffiles = options.config

    if options.config_dir:
        confpaths = options.config_dir

    if options.connect_uri:
        server_uri = options.connect_uri

    try:
        config = pconfig.parse_configuration_files(conffiles, confpaths)
        config_json_str = json.dumps(config, indent=4)
    except pconfig.ConfigurationException as e:
        logger.error(str(e))
        sys.exit(-1)

    plogger.setup_loggers(config.get("Logging", {}))
    sys.stdout = plogger.stream_to_logger((logging.getLogger("STDOUT"),
                                           logging.DEBUG))
    sys.stderr = plogger.stream_to_logger((logging.getLogger("STDERR"),
                                           logging.WARN))

    logger.info("configuration for the session: %s", config)
    uri_client = HttpJrpcClient(server_uri)

    # private_key of client
    private_key = enclave_helper.generate_signing_keys()

    # Initializing worker object to pass client default worker
    # data to testcases
    worker_obj = worker.SGXWorkerDetails()

    worker_obj, err_cd = worker_lookup_retrieve(config, worker_obj, uri_client)

    # return worker_obj, sig_obj, uri_client, private_key, err_cd
    return worker_obj, uri_client, private_key, err_cd


def worker_lookup_retrieve(config, worker_obj, uri_client):
    """ Function for computing worker lookup and retrieve once per session. """

    if not uri_client:
        logger.error("Server URI is not provided")
        exit(1)

    # logger.info("Execute work order")
    response = None

    err_cd = 0
    # create worker lookup request
    output_json_file_name = 'worker_lookup'

    lookup_obj = WorkerLookUp()
    lookup_obj.set_worker_type(WorkerType.TEE_SGX.value)
    input_worker_look_up = json.loads(lookup_obj.to_string())

    # input_json_str = input_worker_look_up
    logger.info("------------------Testing WorkerLookUp------------------")

    # submit worker lookup request and retrieve response
    logger.info("********Received Request*******\n%s\n", input_worker_look_up)
    response = submit_request(uri_client, input_worker_look_up,
                              output_json_file_name)
    logger.info("**********Received Response*********\n%s\n", response)

    # check worker lookup response
    if "result" in response and "totalCount" in response["result"].keys():
        if response["result"]["totalCount"] == 0:
            err_cd = 1
            logger.info('ERROR: Failed at WorkerLookUp - \
            No Workers exist to submit workorder.')

    if err_cd == 0:

        retrieve_obj = WorkerRetrieve()

        logger.info("-----Testing WorkerRetrieve-----")
        # Retrieving the worker id from the "WorkerLookUp" response and
        # update the worker id information for the further json requests
        if "result" in response and "ids" in response["result"].keys():
            retrieve_obj.set_worker_id(crypto_utils.strip_begin_end_public_key
                                       (response["result"]["ids"][0]))
            input_worker_retrieve = json.loads(retrieve_obj.to_string())
            logger.info('*****Worker details Updated with Worker ID***** \
                           \n%s\n', input_worker_retrieve)
        else:
            logger.info('ERROR: Failed at WorkerLookUp - \
                       No Worker ids in WorkerLookUp response.')
            err_cd = 1

        if err_cd == 0:
            # submit worker retrieve request and load to worker object
            response = submit_request(uri_client, input_worker_retrieve,
                                      output_json_file_name)
            worker_obj.load_worker(response)

    return worker_obj, err_cd
