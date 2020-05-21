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
import hashlib

import avalon_enclave_manager.sgx_work_order_request as work_order_request
import avalon_enclave_manager.kme.kme_enclave_info as enclave_info
import avalon_crypto_utils.crypto_utility as crypto_utils
from avalon_enclave_manager.base_enclave_manager import EnclaveManager
from avalon_enclave_manager.worker_kv_delegate import WorkerKVDelegate
from avalon_enclave_manager.work_order_kv_delegate import WorkOrderKVDelegate
from listener.base_jrpc_listener import parse_bind_url
from avalon_enclave_manager.kme.kme_listener import KMEListener

logger = logging.getLogger(__name__)


class KeyManagementEnclaveManager(EnclaveManager):
    """
    Class to manage key management enclave in a worker pool
    setup for processing work orders
    """

    def __init__(self, config):

        super().__init__(config)
        self.proof_data_type = config.get("WorkerConfig")["ProofDataType"]

# -------------------------------------------------------------------------

    def _create_signup_data(self):
        """
        Create KME signup data.

        Returns :
            signup_data - Relevant signup data to be used for requests to the
                          enclave
        """
        return enclave_info.\
            KeyManagementEnclaveInfo(self._config["EnclaveModule"])

# -------------------------------------------------------------------------

    def _manager_on_boot(self):
        """
        Executes Boot flow of enclave manager
        """
        logger.info("Executing boot time procedure")

        # Add a new worker
        worker_info = EnclaveManager.create_json_worker(self, self._config)
        worker_id = crypto_utils.strip_begin_end_public_key(self.enclave_id) \
            .encode("UTF-8")
        # Calculate sha256 of worker id to get 32 bytes. The TC spec proxy
        # model contracts expect byte32. Then take a hexdigest for hex str.
        worker_id = hashlib.sha256(worker_id).hexdigest()
        self._worker_kv_delegate.add_new_worker(worker_id, worker_info)

        # Cleanup wo-processing" table
        self._wo_kv_delegate.cleanup_work_orders()

# -------------------------------------------------------------------------

    def _execute_work_order(self, input_json_str, indent=4):
        """
        Submits request to KME and retrieves the response

        Parameters :
            input_json_str - A JSON formatted str of the request to execute
        Returns :
            json_response - A JSON formatted str of the response received from
                            the enclave
        """
        try:
            wo_request = work_order_request.SgxWorkOrderRequest(
                self._config,
                input_json_str)
            wo_response = wo_request.execute()

            try:
                json_response = json.dumps(wo_response, indent=indent)
            except Exception as err:
                logger.error("ERROR: Failed to serialize JSON; %s", str(err))

        except Exception as e:
            logger.error("failed to execute work order; %s", str(e))

        return json_response

# -------------------------------------------------------------------------

    def start_enclave_manager(self):
        """
        Execute boot flow and run time flow
        """
        try:
            logger.info(
                "--------------- Starting Boot time flow ----------------")
            self._manager_on_boot()
            logger.info(
                "--------------- Boot time flow Complete ----------------")
        except Exception as err:
            logger.error("Failed to execute boot time flow; " +
                         "exiting Intel SGX Enclave manager: {}".format(err))
            exit(1)

        self._start_kme_listener()


# -------------------------------------------------------------------------

    def _start_kme_listener(self):
        """
        This function reads the host_name and port for the listener to
        bind. It instantiates the KMEListener and starts it. This
        listener runs indefinitely processing requests received from
        WPEs. It terminates only when an exception occurs within start
        method os the listener instance.
        """
        host_name, port = parse_bind_url(
            self._config["KMEListener"].get("bind"))

        rpc_methods = [
            self.kme_uid,
            self.kme_reg,
            self.pre_process_wo
        ]
        kme_listener = KMEListener(rpc_methods)
        kme_listener.start(host_name, port)


# -----------------------------------------------------------------

    def GetUniqueVerificationKey(self, **params):
        """
        """
        return ""

# -----------------------------------------------------------------

    def RegisterWorkOrderProcessor(self, **params):
        """
        """
        return ""

# -----------------------------------------------------------------

    def PreProcessWorkOrder(self, **params):
        """
        """
        pass

# -----------------------------------------------------------------


def main(args=None):
    import config.config as pconfig
    import utility.logger as plogger

    # parse out the configuration file first
    tcf_home = os.environ.get("TCF_HOME", "../../../../")

    conf_files = ["kme_config.toml"]
    conf_paths = [".", tcf_home + "/"+"config"]

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="configuration file", nargs="+")
    parser.add_argument("--config-dir", help="configuration folder", nargs="+")
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

    plogger.setup_loggers(config.get("Logging", {}))
    sys.stdout = plogger.stream_to_logger(
        logging.getLogger("STDOUT"), logging.DEBUG)
    sys.stderr = plogger.stream_to_logger(
        logging.getLogger("STDERR"), logging.WARN)

    EnclaveManager.parse_command_line(config, remainder)
    logger.info("Initialize KeyManagement enclave_manager")
    enclave_manager = KeyManagementEnclaveManager(config)
    logger.info("About to start KeyManagement Enclave manager")
    enclave_manager.start_enclave_manager()


main()
