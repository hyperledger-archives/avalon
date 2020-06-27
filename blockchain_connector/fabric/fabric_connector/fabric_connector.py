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
from os import path, environ
import errno
import asyncio
import logging
import json
import random
import nest_asyncio

from connector_common.base_connector import BaseConnector

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class FabricConnector(BaseConnector):
    """
    Fabric blockchain connector
    """

    def __init__(self, config, fabric_registry_instance,
                 fabric_worker_instance,
                 fabric_work_order_instance,
                 fabric_wo_receipt_instance):
        """
        initialize connector
        @param config - dict containing config params
        @param fabric_registry_instance - object of
        FabricWorkerRegistryListImpl
        @param fabric_worker_instance - object of FabricWorkerRegistryImpl
        @param fabric_work_order_instance - object of FabricWorkOrderProxyImpl
        @param fabric_wo_receipt_instance - object of Fabric implementation for
        work order receipt
        """
        super(FabricConnector, self).__init__(
            config,
            fabric_registry_instance,
            fabric_worker_instance,
            fabric_work_order_instance,
            fabric_wo_receipt_instance
        )
        self._fabric_work_order = fabric_work_order_instance

    def start_wo_submitted_event_listener(self, handler_func):
        """
        Start event listener is blockchain specific
        and it is implemented using blockchain provided sdk
        @param handler_func is event handler function
        """
        def workorder_event_handler_func(event, block_num, txn_id, status):
            payload_string = event['payload'].decode("utf-8")
            work_order_req = json.loads(payload_string)
            work_order_id = work_order_req['workOrderId']
            worker_id = work_order_req["workerId"]
            requester_id = work_order_req["requesterId"]
            work_order_params = work_order_req["workOrderRequest"]
            logging.info("Received event from fabric blockchain")
            handler_func(work_order_id, worker_id,
                         requester_id,
                         work_order_params)

        logging.info("Creating work order submit event handler")
        event_handler = self._fabric_work_order.\
            get_work_order_submitted_event_handler(
                workorder_event_handler_func
            )
        if event_handler is None:
            logging.info("Failed to create fabric event handler")
            return
        else:
            try:
                asyncio.get_event_loop().run_until_complete(
                    event_handler.start_event_handling()
                )
            except KeyboardInterrupt:
                asyncio.get_event_loop().run_until_complete(
                    event_handler.stop_event_handling()
                )
