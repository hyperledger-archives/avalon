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

import logging
import asyncio
import importlib

from database import connector
import utility.file_utils as file_utils
from avalon_enclave_manager.base_enclave_manager import EnclaveManager
from avalon_enclave_manager.worker_kv_delegate import WorkerKVDelegate

logger = logging.getLogger(__name__)

class WorkerKeyRefresh:
    """
    Class for handling worker encryption key refresh
    """
    def __init__(self, enclave_info, config, enclave_type):
        super().__init__()
        self._enclave_info = enclave_info
        if enclave_type == "singleton":
            self._enclave = importlib.import_module(
                "avalon_enclave_manager.singleton.singleton_enclave")
            self._enclave_type = "singleton"
        elif enclave_type == "kme":
            self._enclave = importlib.import_module(
                "avalon_enclave_manager.kme.kme_enclave")
            self._enclave_type = "kme"
        self._config = config
        self._worker_id = enclave_info._worker_id

        try:
            self._kv_helper = connector.open(config['KvStorage']['remote_url'])
            self._worker_kv_delegate = WorkerKVDelegate(self._kv_helper)
        except Exception as err:
            logger.error("Failed to open KV storage interface; " +
                         "exiting Intel SGX Enclave manager: {}".format(err))
            sys.exit(-1)

    def __refresh_worker_encryption_key(self):
        """
        Refresh worker encryption key pair and retrieve updated
        worker details from enclave
        """
        # start enclave key refresh
        if self._enclave_type == "singleton":
            signup_cpp_obj = self._enclave.SignupInfoSingleton()
        elif self._enclave_type == "kme":
            signup_cpp_obj = self._enclave.SignupInfoKME()
        updated_signup_data = signup_cpp_obj.RefreshWorkerEncryptionKey()

        if updated_signup_data is None:
            return None
        signup_info = {
            'encryption_key':
                updated_signup_data['encryption_key'],
            'encryption_key_signature':
                updated_signup_data['encryption_key_signature'],
            'sealed_enclave_data':
                updated_signup_data['sealed_enclave_data']
        }

        if signup_info['sealed_enclave_data'] is None:
            logger.info("Sealed data is None, so nothing to persist.")
        else:
            file_utils.write_to_file(
                signup_info['sealed_enclave_data'],
                self._enclave_info._get_sealed_data_file_name(
                    self._config["EnclaveModule"]["sealed_data_path"],
                    self._worker_id))
        return signup_info

# -----------------------------------------------------------------

    def _initiate_key_refresh(self):

        """
        Initiate worker encryption key refresh and update worker details
        and updates worker details to kv storage
        """

        try:
            enclave_signup_data = \
                self.__refresh_worker_encryption_key()
            # Update worker encryption key, encryption key signature and
            # sealed data after key refresh
            logger.info("_initiate_key_refresh")
            self._enclave_info.encryption_key = enclave_signup_data['encryption_key']
            self._enclave_info.encryption_key_signature = \
                enclave_signup_data['encryption_key_signature']
            self._enclave_info.sealed_enclave_data = enclave_signup_data['sealed_enclave_data']

            # Add a new worker
            worker_info = EnclaveManager.create_json_worker(
                self._enclave_info, self._config)
            logger.info(
                "Persiting updated worker details after key refresh - %s",
                worker_info)
            # Hex string read from config which is 64 characters long
            self._worker_kv_delegate.add_new_worker(
                self._enclave_info._worker_id, worker_info)
            return self
        except Exception as e:
            logger.error("failed to get signup data after key refresh: %s",
                        str(e))
            raise e

