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
import sys
import zmq
from abc import ABC, abstractmethod

import avalon_enclave_manager.avalon_enclave_info as enclave_info
from database import connector
from avalon_enclave_manager.worker_kv_delegate import WorkerKVDelegate
from avalon_enclave_manager.work_order_kv_delegate import WorkOrderKVDelegate
from avalon_sdk.worker.worker_details import WorkerStatus, WorkerType

logger = logging.getLogger(__name__)


class EnclaveManager(ABC):
    """
    Abstract base class for Enclave Manager
    """

    def __init__(self, config):

        super().__init__()

        self._config = config
        signup_data, measurements = self._setup_enclave()
        self._kv_helper = self._connect_to_kv_store()
        self._worker_kv_delegate = WorkerKVDelegate(self._kv_helper)
        self._wo_kv_delegate = WorkOrderKVDelegate(self._kv_helper)
        self.enclave_data = signup_data
        self.sealed_data = signup_data.sealed_data
        self.verifying_key = signup_data.verifying_key
        self.encryption_key = signup_data.encryption_key

        # TODO: encryption_key_nonce is hardcoded to an empty str
        # Need to come up with a scheme to generate it for every unique
        # encryption key.
        self.encryption_key_nonce = ""
        self.encryption_key_signature = signup_data.encryption_key_signature
        self.enclave_id = signup_data.enclave_id
        self.extended_measurements = measurements
        self.proof_data_type = config.get("WorkerConfig")["ProofDataType"]
        self.proof_data = signup_data.proof_data

# -------------------------------------------------------------------------

    @abstractmethod
    def _manager_on_boot(self):
        """
        Executes Boot flow of enclave manager. This function includes a set
        of tasks that an enclave manager is supposed to do as soon as it is
        started and before it handles requests indefinitely. It may include
        a cleanup of database or ensuring syncup with it. There can also be
        some sanity checks to ensure reentrancy in case of abrupt failures.
        """
        pass

# -------------------------------------------------------------------------

    @abstractmethod
    def _execute_work_order(self, input_json_str, indent=4):
        """
        Submits the incoming request to corresponding enclave for execution.

        Returns :
            response - Response received as response from execution at the
                       enclave.
        """
        pass

# -------------------------------------------------------------------------

    @abstractmethod
    def start_enclave_manager(self):
        """
        Executes boot flow and run time flow. This is the engine of an enclave
        manager which keeps running as long as there are no unexpected errors.
        It should first carry out the boot time flow followed by the run time
        routine which is indefinite.
        """
        pass

# -------------------------------------------------------------------------

    def _connect_to_kv_store(self):
        """
        This function creates a connection to the KVStorage.

        Returns :
            kv_helper - An instance of LMDBHelperProxy that helps interact
                        with the database
        """
        if self._config.get("KvStorage") is None:
            logger.error("Kv Storage path is missing")
            sys.exit(-1)
        try:
            kv_helper = connector.open(self._config['KvStorage']['remote_url'])
        except Exception as err:
            logger.error("Failed to open KV storage interface; " +
                         "exiting Intel SGX Enclave manager: {}".format(err))
            sys.exit(-1)
        return kv_helper

# -------------------------------------------------------------------------

    def _setup_enclave(self):
        """
        This function is responsible for initialization of the trusted
        enclave. It does so via the EnclaveInfo class which not only
        initializes the enclave but also ensure the enclave creates
        the signup data. This signup data is key to all the trusted
        functionalities over this instance of the enclave. Therefore
        all relevant data is sent back here. This is kept in memory
        for use hereafter.

        Returns :
            signup_data - Relevant signup data to be used for requests to the
                          enclave
            extended_measurements - A tuple of enclave basename & measurements
        """
        try:
            logger.info("Initialize enclave and create signup data")
            signup_data = enclave_info.\
                EnclaveInfo(self._config.get("EnclaveModule"))
            extended_measurements = signup_data.get_extended_measurements()
        except Exception as e:
            logger.exception("failed to initialize/signup enclave; %s", str(e))
            sys.exit(-1)
        return signup_data, extended_measurements

    # -----------------------------------------------------------------

    @staticmethod
    def validate_request(wo_request):
        """
        Validate JSON workorder request.
        Parameters :
            wo_request - Flattened JSON request
        Returns :
            True - If the input string is a valid JSON
            False - Otherwise
        """
        try:
            json.loads(wo_request)
        except ValueError as e:
            logger.error("Invalid JSON format found for workorder - %s", e)
            return False
        return True

    # -----------------------------------------------------------------

    @staticmethod
    def create_json_worker(enclave_data, config):
        """
        Create JSON worker object which gets saved in KvStorage
        Parameters :
            enclave_data - An instance of the corresponding EnclaveManager
            config - A dict of configs
        Returns :
            json_worker_info - JSON serialized worker info
        """
        worker_type_data = dict()
        worker_type_data["verificationKey"] = enclave_data.verifying_key
        worker_type_data["extendedMeasurements"] = \
            enclave_data.extended_measurements
        worker_type_data["proofDataType"] = enclave_data.proof_data_type
        worker_type_data["proofData"] = enclave_data.proof_data
        worker_type_data["encryptionKey"] = enclave_data.encryption_key
        worker_type_data["encryptionKeySignature"] = \
            enclave_data.encryption_key_signature

        worker_info = dict()
        worker_info["workerType"] = WorkerType.TEE_SGX.value
        worker_info["organizationId"] = \
            config.get("WorkerConfig")["OrganizationId"]
        worker_info["applicationTypeId"] = \
            config.get("WorkerConfig")["ApplicationTypeId"]

        details_info = dict()
        details_info["workOrderSyncUri"] = \
            config.get("WorkerConfig")["WorkOrderSyncUri"]
        details_info["workOrderAsyncUri"] = \
            config.get("WorkerConfig")["WorkOrderAsyncUri"]
        details_info["workOrderPullUri"] = \
            config.get("WorkerConfig")["WorkOrderPullUri"]
        details_info["workOrderNotifyUri"] = \
            config.get("WorkerConfig")["WorkOrderNotifyUri"]
        details_info["receiptInvocationUri"] = \
            config.get("WorkerConfig")["ReceiptInvocationUri"]
        details_info["workOrderInvocationAddress"] = config.get(
            "WorkerConfig")["WorkOrderInvocationAddress"]
        details_info["receiptInvocationAddress"] = config.get(
            "WorkerConfig")["ReceiptInvocationAddress"]
        details_info["fromAddress"] = config.get("WorkerConfig")["FromAddress"]
        details_info["hashingAlgorithm"] = \
            config.get("WorkerConfig")["HashingAlgorithm"]
        details_info["signingAlgorithm"] = \
            config.get("WorkerConfig")["SigningAlgorithm"]
        details_info["keyEncryptionAlgorithm"] = \
            config.get("WorkerConfig")["KeyEncryptionAlgorithm"]
        details_info["dataEncryptionAlgorithm"] = \
            config.get("WorkerConfig")["DataEncryptionAlgorithm"]
        details_info["workOrderPayloadFormats"] = \
            config.get("WorkerConfig")["workOrderPayloadFormats"]
        details_info["workerTypeData"] = worker_type_data

        worker_info["details"] = details_info
        worker_info["status"] = WorkerStatus.ACTIVE.value

        # JSON serialize worker_info
        json_worker_info = json.dumps(worker_info)
        logger.info("JSON serialized worker info is %s", json_worker_info)
        return json_worker_info

    # -----------------------------------------------------------------

    @staticmethod
    def bind_zmq_socket(zmq_port):
        """
        Function to bind to zmq port configured. ZMQ is used for
        synchronous work order processing.

        Returns :
            socket - An instance of a Socket bound to the configured
                     port.
        """
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://0.0.0.0:"+zmq_port)
        return socket

    # -----------------------------------------------------------------

    @staticmethod
    def parse_command_line(config, args):
        """
        Parse command line arguments
        """

        parser = argparse.ArgumentParser()

        parser.add_argument(
            "--logfile",
            help="Name of the log file, __screen__ for standard output",
            type=str)
        parser.add_argument("--loglevel", help="Logging leve", type=str)
        parser.add_argument(
            "--lmdb_url",
            help="DB url to connect to lmdb", type=str)

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
        if options.lmdb_url:
            config["KvStorage"]["remote_url"] = options.lmdb_url
