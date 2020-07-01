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

import binascii
import json
import logging
from os import environ
import time
import asyncio
import nest_asyncio

from utility.hex_utils import is_valid_hex_str
from avalon_sdk.connector.blockchains.common.contract_response \
    import ContractResponse
from avalon_sdk.connector.blockchains.fabric.fabric_wrapper \
    import FabricWrapper
from avalon_sdk.connector.interfaces.work_order_proxy \
    import WorkOrderProxy

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class FabricWorkOrderImpl(WorkOrderProxy):
    """
    This class provides work order management APIs which interact with the
    Fabric blockchain. Detail method descriptions are
    available in WorkOrder interface.
    """

    def __init__(self, config):
        """
        Parameters:
        config    Dictionary containing Fabric-specific parameters
        """
        self.__fabric_wrapper = None
        # Chain code name
        self.CHAIN_CODE = 'order'
        self.WORK_ORDER_SUBMITTED_EVENT_NAME = 'workOrderSubmitted'
        self.WORK_ORDER_COMPLETED_EVENT_NAME = 'workOrderCompleted'
        # When chain code call for the first time
        # and if peer is not instantiate the chaincode
        # then it will take some time to instantiate
        self.WORK_ORDER_GET_RESULT_TIMEOUT = 60
        nest_asyncio.apply()
        if config is not None:
            self.__fabric_wrapper = FabricWrapper(config)
        else:
            raise Exception("config is none")

    def work_order_submit(self, work_order_id, worker_id, requester_id,
                          work_order_request, id=None):
        """
        Submit work order request to the Fabric block chain.

        Parameters:
        work_order_id      Unique ID of the work order request
        worker_id          Identifier for the worker
        requester_id       Unique id to identify the requester
        work_order_request JSON RPC string work order request.
                           Complete definition at work_order.py and
                           defined in EEA specification 6.1.1
        id                 Optional JSON RPC request ID

        Returns:
        0 on success and non-zero on error.
        """
        if (self.__fabric_wrapper is not None):
            params = []
            params.append(work_order_id)
            params.append(worker_id)
            params.append(requester_id)
            params.append(work_order_request)
            txn_status = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'workOrderSubmit',
                params)
            return txn_status
        else:
            logging.error("Fabric wrapper instance is not initialized")
            return ContractResponse.ERROR

    def work_order_get_result(self, work_order_id, id=None):
        """
        Query blockchain to get work order result.

        Parameters:
        work_order_id Work Order ID that was sent in the
                      corresponding work_order_submit request
        id            Optional JSON RPC request ID

        Returns:
        Tuple containing work order status, worker id, work order request,
        work order response, and error code.
        None on error.
        """
        wo_resp = None
        # First make a call to contract query API workOrderGet,
        # if it returns result then return it
        # otherwise wait in event loop to get workOrderCompleted
        # event from blockchain.

        def handle_fabric_event(event, block_num, txn_id, status):
            """
            Callback function for Fabric event handler.

            Parameters:
                event      Event payload
                block_num  Block number (unused)
                txn_id     Transaction ID (unused)
                status     Status (unused)
            """
            payload = event['payload'].decode("utf-8")
            resp = json.loads(payload)
            response = json.loads(resp["workOrderResponse"])
            # to use global scope of wo_resp
            nonlocal wo_resp
            # Event has result tag in case work order successful
            if "result" in response and \
                    work_order_id in response["result"].values():
                wo_resp = response
                # Return this flag event listener to stop the
                # event handling
                return True
            # Event has error tag if work order failed
            elif "error" in response and \
                    work_order_id in response["error"]["data"].values():
                wo_resp = response
                return True
            else:
                return False

        if (self.__fabric_wrapper is not None):
            params = []
            params.append(work_order_id)
            txn_status = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'workOrderGet',
                params)
            # workOrderGet returns tuple containing work order
            # result params as defined in EEA spec 6.10.5
            if txn_status and len(txn_status) > 0:
                logging.info(
                    "work order get response {}".format(txn_status[3]))
                return json.loads(txn_status[3])
            else:
                logging.warn("Work order seems to be not yet completed, "
                             "going to listen for workOrderCompleted event")
        # Wait for workOrderCompleted event
        event_handler = \
            self.get_work_order_completed_event_handler(
                handle_fabric_event
            )
        if event_handler:
            try:
                asyncio.get_event_loop().run_until_complete(
                    asyncio.wait_for(
                        event_handler.get_single_event(),
                        timeout=self.WORK_ORDER_GET_RESULT_TIMEOUT
                        )
                )
            except asyncio.TimeoutError:
                logging.error("Work order get result timed out."
                              " Either work order id is invalid or"
                              " Work order execution is not completed yet")
                # stop event handler
                asyncio.get_event_loop().run_until_complete(
                    event_handler.stop_event_handling())
                return None

            return wo_resp
        else:
            logging.error("Failed while creating event handler")
            return None

    def work_order_complete(self, work_order_id, work_order_response):
        """
        This function is called by the Worker Service to
        complete a work order successfully or in error.
        This API is for the proxy model.

        Parameters:
        work_order_id       Unique ID to identify the work order request
        work_order_response Work order response data in a string

        Returns:
        errorCode           0 on success or non-zero on error.
        """
        if (self.__fabric_wrapper is not None):
            if work_order_response is None:
                logging.info("Work order response is empty")
                return ContractResponse.ERROR
            params = []
            params.append(work_order_id)
            params.append(work_order_response)
            txn_status = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'workOrderComplete',
                params)
            return txn_status
        else:
            logging.error(
                "Fabric wrapper instance is not initialized")
            return ContractResponse.ERROR

    def encryption_key_start(self, tag):
        """
        Initiate setting the encryption key of the worker.
        Not supported for Fabric.
        """
        logging.error("This API is not supported")
        return None

    def encryption_key_get(self, worker_id, requester_id,
                           last_used_key_nonce=None, tag=None,
                           signature_nonce=None,
                           signature=None):
        """
        Get worker's key from Fabric blockchain.
        Not supported for Fabric.
        """
        logging.error("This API is not supported")
        return None

    def encryption_key_set(self, worker_id, encryption_key,
                           encryption_nonce, tag, signature):
        """
        Set worker's encryption key.
        Not supported for Fabric.
        """
        logging.error("This API is not supported")
        return None

    def get_work_order_submitted_event_handler(self, handler_func):
        """
        Start event handler loop for a workOrderSubmitted event.

        Parameters:
        handler_func  Callback function name as a string

        Returns:
        Event handler object.
        """
        if (self.__fabric_wrapper is not None):
            event_handler = self.__fabric_wrapper.get_event_handler(
                self.WORK_ORDER_SUBMITTED_EVENT_NAME,
                self.CHAIN_CODE,
                handler_func
            )
            return event_handler
        else:
            logging.error(
                "Fabric wrapper instance is not initialized")
            return None

    def get_work_order_completed_event_handler(self, handler_func):
        """
        Start event handler loop for a workOrderCompleted event.

        Parameters:
        handler_func Callback function name as a string
        """
        if (self.__fabric_wrapper is not None):
            event_handler = self.__fabric_wrapper.get_event_handler(
                self.WORK_ORDER_COMPLETED_EVENT_NAME,
                self.CHAIN_CODE,
                handler_func
            )
            return event_handler
        else:
            logging.error(
                "Fabric wrapper instance is not initialized")
            return None
