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

from utility.hex_utils import is_valid_hex_str
from avalon_sdk.contract_response.contract_response import ContractResponse
from avalon_sdk.fabric.fabric_wrapper import FabricWrapper
from avalon_sdk.interfaces.work_order_proxy \
    import WorkOrderProxy

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class FabricWorkOrderImpl(WorkOrderProxy):
    """
    This class provide work order management APIs which interact with
    Fabric blockchain. Detail method description will be
    available in WorkOrder interface
    """

    def __init__(self, config):
        """
        config is dict containing fabric specific parameters.
        """
        self.__fabric_wrapper = None
        # Chain code name
        self.CHAIN_CODE = 'order'
        self.WORK_ORDER_SUBMITTED_EVENT_NAME = 'workOrderSubmitted'
        self.WORK_ORDER_COMPLETED_EVENT_NAME = 'workOrderCompleted'
        self.WAIT_TIME = 30
        self.__wo_resp = ''
        if config is not None:
            self.__fabric_wrapper = FabricWrapper(config)
        else:
            raise Exception("config is none")

    def work_order_submit(self, work_order_id, worker_id, requester_id,
                          work_order_request, id=None):
        """
        Submit work order request to fabric block chain.
        Params
            work_order_id is unique id of the work order request
            worker_id is identifier for the worker
            requester_id is unique id to identify the requester
            work_order_request is json string work order request
            defined in EEA specification 6.1.1.
        Returns
        0 on success and non zero on error.
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
        Function to query blockchain to get work order result.
        Params
            work_order_id is a Work Order id that was
            sent in the corresponding work_order_submit request.
        Returns
        None on error, result on Success.
        """
        # Calling the contract workOrderGet() will result in error
        # work order id doesn't exist. This is because committing will
        # take some time to commit to chain.
        # Instead of calling contract api to get result chosen the
        # event based approach.
        event_handler = \
            self.get_work_order_completed_event_handler(
                self.handle_fabric_event)
        if event_handler:
            tasks = [
                event_handler.start_event_handling(),
                event_handler.stop_event_handling(int(self.WAIT_TIME))
                ]
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                asyncio.wait(tasks,
                return_when=asyncio.ALL_COMPLETED))
            loop.close()
            return self.__wo_resp
        else:
            logging.info("Failed while creating event handler")
            return None

    def work_order_complete(self, work_order_id, work_order_response):
        """
        This function is called by the Worker Service to
        complete a Work Order successfully or in error.
        This API is for proxy model.
        params
            work_order_id is unique id to identify the work order request
            work_order_response is the Work Order response data in string
        Returns
            errorCode is a result of operation.
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
        Function to initiate to set the encryption key of
        worker.
        """
        logging.error("This API is not supported")
        return None

    def encryption_key_get(self, worker_id, requester_id,
                           last_used_key_nonce=None, tag=None,
                           signature_nonce=None,
                           signature=None):
        """
        Function to worker's key from fabric block chain.
        """
        logging.error("This API is not supported")
        return None

    def encryption_key_set(self, worker_id, encryption_key,
                           encryption_nonce, tag, signature):
        """
        Function to set worker's encryption key.
        """
        logging.error("This API is not supported")
        return None

    def get_work_order_submitted_event_handler(self, handler_func):
        """
        Function to start event handler loop for
        workOrderSubmitted event
        params:
            handler_func is call back function name as string
        returns:
            event handler object
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
        Function to start event handler loop for
        workOrderCompleted event
        params:
            handler_func is call back function name as string
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

    def handle_fabric_event(self, event, block_num, txn_id, status):
        """
        callback function for fabric event handler
        """
        payload = event['payload'].decode("utf-8")
        resp = json.loads(payload)
        self.__wo_resp = json.loads(resp["workOrderResponse"])
        logging.debug("Work order response from event : {}".format(
            self.__wo_resp
        ))
