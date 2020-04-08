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
from avalon_sdk.connector.blockchains.fabric.fabric_wrapper \
    import FabricWrapper
from avalon_sdk.connector.interfaces.work_order \
    import WorkOrderReceipt

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class FabricWorkOrderReceiptImpl(WorkOrderReceipt):
    """
    This class provides work order receipt management APIs
    which interact with the Fabric blockchain.
    Detailed method descriptions are available in the
    WorkOrderReceipt interface.
    """

    def __init__(self, config):
        """
        Parameters:
        config    Dict containing Fabric-specific parameters.
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
        Create work order receipt in the Fabric block chain.

        Parameters:
        work_order_id           ID of the Work Order
        worker_id               Worker id that should execute the Work Order
        worker_service_id       ID of the Worker Service that
                                hosts the Worker
        requester_id            ID of the requester
        receipt_create_status   Initial receipt status defined
                                in EEA spec 7.1.1
        work_order_request_hash Hash value of the work order request as
                                defined in EEA spec 6.7

        Returns:
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
            logging.error("Fabric wrapper instance is not initialized")
            return -1

    def work_order_receipt_update(self, work_order_id,
                                  updater_id, update_type, update_data,
                                  update_signature=None,
                                  signature_rules=None):
        """
        Update a Work Order Receipt.

        Parameters:
        work_order_id    Work Order ID that was sent in the
                         corresponding work_order_submit request
        updater_id       ID of the updating entity. It is optional if it
                         is the same as the transaction sender address
        update_type      Type of the Work Order update that defines
                         how the update should be handled
        update_data      Update-specific data that depends on the
                         updater type defined in EEA spec 7.1.2
        update_signature Optional signature of concatenated
                         work_order_id, update_type, and update_data
        signature_rules  Defines hashing and signing algorithms,
                         that are separated by forward slash '/'

        Returns:
        0 on success, -1 on error.
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
        Retrieve a Work Order Receipt.

        Parameters:
        work_order_id ID of the Work Order to be retrieved
        id        Optional JSON RPC request ID

        Returns:
        worker_service_id, requester_id, work_order_id, receipt_create_status,
        and work_order_request_hash, as defined in work_order_receipt_create().
        Return -1 on error.
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
        Retrieve an update to a work order receipt.

        Parameters:
        work_order_id Work Order ID that was sent in the
                      corresponding work_order_submit request
        updater_id    ID of the updating entity. Ignored if null
        update_index  Index of the update to retrieve
                      Value "0xFFFFFFFF" is reserved to retrieve the
                      last received update

        Returns:
        On success, return updater_id, update_type, update_data,
        update_signature, signature_rules, as defined in
        work_order_receipt_update(), and update_count.
        On error, return -1.
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
        Lookup a work order receipt.

        Parameters:
        worker_service_id Worker Service ID whose receipts will be
                          retrieved
        worker_id         Worker Id whose receipts are requested
        requester_id      ID of the entity requesting receipts
        receipt_status    Defines the status of the receipts retrieve
        id                Optional JSON RPC request ID

        Returns:
        Tuple containing total count, last_lookup_tag, and
        list of work order IDs, on success:
        total_count     Total number of receipts matching the lookup criteria.
                        If this number is bigger than the size of the ids
                        array, the caller should use a lookup_tag to call
                        work_order_receipt_lookup_next() to retrieve the rest
                        of the receipt IDs.
        last_lookup_tag Optional lookup_tag when the receipts exceed the ids
                        array size
        ids             Array of work order receipt ids that match the input

        On error, returns -1.
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
        Retrieve subsequent work order receipts after calling
        work_order_receipt_lookup().

        Parameters:
        worker_service_id Worker Service ID
        worker_id         Worker ID value derived from the worker's DID
        requester_id      Requester ID
        last_lookup_tag   One of the output parameters for function
                          work_order_receipt_lookup()
        id                Optional JSON RPC request ID

        Returns:
        On success, return a tuple containing total count, look up tag, and
        list of work order IDs:
        total_count       Total number of receipts matching the lookup
                          criteria
        lookup_tag        Optional parameter. If it is returned, it means
                          that there are more matching receipts that can be
                          retrieved by calling this function again and with
                          this tag as an input parameter.
        ids               Array of the Work Order receipt IDs that match the
                          input criteria from the corresponding call to
                          work_order_receipt_lookup().
        Return -1 on error.
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
