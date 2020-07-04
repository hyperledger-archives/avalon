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

from avalon_sdk.connector.interfaces.worker_registry_list \
    import WorkerRegistryList
from avalon_sdk.connector.blockchains.ethereum.ethereum_wrapper \
    import EthereumWrapper
from avalon_sdk.registry.registry_status import RegistryStatus

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class EthereumWorkerRegistryListImpl(WorkerRegistryList):
    """
    This class provide APIs to read/write registry entries of workers,
    which is stored in the Ethereum blockchain.
    """

    def __init__(self, config):
        if self.__validate(config):
            self.__initialize(config)
        else:
            raise Exception("Invalid or missing config parameter")

    def registry_lookup(self, app_type_id=None):
        """
        Registry Lookup identified by application type ID.

        Parameters:
        app_type_id  Application type ID to lookup in the registry

        Returns:
        Returns tuple containing totalCount, lookupTag, ids on success:
        totalCount Total number of entries matching a specified
                   lookup criteria.  If this number is larger than the size
                   of the IDs array, the caller should use the lookupTag to
                   call workerLookUpNext to retrieve the rest of the IDs
        lookupTag  Optional parameter. If it is returned, it means that
                   there are more matching registry IDs that can be retrieved
                   by calling the function registry_lookup_next with this tag
                   as an input parameter
        ids        Array of the registry organization IDs that match the
                   input parameters

        Returns None on error.
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
                lookup_result = \
                    self.__contract_instance.functions.registryLookUp(b"") \
                    .call()
            return lookup_result
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return None

    def registry_retrieve(self, org_id):
        """
        Retrieving Registry Information identified by organization ID.

        Parameters:
        org_id     Organization ID to lookup

        Returns:
        Tuple containing following on success:
        uri                  string defining a URI for this registry that
                             supports the Off-Chain Worker Registry JSON
                             RPC API. It will be None for the proxy model
        sc_addr              Ethereum address for worker registry
                             smart contract address
        application_type_ids List of application ids(array of byte[])
        status               Status of the registry

        Returns None on error.
        """
        if (self.__contract_instance is not None):
            if (is_valid_hex_str(binascii.hexlify(org_id).decode("utf8"))
                    is False):
                logging.info("Invalid Org id {}".format(org_id))
                return None
            else:
                registry_details = \
                    self.__contract_instance.functions.registryRetrieve(
                        org_id).call()
                return registry_details
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return None

    def registry_lookup_next(self, app_type_id, lookup_tag):
        """
        Get additional registry lookup results.
        This function is called to retrieve additional results of the
        Registry lookup initiated by the registry_lookUp call.

        Parameters:
        app_type_id    Application type that has to be
                       supported by the workers retrieved
        lookup_tag     Returned by a previous call to either this
                       function or to registry_lookup

        Returns:
        Outputs tuple on success containing the following:
        total_count    Total number of entries matching the lookup
                       criteria. If this number is larger than the number
                       of IDs returned so far, the caller should use
                       lookup_tag to call registry_lookup_next to
                       the rest of the ids
        new_lookup_tag Optional parameter. If it is returned, it means
                       that there are more matching registry IDs that
                       can be retrieved by calling this function again
                       with this tag as an input parameter
        ids            Array of the registry IDs that match the input
                       parameters

        Returns None on error.
        """
        if (self.__contract_instance is not None):
            if is_valid_hex_str(binascii.hexlify(app_type_id).decode("utf8")):
                lookup_result = \
                    self.__contract_instance.functions.registryLookUpNext(
                        app_type_id, lookup_tag).call()
                return lookup_result
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
        Validates parameter from config parameters for existence.

        Parameters:
        config    Configuration parameters to validate

        Returns:
        true on success or false if validation fails.
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
        self.__contract_instance, _ = self.__eth_client.get_contract_instance(
            contract_file_name, contract_address
        )

    def registry_add(self, org_id, uri, sc_addr, app_type_ids):
        """
        Add a new registry.

        Parameters:
        org_id       bytes[] identifies organization that hosts the
                     registry, e.g. a bank in the consortium or an
                     anonymous entity
        uri          String defines a URI for this registry that
                     supports the Off-Chain Worker Registry
                     JSON RPC API.
        sc_addr      bytes[] defines an Ethereum address that
                     runs the Worker Registry Smart Contract API
                     smart contract for this registry
        app_type_ids []bytes[] is an optional parameter that defines
                     application types supported by the worker
                     managed by the registry

        Returns:
        Transaction receipt on success or None on error.
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
            contract_func = \
                self.__contract_instance.functions.registryAdd(
                    org_id, uri, org_id, app_type_ids)
            txn_receipt = self.__eth_client.build_exec_txn(contract_func)
            return txn_receipt
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return None

    def registry_update(self, org_id, uri, sc_addr, app_type_ids):
        """
        Update a registry.

        Parameters:
        org_id               bytes[] identifies organization that hosts the
                             registry, e.g. a bank in the consortium or
                             an anonymous entity
        uri                  string defines a URI for this registry that
                             supports the Off-Chain Worker Registry
                             JSON RPC API
        sc_addr              bytes[] defines an Ethereum address that
                             runs a Worker Registry Smart Contract API
                             smart contract for this registry
        app_type_ids         []bytes[] is an optional parameter that defines
                             application types supported by the worker
                             managed by the registry

        Returns:
        Transaction receipt on success or None on error.
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
            contract_func = \
                self.__contract_instance.functions.registryUpdate(
                    org_id, uri, sc_addr, app_type_ids)
            txn_receipt = self.__eth_client.build_exec_txn(contract_func)
            return txn_receipt
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return None

    def registry_set_status(self, org_id, status):
        """
        Set registry status.

        Parameters:
        org_id  bytes[] identifies organization that hosts
                the registry
        status  Defines registry status to set.
                The currently defined values are:
                1 - the registry is active
                2 - the registry is temporarily "off-line"
                3 - the registry is decommissioned

        Returns:
        Transaction receipt on success or None on error.
        """
        if (self.__contract_instance is not None):
            if (is_valid_hex_str(binascii.hexlify(org_id).decode("utf8"))
                    is False):
                logging.info("Invalid Org id {}".format(org_id))
                return None
            if not isinstance(status, RegistryStatus):
                logging.info("Invalid registry status {}".format(status))
                return None
            contract_func = \
                self.__contract_instance.functions.registrySetStatus(
                    org_id, status.value)
            txn_receipt = self.__eth_client.build_exec_txn(contract_func)
            return txn_receipt
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return None
