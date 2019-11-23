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

import binascii
import logging
from os import environ

from utility.hex_utils import is_valid_hex_str

from utility.tcf_types import WorkerStatus, WorkerType
from connectors.ethereum.ethereum_wrapper import EthereumWrapper
from connectors.interfaces.worker_registry_interface import WorkerRegistryInterface
from connectors.utils import construct_message, validate_details

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class EthereumWorkerRegistryImpl(WorkerRegistryInterface):
    """
    Implements WorkerRegistryInterface interface
    Detail method description will be available in interface
    """

    def __init__(self, config):
        if self.__validate(config) is True:
            self.__initialize(config)
        else:
            raise Exception("Invalid configuration parameter")

    def worker_register(self, worker_id, worker_type, org_id, application_ids, details):
        """
        Registry new worker with details of worker
        """
        if (self.__contract_instance is not None):
            if not is_valid_hex_str(binascii.hexlify(worker_id).decode("utf8")):
                logging.info("Invalid worker id {}".format(worker_id))
                return construct_message("failed", "Invalid worker id {}".format(worker_id))
            if not isinstance(worker_type, WorkerType):
                logging.info("Invalid workerType {}".format(worker_type))
                return construct_message("failed", "Invalid workerType {}".format(worker_type))
            if not is_valid_hex_str(binascii.hexlify(org_id).decode("utf8")):
                logging.info("Invalid organization id {}".format(org_id))
                return construct_message("failed", "Invalid organization id {}".format(org_id))
            for aid in application_ids:
                if not is_valid_hex_str(binascii.hexlify(aid).decode("utf8")):
                    logging.info("Invalid application id {}".format(aid))
                    return construct_message("failed", "Invalid application id {}".format(aid))
            if details is not None:
                is_valid = validate_details(details)
                if is_valid is not None:
                    return construct_message("failed", is_valid)

            txn_hash = self.__contract_instance.functions.workerRegister(
                worker_id, worker_type.value, org_id, application_ids,
                details).buildTransaction(
                {"chainId": self.__eth_client.get_channel_id(),
                "gas": self.__eth_client.get_gas_limit(),
                "gasPrice": self.__eth_client.get_gas_price(),
                "nonce": self.__eth_client.get_txn_nonce()})
            tx = self.__eth_client.execute_transaction(txn_hash)
            return tx
        else:
            logging.error("worker registry contract instance is not initialized")
            return construct_message("failed", "worker registry contract instance is not initialized")

    def worker_set_status(self, worker_id, status):
        """
        Set the registry status identified by worker id
        status is worker type enum type
        """
        if (self.__contract_instance is not None):
            if not is_valid_hex_str(binascii.hexlify(worker_id).decode("utf8")):
                logging.info("Invalid worker id {}".format(worker_id))
                return construct_message("failed", "Invalid worker id {}".format(worker_id))
            if not isinstance(status, WorkerStatus):
                logging.info("Invalid worker status {}".format(status))
                return construct_message("failed", "Invalid worker status {}".format(status))
            txn_hash = self.__contract_instance.functions.workerSetStatus(worker_id,
                status.value).buildTransaction(
                {
                    "chainId": self.__eth_client.get_channel_id(),
                    "gas": self.__eth_client.get_gas_limit(),
                    "gasPrice": self.__eth_client.get_gas_price(),
                    "nonce": self.__eth_client.get_txn_nonce()
                })
            tx = self.__eth_client.execute_transaction(txn_hash)
            return tx
        else:
            logging.error("worker registry contract instance is not initialized")
            return construct_message("failed", "worker registry contract instance is not initialized")

    def worker_update(self, worker_id, details):
        """
        Update the worker with details data which is json string
        """
        if (self.__contract_instance is not None):
            if not is_valid_hex_str(binascii.hexlify(worker_id).decode("utf8")):
                logging.error("Invalid worker id {}".format(worker_id))
                return construct_message("failed", "Invalid worker id {}".format(worker_id))
            if details is not None:
                is_valid = validate_details(details)
                if is_valid is not None:
                    logging.error(is_valid)
                    return construct_message("failed", is_valid)
            txn_hash = self.__contract_instance.functions.workerUpdate(worker_id,
                details).buildTransaction(
                {
                    "chainId": self.__eth_client.get_channel_id(),
                    "gas": self.__eth_client.get_gas_limit(),
                    "gasPrice": self.__eth_client.get_gas_price(),
                    "nonce": self.__eth_client.get_txn_nonce()
                })
            tx = self.__eth_client.execute_transaction(txn_hash)
            return tx
        else:
            logging.error("worker registry contract instance is not initialized")
            return construct_message("failed", "worker registry contract instance is not initialized")

    def worker_lookup(self, worker_type, org_id, application_id):
        """
        Lookup a worker identified worker_type, org_id and application_id
        all fields are optional and if present condition should match for all
        fields. If none passed it should return all workers.
        """
        if (self.__contract_instance is not None):
            if not isinstance(worker_type, WorkerType):
                logging.info("Invalid workerType {}".format(worker_type))
                return construct_message("failed", "Invalid workerType {}".format(worker_type))
            if not is_valid_hex_str(binascii.hexlify(org_id).decode("utf8")):
                logging.info("Invalid organization id {}".format(org_id))
                return construct_message("failed", "Invalid organization id {}".format(org_id))
            if not is_valid_hex_str(binascii.hexlify(application_id).decode("utf8")):
                logging.info("Invalid application id {}".format(application_id))
                return construct_message("failed", "Invalid application id {}".format(application_id))
            lookupResult = self.__contract_instance.functions.workerLookUp(worker_type.value,
                org_id, application_id).call()
            return lookupResult
        else:
            logging.error("worker registry contract instance is not initialized")
            return construct_message("failed", "worker registry contract instance is not initialized")

    def worker_retrieve(self, worker_id):
        """
        Retrieve the worker identified by worker id
        """
        if (self.__contract_instance is not None):
            if not is_valid_hex_str(binascii.hexlify(worker_id).decode("utf8")):
                logging.info("Invalid worker id {}".format(worker_id))
                return construct_message("failed", "Invalid worker id {}".format(worker_id))

            workerDetails = self.__contract_instance.functions.workerRetrieve(worker_id).call()
            return workerDetails
        else:
            logging.error("worker registry contract instance is not initialized")
            return construct_message("failed", "worker registry contract instance is not initialized")

    def worker_lookup_next(self, worker_type, org_id, application_id, lookup_tag):
        if (self.__contract_instance is not None):
            if not isinstance(worker_type, WorkerType):
                logging.info("Invalid workerType {}".format(worker_type))
                return construct_message("failed", "Invalid workerType {}".format(worker_type))
            if not is_valid_hex_str(binascii.hexlify(org_id).decode("utf")):
                logging.info("Invalid organization id {}".format(org_id))
                return construct_message("failed", "Invalid organization id {}".format(org_id))
            if not is_valid_hex_str(binascii.hexlify(application_id).decode("utf8")):
                logging.info("Invalid application id {}".format(org_id))
                return construct_message("failed", "Invalid application id {}".format(org_id))
            lookupResult = self.__contract_instance.functions.workerLookUpNext(worker_type.value,
                org_id, application_id, lookup_tag).call()
            return lookupResult
        else:
            logging.error("worker registry contract instance is not initialized")
            return construct_message("failed", "worker registry contract instance \
                is not initialized")

    def __validate(self, config):
        """
        validates parameter from config parameters for existence.
        Returns false if validation fails and true if it success
        """
        if config["ethereum"]["worker_registry_contract_file"] is None:
            logging.error("Missing worker registry contract file path!!")
            return False
        if config["ethereum"]["worker_registry_contract_address"] is None:
            logging.error("Missing worker registry contract address!!")
            return False
        return True

    def __initialize(self, config):
        """
        Initialize the parameters from config to instance variables.
        """
        self.__eth_client = EthereumWrapper(config)
        tcf_home = environ.get("TCF_HOME", "../../../")
        contract_file_name = tcf_home + "/" + \
            config["ethereum"]["worker_registry_contract_file"]
        contract_address = config["ethereum"]["worker_registry_contract_address"]
        self.__contract_instance = self.__eth_client.get_contract_instance(
            contract_file_name, contract_address
        )
