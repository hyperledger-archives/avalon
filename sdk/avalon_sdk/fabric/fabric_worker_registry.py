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

import binascii
import logging
from os import environ

from utility.hex_utils import is_valid_hex_str
from utility.hex_utils import byte_array_to_hex_str

from avalon_sdk.contract_response.contract_response import ContractResponse
from avalon_sdk.worker.worker_details import WorkerStatus, WorkerType
from avalon_sdk.fabric.fabric_wrapper import FabricWrapper
from avalon_sdk.interfaces.worker_registry \
    import WorkerRegistry
from avalon_sdk.worker.worker_details import WorkerDetails

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class FabricWorkerRegistryImpl(WorkerRegistry):
    """
    This class provide worker APIs which interact with
    Fabric blockchain. Detail method description will be
    available in WorkerRegistry interface
    """

    def __init__(self, config):
        """
        config is dict containing fabric specific parameters.
        """
        self.__fabric_wrapper = None
        # Chain code name
        self.CHAIN_CODE = 'worker'
        if config is not None:
            self.__fabric_wrapper = FabricWrapper(config)
        else:
            raise Exception("config is none")

    def worker_lookup(self, worker_type=None, org_id=None,
                      application_id=None, id=None):
        """
        Lookup a worker identified worker_type, org_id and application_id
        all fields are optional and if present condition should match for all
        fields. If none passed it should return all workers.
        Returns tuple containing workers count, lookup tag and list of
        worker ids or on error returns None.
        """
        if (self.__fabric_wrapper is not None):
            params = []
            if worker_type is None:
                params.append(str(0))
            else:
                params.append(str(worker_type.value))

            if org_id is None:
                params.append("")
            else:
                params.append(org_id)

            if application_id is None:
                params.append("")
            else:
                params.append(application_id)

            logging.info("Worker loookup args {}".format(params))
            lookupResult = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'workerLookUp',
                params)
            return lookupResult
        else:
            logging.error("Fabric wrapper instance is not initialized")
            return None

    def worker_retrieve(self, worker_id, id=None):
        """
        Retrieve the worker identified by worker id
        Returns tuple containing worker status, worker type,
        organization id, list of application ids and worker
        details(json string)
        On error returns None
        """
        if (self.__fabric_wrapper is not None):
            params = []
            params.append(worker_id)
            workerDetails = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'workerRetrieve',
                params)
            return workerDetails
        else:
            logging.error("Fabric wrapper instance is not initialized")
            return None

    def worker_lookup_next(self, worker_type, org_id, application_id,
                           lookup_tag, id=None):
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

        Outputs tuple containing following.
        1. total_count is a total number of entries matching this lookup
        criteria.  If this number is larger than the number of ids returned
        so far, the caller should use lookupTag to call workerLookUpNext to
        retrieve the rest of the ids.
        2. new_lookup_tag is an optional parameter. If it is returned, it
        means that there are more matching Worker ids than can be retrieved
        by calling this function again with this tag as an input parameter.
        3. ids is an array of the Worker ids that match the input parameters.
        On error returns None.
        """
        if (self.__fabric_wrapper is not None):
            params = []
            params.append(str(worker_type.value))
            params.append(org_id)
            params.append(application_id)
            params.append(lookup_tag)
            lookupResult = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'workerLookUpNext',
                params)
            return lookupResult
        else:
            logging.error("Fabric wrapper instance is not initialized")
            return None

    def worker_register(
            self, worker_id, worker_type, org_id,
            application_ids, details, id=None):
        """
        Register new worker with details of worker
        Inputs
        1. worker_id is a worker id, e.g. an Fabric address or
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
        Returns ContractResponse.SUCCESS on success
        or ContractResponse.ERROR on error.
        """
        if (self.__fabric_wrapper is not None):
            params = []
            params.append(worker_id)
            params.append(str(worker_type.value))
            params.append(org_id)
            params.append(','.join(application_ids))
            params.append(details)
            txn_status = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'workerRegister',
                params)
            return txn_status
        else:
            logging.error("Fabric wrapper instance is not initialized")
            return ContractResponse.ERROR

    def worker_set_status(self, worker_id, status, id=None):
        """
        Set the registry status identified by worker id
        status is worker type enum type
        Returns ContractResponse.SUCCESS on success
        or ContractResponse.ERROR on error.
        """
        if (self.__fabric_wrapper is not None):
            params = []
            params.append(worker_id)
            params.append(str(status.value))
            txn_status = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'workerSetStatus',
                params)
            return txn_status
        else:
            logging.error("Fabric wrapper instance is not initialized")
            return ContractResponse.ERROR

    def worker_update(self, worker_id, details, id=None):
        """
        Update the worker with details data which is json string
        Updating a Worker
        Inputs
        1. worker_id is a worker id, e.g. an Fabric address or
        a value derived from the worker's DID.
        2. details is detailed information about the worker in JSON format
        Returns ContractResponse.SUCCESS on success
        or ContractResponse.ERROR on error.
        """
        if (self.__fabric_wrapper is not None):
            params = []
            params.append(worker_id)
            params.append(details)
            txn_status = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'workerUpdate',
                params)
            return txn_status
        else:
            logging.error("Fabric wrapper instance is not initialized")
            return ContractResponse.ERROR
