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

from avalon_sdk.worker.worker_details import WorkerStatus, WorkerType
from avalon_sdk.ethereum.ethereum_wrapper import EthereumWrapper
from avalon_sdk.interfaces.worker_registry \
    import WorkerRegistry
from avalon_sdk.worker.worker_details import WorkerDetails

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class EthereumWorkerRegistryImpl(WorkerRegistry):
    """
    This class provide worker APIs which interact with
    Ethereum blockchain. Detail method description will be
    available in interface
    """

    def __init__(self, config):
        if self.__validate(config) is True:
            self.__initialize(config)
        else:
            raise Exception("Invalid configuration parameter")

    def worker_lookup(self, worker_type, org_id, application_id):
        """
        Lookup a worker identified worker_type, org_id and application_id
        all fields are optional and if present condition should match for all
        fields. If none passed it should return all workers.
        Returns tuple containing workers count, lookup tag and list of
        worker ids or on error returns None.
        """
        if (self.__contract_instance is not None):
            if not isinstance(worker_type, WorkerType):
                logging.info("Invalid workerType {}".format(worker_type))
                return None
            if not is_valid_hex_str(binascii.hexlify(org_id).decode("utf8")):
                logging.info("Invalid organization id {}".format(org_id))
                return None
            if not is_valid_hex_str(
                    binascii.hexlify(application_id).decode("utf8")):
                logging.info(
                    "Invalid application id {}".format(application_id))
                return None
            lookupResult = self.__contract_instance.functions.workerLookUp(
                worker_type.value, org_id, application_id).call()
            return lookupResult
        else:
            logging.error(
                "worker registry contract instance is not initialized")
            return None

    def worker_retrieve(self, worker_id):
        """
        Retrieve the worker identified by worker id
        Returns tuple containing worker status, worker type,
        organization id, list of application ids and worker
        details(json string)
        On error returns None
        """
        if (self.__contract_instance is not None):
            if not is_valid_hex_str(binascii.hexlify(
                    worker_id).decode("utf8")):
                logging.info("Invalid worker id {}".format(worker_id))
                return None

            workerDetails = self.__contract_instance.functions.workerRetrieve(
                worker_id).call()
            return workerDetails
        else:
            logging.error(
                "worker registry contract instance is not initialized")
            return None

    def worker_lookup_next(self, worker_type, org_id, application_id,
                           lookup_tag):
        """
        Getting Additional Worker Lookup Results
        Inputs
        1. worker_type is a characteristic of Workers for which you may wish
        to search.
        2. organization_id is an organization to which a Worker belongs.
        3. application_type_id is an application type that has to be supported
        by the Worker.
        4. lookup_tag is returned by a previous call to either this function
        or to worker_lookup.
        5. id is used for json rpc request

        Outputs tuple containing following.
        1. total_count is a total number of entries matching this lookup
        criteria.  If this number is larger than the number of ids returned
        so far, the caller should use lookupTag to call workerLookUpNext to
        retrieve the rest of the ids.
        2. new_lookup_tag is an optional parameter. If it is returned, it
        means that there are more matching Worker ids than can be retrieved
        by calling this function again with this tag as an input parameter.
        3. ids is an array of the Worker ids that match the input parameters.
        On error returns None.
        """
        if (self.__contract_instance is not None):
            if not isinstance(worker_type, WorkerType):
                logging.info("Invalid workerType {}".format(worker_type))
                return None
            if not is_valid_hex_str(binascii.hexlify(org_id).decode("utf")):
                logging.info("Invalid organization id {}".format(org_id))
                return None
            if not is_valid_hex_str(
                    binascii.hexlify(application_id).decode("utf8")):
                logging.info("Invalid application id {}".format(org_id))
                return None
            lookupResult = self.__contract_instance.functions.workerLookUpNext(
                worker_type.value,
                org_id, application_id, lookup_tag).call()
            return lookupResult
        else:
            logging.error(
                "worker registry contract instance is not initialized")
            return None

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
        contract_address = \
            config["ethereum"]["worker_registry_contract_address"]
        self.__contract_instance = self.__eth_client.get_contract_instance(
            contract_file_name, contract_address
        )

    def worker_register(
            self, worker_id, worker_type, org_id, application_ids, details):
        """
        Register new worker with details of worker
        Inputs
        1. worker_id is a worker id, e.g. an Ethereum address or
        a value derived from the worker's DID.
        2. worker_type defines the type of Worker. Currently defined types are:
            1. indicates "TEE-SGX": an Intel SGX Trusted Execution Environment
            2. indicates "MPC": Multi-Party Compute
            3. indicates "ZK": Zero-Knowledge
        3. organization_id is an optional parameter representing the
        organization that hosts the Worker, e.g. a bank in the consortium or
        anonymous entity.
        4. application_type_ids is an optional parameter that defines
        application types supported by the Worker.
        5. details is detailed information about the worker in JSON format as
        defined in
        https://entethalliance.github.io/trusted-computing/spec.html
        #common-data-for-all-worker-types
        Returns transaction receipt on success or None on error.
        """
        if (self.__contract_instance is not None):
            if not is_valid_hex_str(
                    binascii.hexlify(worker_id).decode("utf8")):
                logging.info("Invalid worker id {}".format(worker_id))
                return None
            if not isinstance(worker_type, WorkerType):
                logging.info("Invalid workerType {}".format(worker_type))
                return None
            if not is_valid_hex_str(binascii.hexlify(org_id).decode("utf8")):
                logging.info("Invalid organization id {}".format(org_id))
                return None
            for aid in application_ids:
                if not is_valid_hex_str(binascii.hexlify(aid).decode("utf8")):
                    logging.info("Invalid application id {}".format(aid))
                    return None
            if details is not None:
                worker = WorkerDetails()
                is_valid = worker.validate_worker_details(details)
                if is_valid is not None:
                    return None

            txn_statusn_hash = \
                self.__contract_instance.functions.workerRegister(
                    worker_id, worker_type.value, org_id, application_ids,
                    details).buildTransaction(
                        self.__eth_client.get_transaction_params()
                        )
            txn_status = self.__eth_client.execute_transaction(
                txn_statusn_hash)
            return txn_status
        else:
            logging.error(
                "worker registry contract instance is not initialized")
            return None

    def worker_set_status(self, worker_id, status):
        """
        Set the registry status identified by worker id
        status is worker type enum type
        Returns transaction receipt on success or None on error.
        """
        if (self.__contract_instance is not None):
            if not is_valid_hex_str(binascii.hexlify(
                    worker_id).decode("utf8")):
                logging.info("Invalid worker id {}".format(worker_id))
                return None
            if not isinstance(status, WorkerStatus):
                logging.info("Invalid worker status {}".format(status))
                return None
            txn_statusn_hash = \
                self.__contract_instance.functions.workerSetStatus(
                    worker_id,
                    status.value).buildTransaction(
                        self.__eth_client.get_transaction_params()
                        )
            txn_status = self.__eth_client.execute_transaction(
                txn_statusn_hash)
            return txn_status
        else:
            logging.error(
                "worker registry contract instance is not initialized")
            return None

    def worker_update(self, worker_id, details):
        """
        Update the worker with details data which is json string
        Updating a Worker
        Inputs
        1. worker_id is a worker id, e.g. an Ethereum address or
        a value derived from the worker's DID.
        2. details is detailed information about the worker in JSON format
        Returns transaction receipt on success or None on error.
        """
        if (self.__contract_instance is not None):
            if not is_valid_hex_str(binascii.hexlify(
                    worker_id).decode("utf8")):
                logging.error("Invalid worker id {}".format(worker_id))
                return None
            if details is not None:
                worker = WorkerDetails()
                is_valid = worker.validate_worker_details(details)
                if is_valid is not None:
                    logging.error(is_valid)
                    return None
            txn_statusn_hash = self.__contract_instance.functions.workerUpdate(
                worker_id,
                details).buildTransaction(
                    self.__eth_client.get_transaction_params()
            )
            txn_status = self.__eth_client.execute_transaction(
                txn_statusn_hash)
            return txn_status
        else:
            logging.error(
                "worker registry contract instance is not initialized")
            return None
