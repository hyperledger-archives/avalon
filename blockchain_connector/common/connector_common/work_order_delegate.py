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
import asyncio
import logging
from error_code.error_status import WorkOrderStatus
from avalon_sdk.connector.blockchains.common.contract_response \
    import ContractResponse

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class WorkOrderDelegate():

    """
    Helper class to sync work orders between avalon and blockchain
    """

    def __init__(self, jrpc_work_order, work_order_instance):
        """
        Initialize the connector with instances of jrpc worker
        implementation and blockchain worker implementation objects.
        @param jrpc_work_order - JRPC implementation class object of work order
        @param work_order_instance - work order blockchain implementation
        class object
        """
        self._work_order_proxy = work_order_instance
        self._jrpc_work_order_instance = jrpc_work_order

    def submit_work_order_and_get_result(self, work_order_id, worker_id,
                                         requester_id, work_order_params):
        """
        This function submits work order using work_order_submit direct API
        """
        logging.info("About to submit work order to listener")
        response = self._jrpc_work_order_instance\
            .work_order_submit(work_order_id, worker_id, requester_id,
                               work_order_params, id=random.randint(0, 100000))
        logging.info("Work order submit response : {}".format(
            json.dumps(response, indent=4)))
        if response and 'error' in response and \
                response['error']['code'] == \
                WorkOrderStatus.PENDING.value:
            # get the work order result
            work_order_result = self._jrpc_work_order_instance\
                .work_order_get_result(work_order_id,
                                       id=random.randint(0, 100000))
            logging.info("Work order get result : {} "
                         .format(json.dumps(work_order_result, indent=4)))
            return work_order_result
        # In Synchronous work order processing response would
        # contain result
        elif response and ('result' in response or
                           'error' in response):
            return response
        else:
            return None

    def add_work_order_result_to_chain(self, work_order_id, response):
        """
        This function adds a work order result to the blockchain
        """
        result = self._work_order_proxy.work_order_complete(
            work_order_id, json.dumps(response))
        if result == ContractResponse.SUCCESS:
            logging.info("Successfully added work order result to blockchain")
        else:
            logging.error("Error adding work order result to blockchain")
        return result
