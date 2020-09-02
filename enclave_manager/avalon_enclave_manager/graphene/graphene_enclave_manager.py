#!/usr/bin/env python3

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
import json
import logging
import os
import sys
import random

from avalon_enclave_manager.base_enclave_manager import EnclaveManager
from avalon_enclave_manager.work_order_processor_manager \
    import WOProcessorManager
from avalon_enclave_manager.graphene.graphene_enclave_info \
    import GrapheneEnclaveInfo
from utility.zmq_comm import ZmqCommunication
from utility.jrpc_utility import get_request_json

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------


class GrapheneEnclaveManager(WOProcessorManager):
    """
    Manager class to handle Graphene based work order processing
    """

    def __init__(self, config):
        """
        Constructor for Graphene Enclave Manager

        Parameters :
            config: Configuration for Graphene Enclave Manager class
        """
        # zmq socket has to be created before calling super class constructor
        # super class constructor calls _create_signup_data() which uses
        # socket for communicating with Graphene worker.
        graphene_zmq_url = config.get("EnclaveManager")["graphene_zmq_url"]
        self.zmq_socket = ZmqCommunication(graphene_zmq_url)
        self.zmq_socket.connect()
        super().__init__(config)
        self._config = config
        self.proof_data_type = config.get("WorkerConfig")["ProofDataType"]
        self._identity = self._worker_id

# -------------------------------------------------------------------------

    def _manager_on_boot(self):
        """
        Executes Boot flow of enclave manager
        """
        logger.info("Executing boot time procedure")

        # Add a new worker
        worker_info = EnclaveManager.create_json_worker(self, self._config)
        # Hex string read from config which is 64 characters long
        worker_id = self._worker_id
        self._worker_kv_delegate.add_new_worker(worker_id, worker_info)
        # Update mapping of worker_id to workers in a pool
        self._worker_kv_delegate.update_worker_map(
            worker_id, self._identity)

        # Cleanup all stale work orders for this worker which
        # used old worker keys
        self._wo_kv_delegate.cleanup_work_orders()

# -------------------------------------------------------------------------

    def _create_signup_data(self):
        """
        Creates Graphene worker signup data.

        Returns :
            signup_data: Signup data containining information of worker
                         like public encryption and verification key,
                         worker quote, mrencalve.
                         In case of error return None.
        """
        json_request = get_request_json("ProcessWorkerSignup",
                                        random.randint(0, 100000))
        try:
            # Send signup request to Graphene worker
            worker_signup = self.zmq_socket.send_request_zmq(
                json.dumps(json_request))
        except Exception as ex:
            logger.error("Exception while sending data over ZMQ:" + str(ex))
            return None

        if worker_signup is None:
            logger.error("Unable to get Graphene worker signup data")
            return None
        logger.debug("Graphene signup result {}".format(worker_signup))
        try:
            worker_signup_json = json.loads(worker_signup)
        except Exception as ex:
            logger.error("Exception during signup json creation:" + str(ex))
            return None
        # Create Signup Graphene object
        signup_data = GrapheneEnclaveInfo(self._config, worker_signup_json)
        return signup_data

# -------------------------------------------------------------------------

    def _execute_wo_in_trusted_enclave(self, input_json_str):
        """
        Submits workorder request to Graphene Worker and retrieves
        the response

        Parameters :
            input_json_str: JSON formatted str of the request to execute
        Returns :
            JSON response received from Graphene worker.
        """
        json_request = get_request_json("ProcessWorkOrder",
                                        random.randint(0, 100000),
                                        input_json_str)
        result = self.zmq_socket.send_request_zmq(json.dumps(json_request))
        if result is None:
            logger.error("Graphene work order execution error")
            return None
        try:
            json_response = json.loads(result)
        except Exception as ex:
            logger.error("Error loading json execution result: " + str(ex))
            return None
        return json_response

# -----------------------------------------------------------------


def main(args=None):
    import config.config as pconfig
    import utility.logger as plogger

    # parse out the configuration file first
    tcf_home = os.environ.get("TCF_HOME", "../../../")

    conf_files = ["graphene_config.toml"]
    conf_paths = [".", tcf_home + "/"+"config"]

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="configuration file", nargs="+")
    parser.add_argument("--config-dir", help="configuration folder", nargs="+")
    parser.add_argument("--worker_id",
                        help="Id of worker in plain text", type=str)

    (options, remainder) = parser.parse_known_args(args)

    if options.config:
        conf_files = options.config

    if options.config_dir:
        conf_paths = options.config_dir

    try:
        config = pconfig.parse_configuration_files(conf_files, conf_paths)
        json.dumps(config, indent=4)
    except pconfig.ConfigurationException as e:
        logger.error(str(e))
        sys.exit(-1)

    if options.worker_id:
        config["WorkerConfig"]["worker_id"] = options.worker_id

    plogger.setup_loggers(config.get("Logging", {}))
    sys.stdout = plogger.stream_to_logger(
        logging.getLogger("STDOUT"), logging.DEBUG)
    sys.stderr = plogger.stream_to_logger(
        logging.getLogger("STDERR"), logging.WARN)

    EnclaveManager.parse_command_line(config, remainder)
    try:
        enclave_manager = GrapheneEnclaveManager(config)
        logger.info("About to start Graphene Enclave manager")
        enclave_manager.start_enclave_manager()
    except Exception as ex:
        logger.error("Error starting Graphene Enclave Manager: " + str(e))
    # Disconnect ZMQ socket.
    if self.zmq_socket:
        self.zmq_socket.disconnect()


main()
