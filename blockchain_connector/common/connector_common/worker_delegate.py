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

import json
import random
import logging
from avalon_sdk.worker.worker_details import WorkerType, WorkerStatus
import avalon_sdk.worker.worker_details as worker_details
from avalon_sdk.connector.blockchains.common.contract_response \
    import ContractResponse

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class WorkerDelegate():

    """
    Helper class to sync workers between avalon and blockchain
    """

    def __init__(self, config, jrpc_worker, worker_instance):
        """
        Initialize the connector with instances of jrpc worker
        implementation and blockchain worker implementation objects.
        @param config - dict containing connector configurations
        @param jrpc_worker - implementation class object JRPC worker
        @param worker_instance - worker blockchain implementation class
        """
        self._jrpc_worker = jrpc_worker
        self._worker_instance = worker_instance
        self._config = config
        # Map to store worker id to worker details mapping over the lifespan
        # of the connector. Before updating a worker, this map is looked up.
        self._worker_details_map = dict()
        # Map to store worker id to worker status mapping over the lifespan
        # of the connector. Before setting status of a worker,
        # this map is looked up.
        self._worker_status_map = dict()

    def lookup_workers_in_kv_storage(self):
        """
        This function retrieves the worker ids from shared kv using
        worker_lookup direct API.
        Returns list of worker id
        """

        jrpc_req_id = random.randint(0, 100000)

        worker_lookup_result = self._jrpc_worker.worker_lookup(
            worker_type=WorkerType.TEE_SGX, id=jrpc_req_id
        )
        logging.info("\nWorker lookup response from kv storage : {}\n".format(
            json.dumps(worker_lookup_result, indent=4)
        ))
        if "result" in worker_lookup_result and \
                "ids" in worker_lookup_result["result"].keys():
            if worker_lookup_result["result"]["totalCount"] != 0:
                return worker_lookup_result["result"]["ids"]
            else:
                logging.error("No workers found in kv storage")
        else:
            logging.error("Failed to lookup worker in kv storage")
        return []

    def _retrieve_worker_details_from_kv_storage(self,
                                                 worker_id):
        # Retrieve worker details
        jrpc_req_id = random.randint(0, 100000)
        worker_info = self._jrpc_worker.worker_retrieve(worker_id, jrpc_req_id)
        logging.debug("Worker retrieve response from kv storage: {}"
                      .format(json.dumps(worker_info, indent=4)))

        if "error" in worker_info:
            logging.error("Unable to retrieve worker details from kv storage")
            None
        return worker_info["result"]

    def add_update_worker_to_chain(self, wids_in_kv, wids_onchain):
        """
        This function adds/updates a worker in the  blockchain
        @param wids_in_kv - worker ids in shared KV
        @param wids_onchain - worker ids in blockchain
        """

        for wid in wids_in_kv:
            worker_info = self._retrieve_worker_details_from_kv_storage(
                wid)
            if worker_info is None:
                continue
            worker_type = WorkerType(worker_info["workerType"])
            org_id = worker_info["organizationId"]
            app_type_id = worker_info["applicationTypeId"]
            details = json.dumps(worker_info["details"])

            result = None
            if wid in wids_onchain:
                if wid not in self._worker_details_map or \
                        self._worker_details_map[wid] != details:
                    result = self._worker_instance.worker_update(
                        wid, details)
                    if result != ContractResponse.SUCCESS:
                        logging.error("Error while updating worker {}"
                                      " to blockchain".format(wid))
                    else:
                        logging.info("Updated worker {} to blockchain"
                                     .format(wid))
                        self._worker_details_map[wid] = details
                        # Update status of worker as active explicitly if a
                        # worker is updated, as worker status is not part of
                        # worker update.
                        if wid is not self._worker_status_map or \
                                self._worker_status_map[wid] != \
                                WorkerStatus.ACTIVE:
                            result = self._worker_instance.worker_set_status(
                                wid, WorkerStatus.ACTIVE)
                            if result != ContractResponse.SUCCESS:
                                logging.error("Error while setting worker "
                                              "status {} in blockchain"
                                              .format(wida))
                            else:
                                logging.info("Marked worker " + wid +
                                             " as active "
                                             "in blockchain")
                                self._worker_status_map[wid] = \
                                    WorkerStatus.ACTIVE
            else:
                logging.info("Adding new worker {} to blockchain"
                             .format(wid))
                result = self._worker_instance.worker_register(
                    wid, worker_type, org_id, [app_type_id], details
                )
                if result != ContractResponse.SUCCESS:
                    logging.error("Error while registering worker "
                                  "{} to blockchain".format(wid))
                else:
                    logging.info(
                        "Registered worker {} to blockchain".format(wid))
                    self._worker_details_map[wid] = details
                    self._worker_status_map[wid] = WorkerStatus.ACTIVE

        for wid in wids_onchain:
            # Mark all stale workers in blockchain as decommissioned
            if wid not in wids_in_kv:
                if wid not in self._worker_status_map:
                    worker_status_onchain, _, _, _, _ = self._worker_instance\
                        .worker_retrieve(wid)
                else:
                    worker_status_onchain = self._worker_status_map[wid]
                # If worker is not already decommissioned, mark it
                # decommissioned as it is no longer available in the kv storage
                if worker_status_onchain != WorkerStatus.DECOMMISSIONED.value:
                    result = self._worker_instance.worker_set_status(
                        wid, WorkerStatus.DECOMMISSIONED)
                    if result != ContractResponse.SUCCESS:
                        logging.error("Error while setting worker status for "
                                      "{} in blockchain".format(wid))
                    else:
                        logging.info("Marked worker " + wid +
                                     " as decommissioned in blockchain")
                        self._worker_status_map[wid] = \
                            WorkerStatus.DECOMMISSIONED

    def lookup_workers_onchain(self):
        """
        Lookup all workers on chain to sync up with kv storage
        """
        # TODO: Remove hardcoding and pass wild characters instead
        count, _, worker_ids = self._worker_instance.worker_lookup(
            WorkerType.TEE_SGX,
            self._config["WorkerConfig"]["OrganizationId"],
            self._config["WorkerConfig"]["ApplicationTypeId"],
        )
        logging.info("Worker lookup response from blockchain: "
                     "count {} worker ids {}\n".format(
                         count, worker_ids))
        # Work lookup returns tuple (worker_count, lookup_tag and list of
        # worker ids)
        if count > 0:
            return worker_ids
        else:
            logging.error("Failed to lookup worker in blockchain")
            return []
