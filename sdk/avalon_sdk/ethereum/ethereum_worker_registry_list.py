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

from utility.hex_utils import is_valid_hex_str
import binascii
from os import environ

from avalon_sdk.interfaces.worker_registry_list \
    import WorkerRegistryList
from avalon_sdk.ethereum.ethereum_wrapper import EthereumWrapper
from avalon_sdk.registry.registry_status import RegistryStatus

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class EthereumWorkerRegistryListImpl(WorkerRegistryList):
    """
    This class provide APIs to read/write registry entries of workers,
    which is stored in Ethereum blockchain.
    """

    def __init__(self, config):
        if self.__validate(config):
            self.__initialize(config)
        else:
            raise Exception("Invalid or missing config parameter")

    def registry_lookup(self, app_type_id=None):
        """
        Registry Lookup identified by application type id
        It returns following
        1. totalCount is the total number of entries matching a specified
        lookup criteria.  If this number is larger than the size of the ids
        array, the caller should use the lookupTag to call workerLookUpNext
        to retrieve the rest of the ids.
        2. lookupTag is an optional parameter. If it is returned, it means that
        there are more matching registry ids that can be retrieved by calling
        the function registry_lookup_next with this tag as an input parameter.
        3. ids is an array of the registry organization ids that match the
        input parameters
        Returns tuple containing count, lookup tag and list of organization
        ids on success and returns None on error.
        """
        if (self.__contract_instance is not None):
            if app_type_id is not None:
                if is_valid_hex_str(binascii.hexlify(app_type_id).decode(
                        "utf8")):
                    lookupResult = \
                        self.__contract_instance.functions.registryLookUp(
                            app_type_id).call()
                else:
                    logging.info(
                        "Invalid application type id {}".format(app_type_id))
                    return None
            else:
                lookupResult = \
                    self.__contract_instance.functions.registryLookUp(b"") \
                    .call()
            return lookupResult
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return None

    def registry_retrieve(self, org_id):
        """
        Retrieving Registry Information identified by organization id
        It returns tuple containing following on success.
        1. uri is string defines a URI for this registry that supports the
        Off-Chain Worker Registry JSON RPC API. It is going to be None
        for proxy model.
        2. sc_addr Ethereum address for worker registry smart contract
        address.
        3. application_type_ids list of application ids(array of byte[])
        4. status of the registry
        Returns None on error.
        """
        if (self.__contract_instance is not None):
            if (is_valid_hex_str(binascii.hexlify(org_id).decode("utf8"))
                    is False):
                logging.info("Invalid Org id {}".format(org_id))
                return None
            else:
                registryDetails = \
                    self.__contract_instance.functions.registryRetrieve(
                        org_id).call()
                return registryDetails
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return None

    def registry_lookup_next(self, app_type_id, lookup_tag):
        """
        Getting Additional Registry Lookup Results
        This function is called to retrieve additional results of the
        Registry lookup initiated by the registryLookUp call.
        Inputs
        1. application_type_id is an application type that has to be
        supported by the workers retrieved.
        2. lookup_tag is returned by a previous call to either this function
        or to registryLookUp.

        Outputs tuple on success containing the below.
        1. total_count is a total number of entries matching the lookup
        criteria. If this number is larger than the number of ids returned
        so far, the caller should use lookup_tag to call registry_lookup_next
        to retrieve the rest of the ids.
        2. new_lookup_tag is an optional parameter. If it is returned, it means
        that there are more matching registry ids that can be retrieved by
        calling this function again with this tag as an input parameter.
        3. ids is an array of the registry ids that match the input parameters
        Returns None on error.
        """
        if (self.__contract_instance is not None):
            if is_valid_hex_str(binascii.hexlify(app_type_id).decode("utf8")):
                lookupResult = \
                    self.__contract_instance.functions.registryLookUpNext(
                        app_type_id, lookup_tag).call()
                return lookupResult
            else:
                logging.info(
                    "Invalid application type id {}".format(app_type_id))
                return None
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return None

    def __validate(self, config):
        """
        validates parameter from config parameters for existence.
        Returns false if validation fails and true if it success
        """
        if config["ethereum"]["direct_registry_contract_file"] is None:
            logging.error("Missing direct registry contract file path!!")
            return False
        if config["ethereum"]["direct_registry_contract_address"] is None:
            logging.error("Missing direct registry contract address!!")
            return False
        return True

    def __initialize(self, config):
        """
        Initialize the parameters from config to instance variables.
        """
        self.__eth_client = EthereumWrapper(config)
        tcf_home = environ.get("TCF_HOME", "../../../")
        contract_file_name = tcf_home + "/" + \
            config["ethereum"]["direct_registry_contract_file"]
        contract_address = \
            config["ethereum"]["direct_registry_contract_address"]
        self.__contract_instance = self.__eth_client.get_contract_instance(
            contract_file_name, contract_address
        )

    def registry_add(self, org_id, uri, sc_addr, app_type_ids):
        """
        Adding a new registry
        Inputs
        1. organization_id bytes[] identifies organization that hosts the
        registry, e.g. a bank in the consortium or anonymous entity.
        2. uri string defines a URI for this registry that supports
        the Off-Chain Worker Registry JSON RPC API.
        3. sc_addr bytes[] defines an Ethereum address that runs the
        Worker Registry Smart Contract API smart contract for this registry.
        4. app_type_ids []bytes[] is an optional parameter that defines
        application types supported by the worker managed by the registry.
        Returns transaction receipt on success or None on error.
        """
        if (self.__contract_instance is not None):
            if (is_valid_hex_str(binascii.hexlify(org_id).decode("utf8"))
                    is False):
                logging.info("Invalid Org id {}".format(org_id))
                return None
            if (sc_addr is not None and is_valid_hex_str(
                    binascii.hexlify(sc_addr).decode("utf8")) is False):
                logging.info("Invalid smart contract address {}")
                return None
            if (not uri):
                logging.info("Empty uri {}".format(uri))
                return None
            for aid in app_type_ids:
                if (is_valid_hex_str(binascii.hexlify(aid).decode("utf8"))
                        is False):
                    logging.info("Invalid application id {}".format(aid))
                    return None

            txn_statusn_hash = self.__contract_instance.functions.registryAdd(
                org_id, uri, org_id, app_type_ids).buildTransaction(
                    self.__eth_client.get_transaction_params()
            )
            txn_status = self.__eth_client.execute_transaction(
                txn_statusn_hash)
            return txn_status
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return None

    def registry_update(self, org_id, uri, sc_addr, app_type_ids):
        """
        Update a registry
        Inputs
        1. organization_id bytes[] identifies organization that hosts the
        registry, e.g. a bank in the consortium or anonymous entity.
        2. uri string defines a URI for this registry that supports the
        Off-Chain Worker Registry JSON RPC API.
        3. sc_addr bytes[] defines an Ethereum address that runs a
        Worker Registry Smart Contract API smart contract for this registry.
        4. application_type_ids []bytes[] is an optional parameter that defines
        application types supported by the worker managed by the registry.
        Returns transaction receipt on success or None on error.
        """
        if (self.__contract_instance is not None):
            if (is_valid_hex_str(binascii.hexlify(org_id).decode("utf8"))
                    is False):
                logging.error("Invalid Org id {}".format(org_id))
                return None
            if (sc_addr is not None and is_valid_hex_str(
                    binascii.hexlify(sc_addr).decode("utf8")) is False):
                logging.error(
                    "Invalid smart contract address {}".format(sc_addr))
                return None
            if (not uri):
                logging.error("Empty uri {}".format(uri))
                return None
            for aid in app_type_ids:
                if (is_valid_hex_str(binascii.hexlify(aid).decode("utf8"))
                        is False):
                    logging.error("Invalid application id {}".format(aid))
                    return None

            txn_statusn_hash = \
                self.__contract_instance.functions.registryUpdate(
                    org_id, uri, sc_addr,
                    app_type_ids).buildTransaction(
                        self.__eth_client.get_transaction_params()
                        )
            txn_status = self.__eth_client.execute_transaction(
                txn_statusn_hash)
            return txn_status
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return None

    def registry_set_status(self, org_id, status):
        """
        Setting Registry Status
        Inputs
        1. organization_id bytes[] identifies organization that hosts the
        registry
        2. status defines registry status to set. The currently defined values
        are:
            1 - indicates that the registry is active
            2 - indicates that the registry is "off-line" (temporarily)
            3 - indicates that the registry is decommissioned
        Returns transaction receipt on success or None on error.
        """
        if (self.__contract_instance is not None):
            if (is_valid_hex_str(binascii.hexlify(org_id).decode("utf8"))
                    is False):
                logging.info("Invalid Org id {}".format(org_id))
                return None
            if not isinstance(status, RegistryStatus):
                logging.info("Invalid registry status {}".format(status))
                return None
            txn_statusn_hash = \
                self.__contract_instance.functions.registrySetStatus(
                    org_id,
                    status.value).buildTransaction(
                        self.__eth_client.get_transaction_params()
                        )
            txn_status = self.__eth_client.execute_transaction(
                txn_statusn_hash)
            return txn_status
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return None
