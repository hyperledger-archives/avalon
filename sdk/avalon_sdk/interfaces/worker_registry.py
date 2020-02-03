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
        Retrieve worker by worker id
        Inputs
        1. worker_id is the id of the registry whose details are requested.
        Outputs
        The same as the input parameters to the corresponding call to
        worker_register()
        plus status as defined in worker_set_status.
        2. id is used for json rpc request
        """
        pass

    @abstractmethod
    def worker_lookup(self, worker_type, organization_id, application_type_id,
                      id=None):
        """
        Initiating Worker lookup
        This function retrieves a list of Worker ids that match the input
        parameters.
        The Worker must match all input parameters (AND mode) to be included
        in the list.
        If the list is too large to fit into a single response (the maximum
        number of entries in a single response is implementation specific),
        the smart contract should return the first batch of the results
        and provide a lookupTag that can be used by the caller to
        retrieve the next batch by calling worker_lookup_next.

        All input parameters are optional and can be provided in any
        combination to select Workers.

        Inputs
        1. worker_type is a characteristic of Workers for which you may wish
        to search
        2. organization_id is an id of an organization that can be used to
        search for one or more Workers that belong to this organization
        3. application_type_id is an application type that is supported by
        the Worker
        4. id is used for json rpc request

        Outputs
        1. total_count is a total number of entries matching a specified
        lookup criteria. If this number is bigger than size of ids array,
        the caller should use lookupTag to call workerLookUpNext to
        retrieve the rest of the ids.
        2. lookup_tag is an optional parameter. If it is returned, it means
        that there are more matching Worker ids that can be retrieved by
        calling function workerLookUpNext with this tag as an input parameter.
        3. ids is an array of the Worker ids that match the input parameters.
        """
        pass

    @abstractmethod
    def worker_lookup_next(self, worker_type, organization_id,
                           application_type_id, lookup_tag, id=None):
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

        Outputs
        1. total_count is a total number of entries matching this lookup
        criteria.  If this number is larger than the number of ids returned
        so far, the caller should use lookupTag to call workerLookUpNext to
        retrieve the rest of the ids.
        2. new_lookup_tag is an optional parameter. If it is returned, it
        means that there are more matching Worker ids than can be retrieved
        by calling this function again with this tag as an input parameter.
        3. ids is an array of the Worker ids that match the input parameters.
        """
        pass

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
