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

import toml
import time
from os import path, environ
import errno
import asyncio
import logging
import json
import random
import nest_asyncio

from utility.hex_utils import byte_array_to_hex_str
from avalon_sdk.fabric import base
from avalon_sdk.fabric import event_listener
from avalon_sdk.worker.worker_details import WorkerType, WorkerStatus
from error_code.error_status import WorkOrderStatus
from avalon_sdk.direct.jrpc.jrpc_worker_registry import JRPCWorkerRegistryImpl
from avalon_sdk.direct.jrpc.jrpc_work_order import JRPCWorkOrderImpl
from avalon_sdk.fabric.fabric_worker_registry import FabricWorkerRegistryImpl
from avalon_sdk.fabric.fabric_work_order import FabricWorkOrderImpl
from avalon_sdk.contract_response.contract_response import ContractResponse

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class FabricConnector():
    """
    Fabric blockchain connector
    """

    def __init__(self, listener_url):
        tcf_home = environ.get("TCF_HOME", "../../../")
        config_file = tcf_home + "/sdk/avalon_sdk/tcf_connector.toml"
        if not path.isfile(config_file):
            raise FileNotFoundError("File not found at path: {0}".format(
                path.realpath(config_file)))
        try:
            with open(config_file) as fd:
                self.__config = toml.load(fd)
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise Exception("Could not open config file: %s", e)
        self.__config['tcf']['json_rpc_uri'] = listener_url
        self.__fabric_worker = FabricWorkerRegistryImpl(self.__config)
        self.__fabric_work_order = FabricWorkOrderImpl(self.__config)
        self.__jrpc_worker = JRPCWorkerRegistryImpl(self.__config)
        self.__jrpc_work_order = JRPCWorkOrderImpl(self.__config)
        # Wait time in sec
        self.WAIT_TIME = 31536000
        nest_asyncio.apply()

    def start(self):
        self.sync_worker()
        loop = asyncio.get_event_loop()
        tasks = self.get_work_order_event_handler_tasks()
        loop.run_until_complete(
            asyncio.wait(tasks,
                         return_when=asyncio.ALL_COMPLETED))
        loop.close()

    def sync_worker(self):
        """
        Check for existing worker and update worker to fabric blockchain
        """
        # Get all TEE Intel SGX based workers ids from the Fabric blockchain
        worker_ids_onchain = self._lookup_workers_onchain()
        # Get all Intel SGX TEE based worker ids from shared kv
        worker_ids_kv = self._lookup_workers_in_kv_storage()
        # If worker id exists in shared kv then update details of
        # worker to with details field.
        # otherwise add worker to blockchain
        # Update all worker which are not in shared kv and
        # present in blockchain to Decommissioned status
        self._add_update_worker_to_chain(worker_ids_onchain, worker_ids_kv)

    def get_work_order_event_handler_tasks(self):
        """
        Sync work order with blockchain
        1. listen to work order submit event
        2. Submit work order request to listener
        3. Wait for a work order result
        4. Update work order result to fabric
        """
        event_handler = self.__fabric_work_order.\
            get_work_order_submitted_event_handler(
                self.workorder_event_handler_func
            )
        if event_handler:
            tasks = [
                event_handler.start_event_handling(),
                event_handler.stop_event_handling(int(self.WAIT_TIME))
            ]
            return tasks
        else:
            logging.info("get work order submitted event handler failed")
            return None

    def workorder_event_handler_func(self, event, block_num, txn_id, status):
        logging.info("Event payload: {}\n Block number: {}\n"
                     "Transaction id: {}\n Status {}".format(
                         event, block_num, txn_id, status
                     ))
        jrpc_req_id = 301
        # Add workorder id to work order list
        payload_string = event['payload'].decode("utf-8")
        work_order_req = json.loads(payload_string)
        work_order_id = work_order_req['workOrderId']
        # Submit the work order to listener
        logging.info("Submitting to work order to listener")
        response = self.__jrpc_work_order.work_order_submit(
            work_order_req['workOrderId'],
            work_order_req['workerId'],
            work_order_req['requesterId'],
            work_order_req["workOrderRequest"],
            id=jrpc_req_id
        )
        logging.info("Work order submit response {}".format(
            response
        ))
        if response and 'error' in response and \
                response['error']['code'] == WorkOrderStatus.PENDING.value:
            # get the work order result
            jrpc_req_id += 1
            work_order_result = \
                self.__jrpc_work_order.work_order_get_result(
                    work_order_req['workOrderId'],
                    jrpc_req_id
                )
            logging.info("Work order get result {}".format(
                work_order_result
            ))
            if work_order_result:
                logging.info("Commit work order result to blockchain")
                # call to chain code to store result to blockchain
                status = self.__fabric_work_order.work_order_complete(
                    work_order_id,
                    json.dumps(work_order_result)
                )
                if status == ContractResponse.SUCCESS:
                    # remove the entry from work order list
                    logging.info(
                        "Chaincode invoke call work_order_complete success"
                    )
                else:
                    logging.info(
                        "Chaincode invoke call work_order_complete failed"
                    )
            else:
                logging.info("work_order_get_result is failed")
        else:
            logging.info("work_order_submit is failed")

    def _lookup_workers_in_kv_storage(self):
        """
        Retrieves the worker ids from shared kv using
        worker_lookup direct API.
        Returns list of worker ids
        """
        jrpc_req_id = random.randint(0, 100000)

        worker_lookup_result = self.__jrpc_worker.worker_lookup(
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

    def _retrieve_worker_details_from_kv_storage(self, worker_id):
        """
        Retrieve worker details from shared kv using
        direct json rpc API
        Returns the worker details in json string format
        """
        jrpc_req_id = random.randint(0, 100000)
        worker_info = self.__jrpc_worker.worker_retrieve(
            worker_id, jrpc_req_id)
        logging.info("Worker retrieve response from kv storage: {}"
                     .format(json.dumps(worker_info, indent=4)))

        if "error" in worker_info:
            logging.error("Unable to retrieve worker details from kv storage")
            return ""
        else:
            return worker_info["result"]

    def _lookup_workers_onchain(self):
        """
        Lookup all workers on chain to sync up with kv storage
        Return list of worker ids
        """
        worker_lookup_result = self.__fabric_worker.worker_lookup(
            worker_type=WorkerType.TEE_SGX
        )
        logging.info("Worker lookup response from blockchain: {}\n".format(
            json.dumps(worker_lookup_result, indent=4)
        ))
        if worker_lookup_result and worker_lookup_result[0] > 0:
            return worker_lookup_result[2]
        else:
            logging.info("No workers found in fabric blockchain")
            return []

    def _add_update_worker_to_chain(self, wids_onchain, wids_kv):
        """
        This function adds/updates a worker in the fabric blockchain
        """
        for wid in wids_kv:
            worker_info = self._retrieve_worker_details_from_kv_storage(
                wid)
            worker_id = wid
            worker_type = WorkerType(worker_info["workerType"])
            org_id = worker_info["organizationId"]
            app_type_id = worker_info["applicationTypeId"]
            details = json.dumps(worker_info["details"])

            result = None
            if wid in wids_onchain:
                logging.info("Updating worker {} on fabric blockchain"
                             .format(wid))
                result = self.__fabric_worker.worker_update(
                    worker_id, details)
            else:
                logging.info("Adding new worker {} to fabric blockchain"
                             .format(wid))
                result = self.__fabric_worker.worker_register(
                    worker_id, worker_type, org_id, [app_type_id], details
                )
            if result != ContractResponse.SUCCESS:
                logging.error("Error while adding/updating worker to fabric"
                              + " blockchain")

        for wid in wids_onchain:
            # Mark all stale workers on blockchain as decommissioned
            if wid not in wids_kv:
                worker = self.__fabric_worker.worker_retrieve(wid)
                # worker_retrieve returns tuple and first element
                # denotes status of worker.
                worker_status_onchain = worker[0]
                # If worker is not already decommissioned,
                # mark it decommissioned
                # as it is no longer available in the kv storage
                if worker_status_onchain != WorkerStatus.DECOMMISSIONED.value:
                    update_status = self.__fabric_worker.worker_set_status(
                        wid, WorkerStatus.DECOMMISSIONED)
                    if update_status == ContractResponse.SUCCESS:
                        logging.info("Marked worker " + wid +
                                     " as decommissioned on" +
                                     " fabric blockchain")
                    else:
                        logging.info("Update worker " + wid + " is failed")
