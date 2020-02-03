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
    This is abstract base class to read/write registries of worker
    which can be called by client.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def registry_retrieve(self, organization_id):
        """
        Retrieving Registry Information identified by organization id
        It returns the following
        1. uri is string defines a URI for this registry that supports the
        Off-Chain Worker Registry JSON RPC API.
        2. sc_addr Ethereum address for worker registry smart contract
        3. application_type_ids list of application ids(array of byte[])
        4. status of the registry
        """
        pass

    @abstractmethod
    def registry_lookup(self, application_type_id):
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
        """
        pass

    @abstractmethod
    def registry_lookup_next(self, application_type_id, lookup_tag):
        """
        Getting Additional Registry Lookup Results
        This function is called to retrieve additional results of the
        Registry lookup initiated by the registryLookUp call.
        Inputs
        1. application_type_id is an application type that has to be
        supported by the workers retrieved.
        2. lookup_tag is returned by a previous call to either this function
        or to registryLookUp.

        Outputs
        1. total_count is a total number of entries matching the lookup
        criteria. If this number is larger than the number of ids returned
        so far, the caller should use lookup_tag to call registry_lookup_next
        to retrieve the rest of the ids.
        2. new_lookup_tag is an optional parameter. If it is returned, it means
        that there are more matching registry ids that can be retrieved by
        calling this function again with this tag as an input parameter.
        3. ids is an array of the registry ids that match the input parameters
        """
        pass

    @abstractmethod
    def registry_add(self, organization_id, uri, sc_addr,
                     application_type_ids):
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
        """
        pass

    @abstractmethod
    def registry_update(self, organization_id, uri, sc_addr,
                        application_type_ids):
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
        """
        pass

    @abstractmethod
    def registry_set_status(self, organization_id, status):
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
        """
        pass
