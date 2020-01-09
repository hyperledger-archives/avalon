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


class WorkerRegistryConnector(ABC):
    """
    This is an abstract base class containing abstract APIs
    which need to implemented by an actual blockchain connector
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def worker_register(self, worker_id, worker_type, organization_id,
                        application_type_ids, details, id=None):
        """
        Registering a New Worker
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
        6. id is used for json rpc request
        """
        pass

    @abstractmethod
    def worker_update(self, worker_id, details, id=None):
        """
        Updating a Worker
        Inputs
        1. worker_id is a worker id, e.g. an Ethereum address or
        a value derived from the worker's DID.
        2. details is detailed information about the worker in JSON format
        3. id is used for json rpc request
        """
        pass

    @abstractmethod
    def worker_set_status(self, worker_id, status, id=None):
        """
        Set the worker status identified by worker id
        Inputs
        1. worker_id is a worker id
        2. status defines Worker status. The currently defined values are:
            1 - indicates that the worker is active
            2 - indicates that the worker is "off-line" (temporarily)
            3 - indicates that the worker is decommissioned
            4 - indicates that the worker is compromised
        3. id is used for json rpc request
        """
        pass

