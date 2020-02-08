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
import logging
import json
from os import environ

from utility.hex_utils import is_valid_hex_str

from avalon_sdk.worker.worker_details import WorkerStatus, WorkerType
from avalon_sdk.ethereum.ethereum_wrapper import EthereumWrapper
from avalon_sdk.interfaces.work_order_proxy \
    import WorkOrderClient

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Return codes
SUCCESS = 0
ERROR = 1


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
        if config["ethereum"]["proxy_work_order_contract_file"] is None:
            logging.error("Missing work order contract file path!!")
            return False
        if config["ethereum"]["proxy_work_order_contract_address"] is None:
            logging.error("Missing work order contract address!!")
            return False
        return True

    def __initialize(self, config):
        """
        Initialize the parameters from config to instance variables.
        """
        self.__eth_client = EthereumWrapper(config)
        tcf_home = environ.get("TCF_HOME", "../../../")
        contract_file_name = tcf_home + "/" + \
            config["ethereum"]["proxy_work_order_contract_file"]
        contract_address = \
            config["ethereum"]["proxy_work_order_contract_address"]
        self.__contract_instance = self.__eth_client.get_contract_instance(
            contract_file_name, contract_address
        )

    def _is_valid_work_order_json(self, work_order_id, worker_id, requester_id,
                                  work_order_request):
        """
        Validate following fields in JSON request against the ones
        provided outside the JSON - workOrderId, workerId, requesterId
        """
        json_request = json.load(work_order_request)
        if (work_order_id == json_request.get("workOrderId")
                and worker_id == json_request.get("workerId")
                and requester_id == json_request.get("requesterId")):
            return True
        else:
            return False

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
            if not is_valid_hex_str(
                    binascii.hexlify(work_order_id).decode("utf8")):
                logging.error("Invalid work order id {}".format(work_order_id))
                return ERROR

            if not is_valid_hex_str(
                    binascii.hexlify(worker_id).decode("utf8")):
                logging.error("Invalid worker id {}".format(worker_id))
                return ERROR

            if not is_valid_hex_str(
                    binascii.hexlify(requester_id).decode("utf8")):
                logging.error("Invalid requester id {}".format(requester_id))
                return ERROR

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
            except Execption as e:
                logging.error(
                    "execption occured when trying to execute workOrderSubmit \
                     transaction on chain"+str(e))
                return ERROR
        else:
            logging.error(
                "work order contract instance is not initialized")
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
            if not is_valid_hex_str(
                    binascii.hexlify(work_order_id).decode("utf8")):
                logging.error("Invalid work order id {}".format(work_order_id))
                return ERROR
            txn_dict = self.__contract_instance.functions.workOrderComplete(
                work_order_id, work_order_response).buildTransaction(
                    self.__eth_client.get_transaction_params()
            )
            try:
                txn_receipt = self.__eth_client.execute_transaction(txn_dict)
                return SUCCESS
            except Execption as e:
                logging.error(
                    "execption occured when trying to execute \
                     workOrderComplete transaction on chain"+str(e))
                return ERROR
        else:
            logging.error(
                "work order contract instance is not initialized")
            return ERROR

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
