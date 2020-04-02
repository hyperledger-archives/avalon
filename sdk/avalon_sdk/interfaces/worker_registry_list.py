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

from abc import ABC, abstractmethod


class WorkerRegistryList(ABC):
    """
    This is an abstract base class to read/write the worker registries,
    which can be called by client.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def registry_retrieve(self, organization_id):
        """
        Retrieve registry information identified by the organization ID.

        Parameters:
        organization_id      Organization ID to lookup

        Returns:
        Tuple containing following on success:
        uri                  String defines a URI for this registry that
                             supports the Off-Chain Worker Registry JSON RPC
                             API. It will be None for the proxy model
        sc_addr              smart contract address for worker registry
                             smart contract address
        application_type_ids List of application ids (array of byte[])
        status               Status of the registry

        Returns None on error.
        """
        pass

    @abstractmethod
    def registry_lookup(self, application_type_id):
        """
        Registry Lookup identified by application type ID

        Parameters:
        application_type_id  Application type ID to lookup in the registry

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
        pass

    @abstractmethod
    def registry_lookup_next(self, application_type_id, lookup_tag):
        """
        This function is called to retrieve additional results of the
        Registry lookup initiated by the registry_lookUp call.

        Parameters:
        application_type_id    Application type that has to be
                               supported by the workers retrieved
        lookup_tag             Returned by a previous call to either this
                               function or to registry_lookup

        Returns:
        Outputs tuple on success containing the following:
        total_count    Total number of entries matching the lookup
                       criteria. If this number is larger than the number
                       of IDs returned so far, the caller should use
                       lookup_tag to call registry_lookup_next to
                       retrieve the rest of the IDs
        new_lookup_tag Optional parameter. If it is returned, it means
                       that there are more matching registry IDs that
                       can be retrieved by calling this function again
                       with this tag as an input parameter
        ids            Array of the registry IDs that match the input
                       parameters

        Returns None on error.
        """
        pass

    @abstractmethod
    def registry_add(self, organization_id, uri, sc_addr,
                     application_type_ids):
        """
        Add a new registry.

        Parameters:
        organization_id      bytes[] identifies organization that hosts the
                             registry, e.g. a bank in the consortium or an
                             anonymous entity
        uri                  String defines a URI for this registry that
                             supports the Off-Chain Worker Registry
                             JSON RPC API.
        sc_addr              bytes[] defines an smart contract address that
                             runs the Worker Registry Smart Contract API
                             smart contract for this registry
        application_type_ids []bytes[] is an optional parameter that defines
                             application types supported by the worker
                             managed by the registry

        Returns:
        Transaction receipt on success or None on error.
        """
        pass

    @abstractmethod
    def registry_update(self, organization_id, uri, sc_addr,
                        application_type_ids):
        """
        Update a registry.

        Parameters:
        organization_id      bytes[] identifies organization that hosts the
                             registry, e.g. a bank in the consortium or an
                             anonymous entity
        uri                  string defines a URI for this registry that
                             supports the Off-Chain Worker Registry
                             JSON RPC API
        sc_addr              bytes[] defines an smart contract address that
                             runs a Worker Registry Smart Contract API
                             smart contract for this registry
        application_type_ids []bytes[] is an optional parameter that defines
                             application types supported by the worker
                             managed by the registry

        Returns:
        Transaction receipt on success or None on error.
        """
        pass

    @abstractmethod
    def registry_set_status(self, organization_id, status):
        """
        Set registry status.

        Parameters:
        organization_id bytes[] identifies organization that hosts the
                        registry, e.g. a bank in the consortium or an
                        anonymous entity
        status          Defines the registry status to set.
                        The currently defined values are:
                        1 - the registry is active
                        2 - the registry is temporarily "off-line"
                        3 - the registry is decommissioned

        Returns:
        Transaction receipt on success or None on error.
        """
        pass
