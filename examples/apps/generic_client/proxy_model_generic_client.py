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
import logging

from avalon_sdk.worker.worker_details import WorkerType, WorkerStatus,\
    SGXWorkerDetails
from avalon_sdk.connector.blockchains.fabric.fabric_worker_registry \
    import FabricWorkerRegistryImpl
from avalon_sdk.connector.blockchains.fabric.fabric_work_order \
    import FabricWorkOrderImpl
from avalon_sdk.connector.blockchains.ethereum.ethereum_worker_registry \
    import EthereumWorkerRegistryImpl
from avalon_sdk.connector.blockchains.ethereum.ethereum_work_order \
    import EthereumWorkOrderProxyImpl
from avalon_sdk.connector.blockchains.common.contract_response \
    import ContractResponse
from base_generic_client import BaseGenericClient

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class ProxyModelGenericClient(BaseGenericClient):
    """
    Generic client class to test end to end test
    for direct and proxy model.
    """

    def __init__(self, config, blockchain_type):
        super().__init__()
        self._config = config
        if blockchain_type.lower() == 'fabric':
            self._worker_instance = FabricWorkerRegistryImpl(self._config)
            self._work_order_instance = FabricWorkOrderImpl(self._config)
        elif blockchain_type.lower() == 'ethereum':
            self._worker_instance = EthereumWorkerRegistryImpl(self._config)
            self._work_order_instance = EthereumWorkOrderProxyImpl(
                self._config)
        else:
            logging.error("Invalid blockchain type")

    def get_worker_details(self, worker_id):
        """
        Fetch worker details for given worker id
        """
        status, _, _, _, details = self._worker_instance.worker_retrieve(
            worker_id
        )
        logging.info("\n Worker retrieve result: Worker status {}"
                     " details : {}\n".format(
                         status, json.dumps(details, indent=4)
                     ))
        if status == WorkerStatus.ACTIVE.value:
            # Initializing Worker Object
            worker_obj = SGXWorkerDetails()
            worker_obj.load_worker(
                json.loads(details))
            return worker_obj
        else:
            logging.error("Worker is not active")
            return None

    def submit_work_order(self, wo_params):
        """
        Submit work order request
        """
        wo_submit_res = self._work_order_instance.work_order_submit(
            wo_params.get_work_order_id(),
            wo_params.get_worker_id(),
            wo_params.get_requester_id(),
            wo_params.to_string()
        )
        return wo_submit_res == ContractResponse.SUCCESS, wo_submit_res

    def get_work_order_result(self, work_order_id):
        """
        Retrieve work order result for given work order id
        """
        wo_get_result = self._work_order_instance.work_order_get_result(
            work_order_id
        )
        logging.info("Work order result {}".format(wo_get_result))
        if wo_get_result and "result" in wo_get_result:
            return True, wo_get_result
        return False, wo_get_result

    def create_work_order_receipt(self, wo_params,
                                  client_private_key):
        # TODO Need to be implemented
        pass

    def retrieve_work_order_receipt(self, wo_id):
        # TODO Need to be implemented
        pass

    def verify_receipt_signature(self, receipt_update_retrieve):
        # TODO Need to be implemented
        pass
