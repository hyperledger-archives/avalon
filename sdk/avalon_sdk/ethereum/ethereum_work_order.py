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
import asyncio
import logging
from os import environ

from utility.hex_utils import is_valid_hex_str

from avalon_sdk.worker.worker_details import WorkerStatus, WorkerType
from avalon_sdk.ethereum.ethereum_wrapper import EthereumWrapper
from avalon_sdk.ethereum.ethereum_listener \
    import BlockchainInterface, EventProcessor
from avalon_sdk.interfaces.work_order_proxy \
    import WorkOrderProxy

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Return codes
SUCCESS = 0
ERROR = 1

# Event Listener sleep duration
LISTENER_SLEEP_DURATION = 5


class EthereumWorkOrderProxyImpl(WorkOrderProxy):

    """
    This class is meant to write work-order related data to Ethereum
    blockchain. Detailed method description is available in the interface
    """

    def __init__(self, config):
        if self.__validate(config) is True:
            self.__initialize(config)
        else:
            raise Exception("Invalid configuration parameter")

    def __validate(self, config):
        """
        Validates config parameters for existence.
        Returns false if validation fails and true if it succeeds
        """
        try:
            if config["ethereum"]["work_order_contract_file"] is None:
                logging.error("Missing work order contract file path!!")
                return False
            if config["ethereum"]["work_order_contract_address"] is None:
                logging.error("Missing work order contract address!!")
                return False
            if config["ethereum"]["provider"] is None:
                logging.error("Missing Ethereum provider url!!")
                return False
        except KeyError as ex:
            logging.error("Required configs not present".format(ex))
            return False
        return True

    def __initialize(self, config):
        """
        Initialize the parameters from config to instance variables.
        """
        self.__eth_client = EthereumWrapper(config)
        self._config = config
        tcf_home = environ.get("TCF_HOME", "../../../")
        contract_file_name = tcf_home + "/" + \
            config["ethereum"]["work_order_contract_file"]
        contract_address = \
            config["ethereum"]["work_order_contract_address"]
        self.__contract_instance, self.__contract_instance_evt =\
            self.__eth_client.get_contract_instance(
                contract_file_name, contract_address
            )

    def work_order_submit(self, work_order_id, worker_id, requester_id,
                          work_order_request, id=None):
        """
        Submit work order request
        work_order_id is a unique id to identify the work order request
        worker_id is the identifier for the worker
        requester_id is a unique id to identify the requester
        work_order_request is a json string(Complete definition at
        work_order.py interface file)
        Returns
            An error code, 0 - success, otherwise an error.
        """
        if (self.__contract_instance is not None):

            if not _is_valid_work_order_json(work_order_id, worker_id,
                                             requester_id, work_order_request):
                logging.error("Invalid request string {}"
                              .format(work_order_request))
                return ERROR

            txn_dict = self.__contract_instance.functions.workOrderSubmit(
                work_order_id, worker_id, requester_id, work_order_request
            ).buildTransaction(
                self.__eth_client.get_transaction_params()
            )
            try:
                txn_receipt = self.__eth_client.execute_transaction(txn_dict)
                return SUCCESS
            except Exception as e:
                logging.error(
                    "Exception occured when trying to execute workOrderSubmit "
                    + "transaction on chain"+str(e))
                return ERROR
        else:
            logging.error(
                "Work order contract instance is not initialized")
            return ERROR

    def work_order_complete(self, work_order_id, work_order_response):
        """
        This function is called by the Worker Service to
        complete a Work Order successfully or in error.
        This API is for proxy model.
        params
            work_order_id is unique id to identify the work order request
            work_order_response is the Work Order response data in string
        Returns
            An error code, 0 - success, otherwise an error.
        """
        if (self.__contract_instance is not None):

            txn_dict = self.__contract_instance.functions.workOrderComplete(
                work_order_id, work_order_response).buildTransaction(
                    self.__eth_client.get_transaction_params()
            )
            try:
                txn_receipt = self.__eth_client.execute_transaction(txn_dict)
                return SUCCESS
            except Exception as e:
                logging.error(
                    "Execption occured when trying to execute "
                    + "workOrderComplete transaction on chain"+str(e))
                return ERROR
        else:
            logging.error(
                "Work order contract instance is not initialized")
            return ERROR

    def work_order_get_result(self, work_order_id, id=None):
        """
        Get worker order result.
        This function starts an event handler for handling workOrderCompleted
        event from Ethereum blockchain.
        Returns the reresponse of work order processing.
        """
        logging.info("About to start Ethereum event handler")

        # Start an event listener that listens for events from the proxy
        # blockchain, extracts response payload from there and passes it
        # on to the requestor

        w3 = BlockchainInterface(self._config)

        contract = self.__contract_instance_evt
        # Listening only for workOrderCompleted event now
        listener = w3.newListener(contract, "workOrderCompleted")

        try:
            daemon = EventProcessor(self._config)
            # Wait for the workOrderCompleted event after starting the
            # listener and handler
            event = asyncio.get_event_loop()\
                .run_until_complete(daemon.get_event_synchronously(listener))

            # Get the first element as this is a list of one event
            # obtained from gather() in ethereum_listener
            work_order_response = event[0]["args"]["workOrderResponse"]
            return json.loads(work_order_response)
        except KeyboardInterrupt:
            asyncio.get_event_loop().run_until_complete(daemon.stop())

    def encryption_key_retrieve(self, worker_id, last_used_key_nonce, tag,
                                requester_id, signature_nonce=None,
                                signature=None, id=None):
        """
        Get Encryption Key Request Payload
        """
        pass

    def encryption_key_start(self, tag, id=None):
        """
        Function to inform the Worker that it should start
        encryption key generation for this requester.
        """
        pass

    def encryption_key_set(self, worker_id, encryption_key,
                           encryption_nonce, tag, signature, id=None):
        """
        Set Encryption Key Request Payload
        """
        pass

    def encryption_key_get(self, worker_id, requester_id,
                           last_used_key_nonce=None, tag=None,
                           signature_nonce=None,
                           signature=None, id=None):
        """
        Get Encryption Key Request Payload
        """
        pass


def _is_valid_work_order_json(work_order_id, worker_id, requester_id,
                              work_order_request):
    """
    Validate following fields in JSON request against the ones
    provided outside the JSON - workOrderId, workerId, requesterId
    """
    json_request = json.loads(work_order_request)
    if (work_order_id == json_request.get("workOrderId")
            and worker_id == json_request.get("workerId")
            and requester_id == json_request.get("requesterId")):
        return True
    else:
        return False
