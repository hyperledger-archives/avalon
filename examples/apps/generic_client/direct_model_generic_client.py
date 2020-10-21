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
import random

from avalon_sdk.worker.worker_details import WorkerType, WorkerStatus, \
    SGXWorkerDetails
from avalon_sdk.connector.blockchains.ethereum.ethereum_worker_registry_list \
    import EthereumWorkerRegistryListImpl
from avalon_sdk.connector.direct.jrpc.jrpc_worker_registry import \
    JRPCWorkerRegistryImpl
from avalon_sdk.connector.direct.jrpc.jrpc_work_order import \
    JRPCWorkOrderImpl
from avalon_sdk.connector.direct.jrpc.jrpc_work_order_receipt \
    import JRPCWorkOrderReceiptImpl
from error_code.error_status import WorkOrderStatus, ReceiptCreateStatus
import avalon_crypto_utils.worker_signing as worker_signing
from error_code.error_status import SignatureStatus
from avalon_sdk.work_order_receipt.work_order_receipt \
    import WorkOrderReceiptRequest
from base_generic_client import BaseGenericClient

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class DirectModelGenericClient(BaseGenericClient):
    """
    Generic client class to test end to end flow
    for direct model.
    """

    def __init__(self, config):
        super().__init__()
        self._config = config
        self._worker_registry_list = None
        self._worker_instance = JRPCWorkerRegistryImpl(self._config)
        self._work_order_instance = JRPCWorkOrderImpl(self._config)
        self._work_order_receipt = JRPCWorkOrderReceiptImpl(self._config)

    def _get_random_jrpc_id(self):
        return random.randint(1, 10000)

    def retrieve_uri_from_registry_list(self, config):
        # Retrieve Http JSON RPC listener uri from registry
        # in case of direct model
        logging.info("\n Retrieve Http JSON RPC listener uri from registry \n")
        # Get block chain type
        blockchain_type = config['blockchain']['type']
        if blockchain_type == "Ethereum":
            self._worker_registry_list = EthereumWorkerRegistryListImpl(
                config)
        else:
            logging.error("\n Worker registry list is currently "
                          "supported only for "
                          "ethereum block chain \n")
            return None

        # Lookup returns tuple, first element is number of registries and
        # second is element is lookup tag and
        # third is list of organization ids.
        registry_count, lookup_tag, registry_list = \
            self._worker_registry_list.registry_lookup()
        logging.info("\n Registry lookup response: registry count: {} "
                     "lookup tag: {} registry list: {}\n".format(
                         registry_count, lookup_tag, registry_list))
        if (registry_count == 0):
            logging.error("No registries found")
            return None
        # Retrieve the fist registry details.
        registry_retrieve_result = \
            self._worker_registry_list.registry_retrieve(
                registry_list[0])
        logging.info("\n Registry retrieve response: {}\n".format(
            registry_retrieve_result
        ))

        return registry_retrieve_result[0]

    def get_worker_details(self, worker_id):
        """
        Fetch worker details for given worker id
        """
        worker_retrieve_res = self._worker_instance.worker_retrieve(
            worker_id,
            self._get_random_jrpc_id()
        )
        if worker_retrieve_res and "result" in worker_retrieve_res:
            status = worker_retrieve_res["result"]["status"]
            details = worker_retrieve_res["result"]["details"]
            logging.info("\n Worker retrieve: worker status {} "
                         "details : {}\n".format(
                             status, json.dumps(details, indent=4)
                         ))
            if status == WorkerStatus.ACTIVE.value:
                # Initializing Worker Object
                worker_obj = SGXWorkerDetails()
                worker_obj.load_worker(
                    details)
                return worker_obj
            else:
                logging.error("Worker is not active")
        else:
            return None

    def get_work_order_result(self, work_order_id):
        """
        Retrieve work order result for given work order id
        """
        work_order_res = self._work_order_instance.work_order_get_result(
            work_order_id,
            self._get_random_jrpc_id()
        )
        logging.info("Work order get result {}".format(
            json.dumps(work_order_res, indent=4)))

        if work_order_res and "result" in work_order_res:
            return True, work_order_res
        return False, work_order_res

    def submit_work_order(self, wo_params):
        """
        Submit work order request
        """
        jrpc_id = self._get_random_jrpc_id()
        wo_request = wo_params.to_string()
        logging.info("\n Work order sumbit request {}\n".format(
            wo_params.to_jrpc_string(jrpc_id)))
        wo_submit_res = self._work_order_instance.work_order_submit(
            wo_params.get_work_order_id(),
            wo_params.get_worker_id(),
            wo_params.get_requester_id(),
            wo_request,
            jrpc_id
        )

        logging.info("Work order submit response : {}\n ".format(
            json.dumps(wo_submit_res, indent=4)
        ))
        if wo_submit_res:
            # in asynchronous mode
            if "error" in wo_submit_res:
                if wo_submit_res["error"]["code"] == WorkOrderStatus.PENDING:
                    return True, wo_submit_res
            # in synchronous mode
            elif "result" in wo_submit_res:
                return True, wo_submit_res
            else:
                return False, wo_submit_res
        else:
            return False, wo_submit_res

    def create_work_order_receipt(self, wo_params,
                                  client_private_key):
        # Create a work order receipt object using
        # WorkOrderReceiptRequest class.
        # This function will send a WorkOrderReceiptCreate
        # JSON RPC request.
        wo_request = json.loads(wo_params.to_jrpc_string(
            self._get_random_jrpc_id()))
        wo_receipt_request_obj = WorkOrderReceiptRequest()
        wo_create_receipt = wo_receipt_request_obj.create_receipt(
            wo_request,
            ReceiptCreateStatus.PENDING.value,
            client_private_key
        )
        logging.info("Work order create receipt request : {} \n \n ".format(
            json.dumps(wo_create_receipt, indent=4)
        ))
        # Submit work order create receipt jrpc request
        wo_receipt_resp = self._work_order_receipt.work_order_receipt_create(
            wo_create_receipt["workOrderId"],
            wo_create_receipt["workerServiceId"],
            wo_create_receipt["workerId"],
            wo_create_receipt["requesterId"],
            wo_create_receipt["receiptCreateStatus"],
            wo_create_receipt["workOrderRequestHash"],
            wo_create_receipt["requesterGeneratedNonce"],
            wo_create_receipt["requesterSignature"],
            wo_create_receipt["signatureRules"],
            wo_create_receipt["receiptVerificationKey"],
            self._get_random_jrpc_id()
        )
        logging.info("Work order create receipt response : {} \n \n ".format(
            wo_receipt_resp
        ))

    def retrieve_work_order_receipt(self, wo_id):
        """
        Retrieve work order receipt for given work order id
        """
        receipt_res = self._work_order_receipt.work_order_receipt_retrieve(
            wo_id,
            id=self._get_random_jrpc_id()
        )
        logging.info("\n Retrieve receipt response:\n {}".format(
            json.dumps(receipt_res, indent=4)
        ))
        # Retrieve last update to receipt by passing 0xFFFFFFFF
        receipt_update_retrieve = \
            self._work_order_receipt.work_order_receipt_update_retrieve(
                wo_id,
                None,
                1 << 32,
                id=self._get_random_jrpc_id())
        logging.info("\n Last update to receipt receipt is:\n {}".format(
            json.dumps(receipt_update_retrieve, indent=4)
        ))

        return receipt_update_retrieve

    def verify_receipt_signature(self, receipt_update_retrieve):
        """
        Verify work order receipt signature
        """
        signer = worker_signing.WorkerSign()
        status = signer.verify_update_receipt_signature(
            receipt_update_retrieve['result'])
        if status == SignatureStatus.PASSED:
            logging.info(
                "Work order receipt retrieve signature verification " +
                "successful")
        else:
            logging.error(
                "Work order receipt retrieve signature verification failed!!")
            return False

        return True
