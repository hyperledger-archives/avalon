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
from os import environ

from utility.hex_utils import is_valid_hex_str
from avalon_sdk.fabric.fabric_wrapper import FabricWrapper
from avalon_sdk.interfaces.work_order \
    import WorkOrderReceipt

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class FabricWorkOrderReceiptImpl(WorkOrderReceipt):
    """
    This class provide work order receipt management APIs
    which interact with Fabric blockchain.
    Detail method description will be available in
    WorkOrderReceipt interface
    """

    def __init__(self, config):
        """
        config is dict containing fabric specific parameters.
        """
        self.__fabric_wrapper = None
        # Chain code name
        self.CHAIN_CODE = 'receipt'
        if config is not None:
            self.__fabric_wrapper = FabricWrapper(config)
        else:
            raise Exception("config is none")

    def work_order_receipt_create(self, work_order_id, worker_id,
                                  worker_service_id,
                                  requester_id, receipt_create_status,
                                  work_order_request_hash):
        """
        Function to create work order receipt in fabric block chain.
        Params
            work_order_id is an id of the Work Order.
            worker_id is the Worker id that should execute the Work Order.
            worker_service_id is an id of the Worker Service that
            hosts the Worker.
            requester_id is the id of the requester.
            receipt_create_status is an initial receipt status defined
            in EEA spec 7.1.1
        Returns
            0 on success and -1 on error.
        """
        if (self.__fabric_wrapper is not None):
            if not is_valid_hex_str(
                    binascii.hexlify(work_order_id).decode("utf8")):
                logging.info("Invalid work order id {}".format(work_order_id))
                return -1
            if not is_valid_hex_str(
                    binascii.hexlify(worker_id).decode("utf8")):
                logging.info("Invalid worker id {}".format(worker_id))
                return -1
            if not is_valid_hex_str(
                    binascii.hexlify(requester_id).decode("utf8")):
                logging.info("Invalid requester id {}".format(requester_id))
                return -1
            if not is_valid_hex_str(
                    binascii.hexlify(worker_service_id).decode("utf8")):
                logging.info("Invalid service id {}".format(worker_service_id))
                return -1
            if work_order_request_hash is None:
                logging.info("work order request hash is None")
                return -1
            params = []
            params.append(work_order_id)
            params.append(worker_id)
            params.append(worker_service_id)
            params.append(requester_id)
            params.append(receipt_create_status)
            params.append(work_order_request_hash)
            txn_status = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'workOrderReceiptCreate',
                params)
            if txn_status is True:
                return 0
            else:
                return -1
        else:
            logging.error("Fabric wrapper instance is not initialized)
            return -1

    def work_order_receipt_update(self, work_order_id,
                                  updater_id, update_type, update_data,
                                  update_signature=None,
                                  signature_rules=None):
        """
        Updating a Work Order Receipt
        Params
            work_order_id is a Work Order id that was
            sent in the corresponding work_order_submit request.
            updater_id is an id of the updating entity. It is optional
            update_type is from 0 to 255, the update sets the receipt
            status to update_type value
            update_data are update specific data that depends on
            updater type defined in EEA spec 7.1.2
            update_signature is an optional signature of
            work_order_id, update_type, and update_data.
            signature_rules defines hashing and signing algorithms,
            that are separated by forward slash '/'
        Returns
        -1 on error, 0 on Success.
        """
        if (self.__fabric_wrapper is not None):
            if not is_valid_hex_str(
                    binascii.hexlify(work_order_id).decode("utf8")):
                logging.info("Invalid work order id {}".format(work_order_id))
                return -1
            if not is_valid_hex_str(
                    binascii.hexlify(updater_id).decode("utf8")):
                logging.info("Invalid updater id {}".format(updater_id))
                return -1
            params = []
            params.append(work_order_id)
            params.append(updater_id)
            params.append(update_type)
            params.append(update_data)
            if update_signature is not None:
                params.append(update_signature)
                params.append(signature_rules)
            receipt_status = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'workOrderReceiptUpdate',
                params)
            if receipt_status is True:
                return 0
            else:
                return -1
        else:
            logging.error(
                "Fabric wrapper instance is not initialized")
            return -1

    def work_order_receipt_retrieve(self, work_order_id):
        """
        Retrieving a Work Order Receipt
        Inputs:
        work_order_id is the id of the Work Order to be retrieved.
        id is used for json rpc request
        Outputs:
        worker_service_id, requester_id, work_order_id, receipt_create_status,
        and work_order_request_hash are defined in work_order_receipt_create().
        -1 on error
        """
        if (self.__fabric_wrapper is not None):
            if not is_valid_hex_str(
                    binascii.hexlify(work_order_id).decode("utf8")):
                logging.info("Invalid work order id {}".format(work_order_id))
                return -1
            params = []
            params.append(work_order_id)
            retrieve_result = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'workOrderReceiptRetrieve',
                params)
            if retrieve_result is not None:
                return retrieve_result
            else:
                return -1
        else:
            logging.error(
                "Fabric wrapper instance is not initialized")
            return -1

    def work_order_receipt_update_retrieve(self, work_order_id,
                                           updater_id, update_index):
        """
        Function to retrieve update to receipt
        Params
            work_order_id is a Work Order id that was
            sent in the corresponding work_order_submit request.
            updater_id is an id of the updating entity. It is optional
            update_index is an index of the update to retrieve.
            Value "0xFFFFFFFF" is reserved to retrieve the last
            received update.
        Returns
            On success return updater_id, update_type,
            update_data, update_signature and
            signature_rules are defined work_order_receipt_update().
            On error returns -1
        """
        if (self.__fabric_wrapper is not None):
            if not is_valid_hex_str(
                    binascii.hexlify(work_order_id).decode("utf8")):
                logging.info("Invalid work order id {}".format(work_order_id))
                return -1
            if not is_valid_hex_str(
                    binascii.hexlify(updater_id).decode("utf8")):
                logging.info("Invalid updater id {}".format(updater_id))
                return -1
            params = []
            params.append(work_order_id)
            params.append(updater_id)
            params.append(update_index)
            receipt_result = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'workOrderReceiptUpdateRetrieve',
                params)
            if receipt_result is not None:
                return receipt_result
            else:
                return -1
        else:
            logging.error(
                "Fabric wrapper instance is not initialized")
            return -1

    def work_order_receipt_lookup(self, worker_service_id,
                                  worker_id, requester_id, receipt_status):
        """
        Function to lookup receipts
        Inputs:
        worker_service_id is a Worker Service id whose receipts will be
        retrieved.
        worker_id is the Worker Id whose receipts are requested.
        requester_id is the id of the entity requesting receipts.
        receipt_status defines the status of the receipts retrieved.
        id is used for json rpc request
        Outputs:
        total_count is the total number of receipts matching the lookup
        criteria. If this number is bigger than the size of the ids array,
        the caller should use a lookup_tag to call
        work_order_receipt_lookup_next() to retrieve the rest of the
        receipt ids.
        ids is an array of the Work Order receipt ids that match the input
        parameters
        On error returns -1
        """
        if (self.__fabric_wrapper is not None):
            if not is_valid_hex_str(
                    binascii.hexlify(worker_id).decode("utf8")):
                logging.info("Invalid worker id {}".format(worker_id))
                return -1
            if not is_valid_hex_str(
                    binascii.hexlify(worker_service_id).decode("utf8")):
                logging.info("Invalid service id {}".format(worker_service_id))
                return -1
            if not is_valid_hex_str(
                    binascii.hexlify(requester_id).decode("utf8")):
                logging.info("Invalid requester id {}".format(requester_id))
                return -1
            params = []
            params.append(worker_service_id)
            params.append(worker_id)
            params.append(requester_id)
            params.append(receipt_status)
            receipt_result = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'workOrderReceiptLookUp',
                params)
            if receipt_result is not None:
                return receipt_result
            else:
                return -1
        else:
            logging.error(
                "Fabric wrapper instance is not initialized")
            return -1

    def work_order_receipt_lookup_next(self, worker_service_id,
                                       worker_id, requester_id,
                                       receipt_status, last_lookup_tag):
        """
        Work Order Receipt Lookup Next
        Inputs:
        worker_service_id, worker_id, and requester_id are input parameters and
        last_lookup_tag is one of the output parameters for function
        work_order_receipt_lookup() defined in section Work Order Receipt
        Lookup.
        id is used for json rpc request
        Outputs:
        1. total_count is the total number of receipts matching the lookup
        criteria.
        2. lookup_tag is an optional parameter. If it is returned, it means
        that there are more matching receipts that can be retrieved by calling
        this function again and with this tag as an input parameter.
        3. ids is an array of the Work Order receipt ids that match the input
        criteria from the corresponding call to work_order_receipt_lookup().
        Returns
            tuple containing total count, look up tag and
            list of work order ids on success
            return -1 on error
        """
        if (self.__fabric_wrapper is not None):
            if not is_valid_hex_str(
                    binascii.hexlify(worker_id).decode("utf8")):
                logging.info("Invalid worker id {}".format(worker_id))
                return -1
            if not is_valid_hex_str(
                    binascii.hexlify(worker_service_id).decode("utf8")):
                logging.info("Invalid service id {}".format(worker_service_id))
                return -1
            if not is_valid_hex_str(
                    binascii.hexlify(requester_id).decode("utf8")):
                logging.info("Invalid requester id {}".format(requester_id))
                return -1
            params = []
            params.append(worker_service_id)
            params.append(worker_id)
            params.append(requester_id)
            params.append(receipt_status)
            params.append(last_lookup_tag)
            receipt_result = self.__fabric_wrapper.invoke_chaincode(
                self.CHAIN_CODE,
                'workOrderReceiptLookUpNext',
                params)
            if receipt_result is not None:
                return receipt_result
            else:
                return -1
        else:
            logging.error(
                "Fabric wrapper instance is not initialized")
            return -1
