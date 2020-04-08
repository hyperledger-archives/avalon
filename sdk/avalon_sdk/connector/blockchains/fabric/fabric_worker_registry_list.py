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

from utility.hex_utils import byte_array_to_hex_str
from avalon_sdk.connector.interfaces.worker_registry_list \
    import WorkerRegistryList
from avalon_sdk.registry.registry_status import RegistryStatus
from avalon_sdk.connector.blockchains.fabric.fabric_wrapper \
    import FabricWrapper

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class FabricWorkerRegistryListImpl(WorkerRegistryList):
    """
    This class provide APIs to read/write registry entries of workers,
    which is stored in the Hyperledger Fabric blockchain.
    """
    def __init__(self, config):
        """
        Parameters:
        config    Dictionary containing Fabric-specific parameters.
        """
        self.__fabric_wrapper = None
        # Chain code name
        self.CHAIN_CODE = 'registry'
        if config is not None:
            self.__fabric_wrapper = FabricWrapper(config)
        else:
            raise Exception("config is none")

    def registry_lookup(self, app_type_id=None):
        """
        Registry Lookup identified by application type ID

        Parameters:
        app_type_id  Application type ID to lookup in the registry

        Returns:
        Tuple containing totalCount, lookupTag, and ids on success:
        totalCount Total number of entries matching a specified lookup
                   criteria. If this number is larger than the size of the
                   ids array, the caller should use the lookupTag to call
                   registry_lookup_next to retrieve the rest of the IDs
        lookupTag  Optional parameter. If it is returned, it means that
                   there are more matching registry IDs that can be
                   retrieved by calling the function registry_lookup_next
                   with this tag as an input parameter.
        ids        Array of the registry organization ids that match the
                   input parameters.

        Returns None on error.
        """
        if (self.__fabric_wrapper is not None):
            if app_type_id is not None:
                if is_valid_hex_str(binascii.hexlify(app_type_id).decode(
                        "utf8")):
                    params = []
                    params.append(byte_array_to_hex_str(app_type_id))
                    lookupResult = \
                        self.__fabric_wrapper.invoke_chaincode(
                            self.CHAIN_CODE,
                            'registryLookUp',
                            params)
                else:
                    logging.info(
                        "Invalid application type id {}".format(app_type_id))
                    return None
        else:
            logging.error(
                "Fabric wrapper instance is not initialized")
            return None

    def registry_retrieve(self, org_id):
        """
        Retrieve registry information identified by the organization ID.

        Parameters:
        org_id                Organization ID to lookup

        Returns:
        Tuple containing following on success:
        uri                  String defines a URI for this registry that
                             supports the Off-Chain Worker Registry JSON RPC
                             API. It will be None for the proxy model
        sc_addr              Fabric address for worker registry
                             smart contract address
        application_type_ids List of application ids (array of byte[])
        status               Status of the registry

        Returns None on error.
        """
        if (self.__fabric_wrapper is not None):
            if (is_valid_hex_str(binascii.hexlify(org_id).decode("utf8"))
                    is False):
                logging.info("Invalid Org id {}".format(org_id))
                return None
            else:
                params = []
                params.append(byte_array_to_hex_str(org_id))
                registryDetails = \
                    self.__fabric_wrapper.invoke_chaincode(
                        self.CHAIN_CODE,
                        'registryRetrieve',
                        params
                    )
                return registryDetails
        else:
            logging.error(
                "Fabric wrapper instance is not initialized")
            return None

    def registry_lookup_next(self, app_type_id, lookup_tag):
        """
        Get additional registry lookup results.
        This function is called to retrieve additional results of the
        Registry lookup initiated by the registry_lookup call.

        Parameters:
        app_type_id    Application type ID that has to be
                       supported by the workers retrieved
        lookup_tag     Returned by a previous call to either this function
                       or to registry_lookup

        Returns:
        Outputs a tuple on success containing the following:
        total_count    Total number of entries matching the lookup
                       criteria. If this number is larger than the number
                       of IDs returned so far, the caller should use
                       lookup_tag to call registry_lookup_next to
                       retrieve the rest of the IDs
        new_lookup_tag is an optional parameter. If it is returned, it means
                       that there are more matching registry IDs that can be
                       retrieved by calling this function again with this tag
                       as an input parameter
        ids            Array of the registry IDs that match the input
                       parameters

        Returns None on error.
        """
        if (self.__fabric_wrapper is not None):
            if is_valid_hex_str(binascii.hexlify(app_type_id).decode("utf8")):
                params = []
                params.append(byte_array_to_hex_str(app_type_id))
                params.append(lookup_tag)
                lookupResult = self.__fabric_wrapper.invoke_chaincode(
                            self.CHAIN_CODE,
                            'registryLookUpNext',
                            params)
            else:
                logging.info(
                    "Invalid application type id {}".format(app_type_id))
                return None
        else:
            logging.error(
                "Fabric wrapper instance is not initialized")
            return None

    def registry_add(self, org_id, uri, sc_addr, app_type_ids):
        """
        Add a new registry.

        Parameters:
        org_id       bytes[] identifies organization that hosts the
                     registry, e.g. a bank in the consortium or an
                     anonymous entity
        uri          String defining a URI for this registry that
                     supports the Off-Chain Worker Registry
                     JSON RPC API
        sc_addr      bytes[] defines a Fabric chain code name that
                     runs the Worker Registry Smart Contract API
                     smart contract for this registry
        app_type_ids []bytes[] is an optional parameter that defines
                     application types supported by the worker
                     managed by the registry

        Returns:
        Transaction receipt on success or None on error.
        """
        if (self.__fabric_wrapper is not None):
            if (is_valid_hex_str(binascii.hexlify(org_id).decode("utf8"))
                    is False):
                logging.info("Invalid Org id {}".format(org_id))
                return None
            if (sc_addr is not None and is_valid_hex_str(
                    binascii.hexlify(sc_addr).decode("utf8")) is False):
                logging.info("Invalid smart contract name {}")
                return None
            if (not uri):
                logging.info("Empty uri {}".format(uri))
                return None
            app_ids = []
            for aid in app_type_ids:
                if (is_valid_hex_str(binascii.hexlify(aid).decode("utf8"))
                        is False):
                    logging.info("Invalid application id {}".format(aid))
                    return None
                else:
                    app_ids.append(byte_array_to_hex_str(aid))

            params = []
            params.append(byte_array_to_hex_str(org_id))
            params.append(uri)
            params.append(byte_array_to_hex_str(sc_addr))
            params.append(','.join(app_ids))
            txn_status = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'registryAdd',
                params)
            return txn_status
        else:
            logging.error(
                "Fabric wrapper instance is not initialized")
            return None

    def registry_update(self, org_id, uri, sc_addr, app_type_ids):
        """
        Update a registry.

        Parameters:
        org_id       bytes[] identifies organization that hosts the
                     registry, e.g. a bank in the consortium or an
                     anonymous entity
        uri          string that defines a URI for this registry that
                     supports the Off-Chain Worker Registry
                     JSON RPC API
        sc_addr      bytes[] defines a Fabric chain code name that
                     runs the Worker Registry Smart Contract API
                     smart contract for this registry
        app_type_ids []bytes[] is an optional parameter that defines
                     application types supported by the worker
                     managed by the registry

        Returns:
        Transaction receipt on success or None on error.
        """
        if (self.__fabric_wrapper is not None):
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
            app_ids = []
            for aid in app_type_ids:
                if (is_valid_hex_str(binascii.hexlify(aid).decode("utf8"))
                        is False):
                    logging.error("Invalid application id {}".format(aid))
                    return None
                else:
                    app_ids.append(byte_array_to_hex_str(aid))

            params = []
            params.append(byte_array_to_hex_str(org_id))
            params.append(uri)
            params.append(byte_array_to_hex_str(sc_addr))
            params.append(','.join(app_ids))
            txn_status = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'registryUpdate',
                params)
            return txn_status
        else:
            logging.error(
                "Fabric wrapper instance is not initialized")
            return None

    def registry_set_status(self, org_id, status):
        """
        Set registry status.

        Parameters:
        org_id  bytes[] identifies organization that hosts the
                registry, e.g. a bank in the consortium or an
                anonymous entity
        status  Defines the registry status to set.
                The currently defined values are:
                1 - the registry is active
                2 - the registry is temporarily "off-line"
                3 - the registry is decommissioned

        Returns:
        Transaction receipt on success or None on error.
        """
        if (self.__fabric_wrapper is not None):
            if (is_valid_hex_str(binascii.hexlify(org_id).decode("utf8"))
                    is False):
                logging.info("Invalid Org id {}".format(org_id))
                return None
            if not isinstance(status, RegistryStatus):
                logging.info("Invalid registry status {}".format(status))
                return None
            params = []
            params.append(byte_array_to_hex_str(org_id))
            params.append(str(status))
            txn_status = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'registrySetStatus',
                params)
            return txn_status
        else:
            logging.error(
                "Fabric wrapper instance is not initialized")
            return None
