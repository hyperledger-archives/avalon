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

import logging
import json
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
    This class is sets and gets worker-related information to and from
    the Ethereum blockchain.
    Detailed method descriptions are available in the WorkerRegistry
    interfaces.
    """

    def __init__(self, config):
        """
        Parameters:
        config    Dictionary containing Ethereum-specific parameters
        """
        if self.__validate(config) is True:
            self.__initialize(config)
        else:
            raise Exception("Invalid configuration parameter")

    def worker_lookup(self, worker_type, org_id, application_id, id=None):
        """
        Lookup a worker identified by worker_type, org_id, and application_id.
        All fields are optional and, if present, condition should match for
        all fields. If none are passed it should return all workers.

        If the list is too large to fit into a single response (the maximum
        number of entries in a single response is implementation specific),
        the smart contract should return the first batch of the results
        and provide a lookupTag that can be used by the caller to
        retrieve the next batch by calling worker_lookup_next.

        Parameters:
        worker_type    Optional characteristic of workers for which you may
                       wish to search
        org_id         Optional organization ID that can be used to search
                       for one or more workers that belong to this
                       organization
        application_id Optional application type ID that is supported by
                       the worker
        id             Optional JSON RPC request ID

        Returns:
        Tuple containing workers count, lookup tag, and list of
        worker IDs:
        total_count Total number of entries matching a specified
                    lookup criteria. If this number is larger than the
                    size of the IDs array, the caller should use
                    lookupTag to call worker_lookup_next to retrieve
                    the rest of the IDs
        lookup_tag  Optional parameter. If it is returned, it means
                    that there are more matching worker IDs, which can then
                    be retrieved by calling function worker_lookup_next
                    with this tag as an input parameter
        ids         Array of the worker IDs that match the input parameters

        On error returns None.
        """

        if (self.__contract_instance is not None):
            if not isinstance(worker_type, WorkerType):
                logging.error("Invalid workerType {}".format(worker_type))
                return None
            if not is_valid_hex_str(org_id):
                logging.error("Invalid organization id {}".format(org_id))
                return None
            if not is_valid_hex_str(application_id):
                logging.error(
                    "Invalid application id {}".format(application_id))
                return None
            lookup_result = self.__contract_instance.functions.workerLookUp(
                worker_type.value, org_id, application_id).call()

            return _convert_lookup_result_to_json(lookup_result)
        else:
            logging.error(
                "worker registry contract instance is not initialized")
            return None

    def worker_retrieve(self, worker_id, id=None):
        """
        Retrieve the worker identified by worker ID.

        Parameters:
        worker_id  Worker ID of the registry whose details are requested
        id         Optional JSON RPC request ID

        Returns:
        Tuple containing worker status (defined in worker_set_status),
        worker type, organization ID, list of application IDs, and worker
        details (JSON RPC string).

        On error returns None.
        """

        if (self.__contract_instance is not None):
            if not is_valid_hex_str(worker_id):
                logging.error("Invalid worker id {}".format(worker_id))
                return None

            worker_details = self.__contract_instance.functions.workerRetrieve(
                worker_id).call()
            return _convert_retrieve_result_to_json(worker_details)
        else:
            logging.error(
                "worker registry contract instance is not initialized")
            return None

    def worker_lookup_next(self, worker_type, org_id, application_id,
                           lookup_tag):
        """
        Retrieve additional worker lookup results after calling worker_lookup.

        Parameters:
        worker_type         Characteristic of Workers for which you may wish
                            to search
        org_id              Organization ID to which a Worker belongs
        application_id      Optional application type ID that is
                            supported by the worker
        lookup_tag          is returned by a previous call to either this
                            function or to worker_lookup
        id                  Optional Optional JSON RPC request ID


        Returns:
        Tuple containing the following:
        total_count    Total number of entries matching this lookup
                       criteria.  If this number is larger than the number
                       of IDs returned so far, the caller should use
                       lookupTag to call worker_lookup_next to retrieve
                       the rest of the IDs
        new_lookup_tag Optional parameter. If it is returned, it
                       means that there are more matching worker IDs that
                       can be retrieved by calling this function again with
                       this tag as an input parameter
        ids            Array of the worker IDs that match the input parameters

        On error returns None.
        """

        if (self.__contract_instance is not None):
            if not isinstance(worker_type, WorkerType):
                logging.error("Invalid workerType {}".format(worker_type))
                return None
            if not is_valid_hex_str(org_id):
                logging.error("Invalid organization id {}".format(org_id))
                return None
            if not is_valid_hex_str(application_id):
                logging.error("Invalid application id {}".format(org_id))
                return None
            lookup_result = self.__contract_instance.functions\
                .workerLookUpNext(
                    worker_type.value,
                    org_id, application_id, lookup_tag).call()
            return lookup_result
        else:
            logging.error(
                "worker registry contract instance is not initialized")
            return None

    def worker_register(self, worker_id, worker_type, organization_id,
                        application_type_ids, details):
        """
        Register a new worker with details of the worker.

        Parameters:
        worker_id       Worker ID value. E.g., an Ethereum address or
                        a value derived from the worker's DID
        worker_type     Type of Worker. Currently defined types are:
                        * "TEE-SGX": an Intel SGX Trusted Execution
                          Environment
                        * "MPC": Multi-Party Compute
                        * "ZK": Zero-Knowledge
        organization_id Optional parameter representing the
                        organization that hosts the Worker,
                        e.g. a bank in the consortium or
                        anonymous entity
        application_ids Optional parameter that defines
                        application types supported by the Worker
        details         Detailed information about the worker in
                        JSON RPC format as defined in
                https://entethalliance.github.io/trusted-computing/spec.html
                #common-data-for-all-worker-types

        Returns:
        Transaction receipt if registration succeeds.
        None if registration does not succeed.
        """

        if (self.__contract_instance is not None):
            if not is_valid_hex_str(worker_id):
                logging.error("Invalid worker id {}".format(worker_id))
                return None
            if not isinstance(worker_type, WorkerType):
                logging.error("Invalid workerType {}".format(worker_type))
                return None
            if not is_valid_hex_str(organization_id):
                logging.error("Invalid organization id {}"
                              .format(organization_id))
                return None
            for app_id in application_type_ids:
                if not is_valid_hex_str(app_id):
                    logging.error("Invalid application id {}".format(app_id))
                    return None
            # TODO : Validate worker details. As of now worker details are not
            # strictly following the spec
            """if details is not None:
                worker = WorkerDetails()
                is_valid = worker.validate_worker_details(details)
                if is_valid is not None:
                    logging.error(
                        "Worker details not valid : {}".format(is_valid))
                    return None
            """
            txn_dict = self.__contract_instance.functions.workerRegister(
                worker_id, worker_type.value, organization_id,
                application_type_ids, details)\
                .buildTransaction(
                self.__eth_client.get_transaction_params())
            txn_receipt = self.__eth_client.execute_transaction(
                txn_dict)
            return txn_receipt
        else:
            logging.error(
                "worker registry contract instance is not initialized")
            return None

    def worker_update(self, worker_id, details):
        """
        Update a worker with details data.

        Parameters:
        worker_id  Worker ID value. E.g., an Ethereum address or
                   a value derived from the worker's DID
        details    Detailed information about the worker in JSON format

        Returns:
        Transaction receipt if registration succeeds.
        None if registration does not succeed.
        """

        if (self.__contract_instance is not None):
            if not is_valid_hex_str(worker_id):
                logging.error("Invalid worker id {}".format(worker_id))
                return None

            # TODO : Validate worker details. As of now worker details are not
            # strictly following the spec
            """if details is not None:
                worker = WorkerDetails()
                is_valid = worker.validate_worker_details(details)
                if is_valid is not None:
                    logging.error(
                        "Worker details not valid : {}".format(is_valid))
                    return None
            """
            txn_dict = self.__contract_instance.functions.workerUpdate(
                worker_id, details)\
                .buildTransaction(self.__eth_client.get_transaction_params())
            txn_receipt = self.__eth_client.execute_transaction(txn_dict)
            return txn_receipt
        else:
            logging.error(
                "worker registry contract instance is not initialized")
            return None

    def worker_set_status(self, worker_id, status):
        """
        Set the worker status identified by worker ID.

        Parameters:
        worker_id Worker ID value. E.g., an Ethereum address or
                  a value derived from the worker's DID
        status    Worker status. The currently defined values are:
                  1 - worker is active
                  2 - worker is temporarily "off-line"
                  3 - worker is decommissioned
                  4 - worker is compromised

        Returns:
        Transaction receipt if registration succeeds.
        None if registration does not succeed.
        """

        if (self.__contract_instance is not None):
            if not is_valid_hex_str(worker_id):
                logging.error("Invalid worker id {}".format(worker_id))
                return None
            if not isinstance(status, WorkerStatus):
                logging.error("Invalid workerStatus {}".format(status))
                return None

            txn_dict = self.__contract_instance.functions.workerSetStatus(
                worker_id, status.value)\
                .buildTransaction(self.__eth_client.get_transaction_params())
            txn_receipt = self.__eth_client.execute_transaction(txn_dict)
            return txn_receipt
        else:
            logging.error(
                "worker registry contract instance is not initialized")
            return None

    def _is_valid_json(self, json_string):
        try:
            json.loads(json_string)
        except ValueError as e:
            logging.error(e)
            return False
        return True

    def __validate(self, config):
        """
        Validate configuration parameters for existence.

        Parameters:
        config    Ethereum-specific configuration parameters

        Returns:
        True if validation succeeds or false if validation fails.
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

        Parameters:
        config    Ethereum-specific configuration parameters to initialize
        """
        self.__eth_client = EthereumWrapper(config)
        tcf_home = environ.get("TCF_HOME", "../../../")
        contract_file_name = tcf_home + "/" + \
            config["ethereum"]["proxy_worker_registry_contract_file"]
        contract_address = \
            config["ethereum"]["proxy_worker_registry_contract_address"]
        self.__contract_instance, self.__contract_instance_evt = \
            self.__eth_client.get_contract_instance(
                contract_file_name, contract_address
            )


def _convert_lookup_result_to_json(worker_lookup_result):
    """Convert worker lookup result to JSON format."""
    result = {}
    result["totalCount"] = worker_lookup_result[0]
    result["lookupTag"] = worker_lookup_result[1]
    result["ids"] = _convert_byte32_arr_to_hex_arr(worker_lookup_result[2])

    return {"result": result}


def _convert_byte32_arr_to_hex_arr(byte32_arr):
    """
    This function takes in an array of byte32 strings and
    returns an array of hex strings.

    Parameters:
    byte32_arr Strings to convert from a byte32 array to a hex array
    """
    hex_ids = []
    for byte32_str in byte32_arr:
        hex_ids = hex_ids + [byte32_str.hex()]
    return hex_ids


def _convert_retrieve_result_to_json(retrieve_result):
    """
    This function takes in the result retrieved from the blockchain
    and converts it to JSON for external entities.

    Parameters:
    retrieve_result Result to convert from a byte32 array to hex
    """
    result = {}
    result["status"] = retrieve_result[0]
    result["workerType"] = retrieve_result[1]
    result["organizationId"] = retrieve_result[2].hex()
    result["applicationTypeId"] = _convert_byte32_arr_to_hex_arr(
        retrieve_result[3])
    result["details"] = json.loads(retrieve_result[4])

    # Convert to make similar to JRPC response structure
    return {"result": result}


def _convert_retrieve_result_to_hex(retrieve_result):
    """
    This function takes in the result retrieved from the blockchain
    and converts byte32 fields to hex for external entities.

    Parameters:
    retrieve_result Result to convert from a byte32 array to hex
    """
    result = [retrieve_result[0], retrieve_result[1],
              None, None, retrieve_result[4]]
    result[2] = retrieve_result[2].hex()
    result[3] = _convert_byte32_arr_to_hex_arr(
        retrieve_result[3])

    return result