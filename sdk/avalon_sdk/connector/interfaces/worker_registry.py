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


class WorkerRegistry(ABC):
    """
    This class is an abstract base class containing abstract APIs
    which can be called from client to manage workers.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def worker_retrieve(self, worker_id, id=None):
        """
        Retrieve worker identified by worker ID.

        Parameters:
        worker_id  Worker ID of the registry whose details are requested
        id         Optional JSON RPC request ID

        Returns:
        Tuple containing worker status (defined in worker_set_status),
        worker type, organization ID, list of application IDs, and worker
        details (JSON RPC string).

        On error returns None.
        """
        pass

    @abstractmethod
    def worker_lookup(self, worker_type, organization_id, application_type_id,
                      id=None):
        """
        Lookup a worker identified worker_type, organization, and
        application_id.
        All fields are optional and, if present, condition should match for
        all fields. If none are passed it should return all workers.

        If the list is too large to fit into a single response (the maximum
        number of entries in a single response is implementation specific),
        the smart contract should return the first batch of the results
        and provide a lookupTag that can be used by the caller to
        retrieve the next batch by calling worker_lookup_next.

        Parameters:
        worker_type     Optional characteristic of workers for which you may
                        wish to search
        organization_id Optional organization ID that can be used to search
                        for one or more workers that belong to this
                        organization
        application_id  Optional application type ID that is supported by
                        the worker
        id              Optional JSON RPC request ID

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
        pass

    @abstractmethod
    def worker_lookup_next(self, worker_type, organization_id,
                           application_type_id, lookup_tag, id=None):
        """
        Retrieve additional worker lookup results after calling worker_lookup.

        Parameters:
        worker_type         Characteristic of Workers for which you may wish
                            to search.
        organization_id     Organization ID to which a Worker belongs
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
        pass

    @abstractmethod
    def worker_register(self, worker_id, worker_type, organization_id,
                        application_type_ids, details, id=None):
        """
        Register a new worker with details of the worker.

        Parameters:
        worker_id       Worker ID value. E.g., a Fabric address
                        or Ethereum DID
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
        id              Optional Optional JSON RPC request ID

        Returns:
        ContractResponse.SUCCESS on success or
        ContractResponse.ERROR on error.
        """
        pass

    @abstractmethod
    def worker_update(self, worker_id, details, id=None):
        """
        Update a worker with details data.

        Parameters:
        worker_id  Worker ID
        details    Detailed information about the worker in JSON format
        id         Optional Optional JSON RPC request ID

        Returns:
        ContractResponse.SUCCESS on success
        or ContractResponse.ERROR on error.
        """
        pass

    @abstractmethod
    def worker_set_status(self, worker_id, status, id=None):
        """
        Set the registry status identified by worker ID

        Parameters:
        worker_id Worker ID value. E.g., a Fabric address
                  or Ethereum DID
        status    Worker status. The currently defined values are:
                  1 - worker is active
                  2 - worker is temporarily "off-line"
                  3 - worker is decommissioned
                  4 - worker is compromised
        id        Optional Optional JSON RPC request ID

        Returns:
        ContractResponse.SUCCESS on success
        or ContractResponse.ERROR on error.
        """
        pass
