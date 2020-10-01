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

import avalon_enclave_manager.sgx_work_order_request as work_order_request
import avalon_enclave_manager.singleton.singleton_enclave_info as enclave_info
from avalon_enclave_manager.base_enclave_manager import EnclaveManager
from avalon_enclave_manager.work_order_processor_manager \
    import WOProcessorManager
from error_code.error_status import WorkOrderStatus
from avalon_enclave_manager.enclave_type import EnclaveType

logger = logging.getLogger(__name__)


class SingletonEnclaveManager(WOProcessorManager):
    """
    Manager class to handle single enclave based work order processing
    """

    def __init__(self, config):

        super().__init__(config)
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
        Create Singleton enclave signup data.

        Returns :
            signup_data - Relevant signup data to be used for requests to the
                          enclave
        """
        return enclave_info.\
            SingletonEnclaveInfo(self._config,
                                 self._worker_id,
                                 EnclaveType.SINGLETON)

# -------------------------------------------------------------------------

    def _execute_wo_in_trusted_enclave(self, input_json_str):
        """
        Submits workorder request to Worker enclave and retrieves the response

        Parameters :
            input_json_str - A JSON formatted str of the request to execute
        Returns :
            json_response - A JSON formatted str of the response received from
                            the enclave. Errors are also wrapped in a JSON str
                            if exceptions have occurred.
        """
        try:
            wo_request = work_order_request.SgxWorkOrderRequest(
                EnclaveType.SINGLETON,
                input_json_str)
        except Exception as e:
            logger.exception(
                'Failed to initialize SgxWorkOrderRequest; %s', str(e))
        return wo_request.execute()


# -----------------------------------------------------------------


def main(args=None):
    import config.config as pconfig
    import utility.logger as plogger

    # parse out the configuration file first
    tcf_home = os.environ.get("TCF_HOME", "../../../../")

    conf_files = ["singleton_enclave_config.toml"]
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
    logger.info("Initialize singleton enclave_manager")
    enclave_manager = SingletonEnclaveManager(config)
    logger.info("About to start Singleton Enclave manager")
    enclave_manager.start_enclave_manager()


main()
