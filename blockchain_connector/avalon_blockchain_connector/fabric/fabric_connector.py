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
import nest_asyncio


from utility.hex_utils import byte_array_to_hex_str
from avalon_sdk.fabric import base
from avalon_sdk.fabric import event_listener
from avalon_sdk.worker.worker_details import WorkerType
from error_code.error_status import WorkOrderStatus
from avalon_sdk.direct.jrpc.jrpc_worker_registry import JRPCWorkerRegistryImpl
from avalon_sdk.direct.jrpc.jrpc_work_order import JRPCWorkOrderImpl
from avalon_sdk.fabric.fabric_worker_registry import FabricWorkerRegistryImpl
from avalon_sdk.fabric.fabric_work_order import FabricWorkOrderImpl

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
        worker_type = WorkerType.TEE_SGX
        req_id = 15
        lookup_result = self.__jrpc_worker.worker_lookup(
            worker_type=worker_type, id=req_id)
        logging.info("worker lookup result {}".format(
            lookup_result
        ))
        if lookup_result and 'result' in lookup_result:
            # Since currently we have only worker, get the first worker
            if lookup_result['result']['totalCount'] > 0:
                worker_id = lookup_result['result']['ids'][0]
                worker_result = self.__jrpc_worker.worker_retrieve(
                    worker_id, req_id+1)
                logging.info("worker retrieve result {}".format(
                    worker_result
                ))
                if worker_result and 'result' in worker_result:
                    worker = worker_result['result']
                    # add worker to fabric block chain
                    status = self.__fabric_worker.worker_register(
                        worker_id,
                        WorkerType(int(worker['workerType'])),
                        worker['organizationId'],
                        [worker['applicationTypeId']],
                        json.dumps(worker['details'])
                    )
                    if status == 0:
                        logging.info(
                            "Added worker to fabric blockchain")
                    else:
                        logging.info(
                            "Failed to add worker to fabric \
                                blockchain")
                else:
                    logging.info("Failed to retrieve worker")
            else:
                logging.info("No workers are available!")
        else:
            logging.info("Failed to lookup workers")

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
        logging.info("work order request {}\n {}".format(
            payload_string, type(payload_string)
        ))
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
            work_order_result = self.__jrpc_work_order.work_order_get_result(
                work_order_req['workOrderId'],
                jrpc_req_id
            )
            logging.info("Work order get result {}".format(
                work_order_result
            ))
            if work_order_result and 'result' in work_order_result:
                logging.info("Commit work order result to blockchain")
                # call to chain code to store result to blockchain
                status = self.__fabric_work_order.work_order_complete(
                    work_order_id,
                    json.dumps(work_order_result['result'])
                )
                if status == 0:
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
