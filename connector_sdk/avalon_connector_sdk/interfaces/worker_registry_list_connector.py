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


class WorkerRegistryListConnector(ABC):
    """
    This is an interface with abstract methods to interact
    with registry like add, update, set status etc.
    """

    def __init__(self):
        super().__init__()

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
