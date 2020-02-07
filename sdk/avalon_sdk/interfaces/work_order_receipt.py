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

from abc import ABC, abstractmethod


class WorkOrderReceipt(ABC):
    """
    This class is an abstract base class that contains
    abstract APIs to manage work order receipts.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def work_order_receipt_create(self, work_order_id, worker_id,
                                  worker_service_id,
                                  requester_id,
                                  receipt_create_status,
                                  work_order_request_hash,
                                  id=None):
        """
        Creating a Work Order Receipt
        Inputs:
        work_order_id is an id of the Work Order.
        worker_id is the Worker id that should execute the Work Order.
        worker_service_id is an id of the Worker Service that hosts the Worker.
        requester_id is the id of the requester.
        receipt_create_status is an initial receipt status, it can be
            0 - "pending". The work order is waiting to be processed by the
                worker
            1 - "completed". The worker processed the Work Order and no more
                worker updates are expected
            2 - "processed". The worker processed the Work Order, but
                additional worker updates are expected,
                e.g. oracle notifications
            3 - "failed". The Work Order processing failed,
                e.g. by the worker service because of invalid workerId
            4 - "rejected". The Work Order is rejected by the smart contract,
                e.g. invalid workerServiceId
            values from 5 to 254 are reserved
            value 255 indicates any status
            values above 255 are application specific values
        work_order_request_hash is a hash value of the work order request as
        defined in section
        Submitting a New Work Order.
        id is used for json rpc request
        Outputs:
        errorCode is a result of the function, zero is success,
        otherwise an error.
        """
        pass

    @abstractmethod
    def work_order_receipt_update(self, work_order_id,
                                  updater_id,
                                  update_type,
                                  update_data,
                                  update_signature,
                                  signature_rules, id=None):
        """
        Updating a Work Order Receipt
        This API is implemented by a Work Order Receipts smart contract and it
        can be called by one of the following participants
        -> By or on the behalf of the Worker identified during the receipt
        creation, e.g. to notify about the work order completion
        -> By or on the behalf of other Workers, e.g. to submit an oracle
        notification
        -> By the Work Order Receipt creator (requester)
        -> By other participants, e.g. to acknowledge the Work Order results
        in case of multi-party Work Order processing
        Inputs:
        1. work_order_id is the id of the Work Order.
        2. updater_id is an id of the updating entity. It is optional, if it is
        the same as the transaction sender address.
        3. update_type is a type of the Work Order update that defines how the
        update should be handled.
        If update_type is from 0 to 255, the update sets the receipt status to
        update_type value, refer to Creating a Work Order Receipt in case of
        all other types, the processing is application specific
        4. update_data are update specific data that depend on the
        'workOrderStatus` as follows:
        If the update sets the Work Order Receipt status to completed or
        processed, it is a hash value of the Work Order Response in all other
        cases, update_data are application specific

        5. update_signature is an optional signature of concatenated
        work_order_id, update_type, and update_data. It is required only if the
        updaterId is not the same as the transaction sender address. Hashing
        and signing algorithms are defined by signature_rules.
        6. signature_rules defines hashing and signing algorithms, that are
        separated by forward hash '/', e.g. "SHA-256/RSA-OAEP-4096". It is an
        optional parameter and it is required if signing algorithms are
        different from the algorithms defined for the Worker defined during
        the receipt creation.
        7. id is used for json rpc request
        Outputs:
        error_code is a result of the function, zero is success, otherwise an
        error
        """
        pass

    @abstractmethod
    def work_order_receipt_retrieve(self, work_order_id, id=None):
        """
        Retrieving a Work Order Receipt
        Inputs:
        work_order_id is the id of the Work Order to be retrieved.
        id is used for json rpc request
        Outputs:
        worker_service_id, requester_id, work_order_id, receipt_create_status,
        and work_order_request_hash are defined in work_order_receipt_create().
        currentReceiptStatus matches
            -> the receiptCreateStatus at the time of the receipt creation,
            if there have not been any receipt updates changing its status
            -> the status set by the latest receipt update
        Returns
            tuple containing worker service id, worker id, requester id,
            receipt create status, work order request hash and current
            receipt status.
        """
        pass

    @abstractmethod
    def work_order_receipt_update_retrieve(self, work_order_id,
                                           updater_id,
                                           update_index, id=None):
        """
        Retrieving a Work Order Receipt Update
        Inputs:
        work_order_id is the id of the Work Order to be updated.
        updater_id is the id of the updating entity. If it null, updaterId is
        ignored.
        update_index is an index of the update to retrieve. Value "0xFFFFFFFF"
        is reserved to retrieve the last received update.
        id is used for json rpc request
        Outputs:
        updater_id, update_type, update_data, update_signature, and
        signature_rules are defined
        work_order_receipt_update().
        update_count contains the total number of updates for this receipt,
        if updaterId is null, or the total number of updates made by
        'updater_id'.
        Returns
            tuple containing updater id, update type, update data,
            updater signature, update count.
        """
        pass

    @abstractmethod
    def work_order_receipt_lookup(self, worker_service_id,
                                  worker_id,
                                  requester_id,
                                  receipt_status, id=None):
        """
        Work Order Receipt Lookup
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
        lookup_tag is an optional parameter. If it is returned, it means that
        there are more matching receipts than can be retrieved by calling
        work_order_receipt_lookup_next() and with this tag as an input
        parameter.
        ids is an array of the Work Order receipt ids that match the input
        parameters.
        Returns
            tuple containing matching count, lookup tag and list of work
            order receipt ids.
        """
        pass

    @abstractmethod
    def work_order_receipt_lookup_next(self, worker_service_id,
                                       worker_id,
                                       requester_id,
                                       receipt_status,
                                       last_lookup_tag, id=None):
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
            list of work order ids.
        """
        pass

    @abstractmethod
    def work_order_receipt_update(self, work_order_id,
                                  updater_id,
                                  update_type,
                                  update_data,
                                  update_signature,
                                  signature_rules, id=None):
        """
        Updating a Work Order Receipt
        This API is implemented by a Work Order Receipts smart contract and it
        can be called by one of the following participants
        -> By or on the behalf of the Worker identified during the receipt
        creation, e.g. to notify about the work order completion
        -> By or on the behalf of other Workers, e.g. to submit an oracle
        notification
        -> By the Work Order Receipt creator (requester)
        -> By other participants, e.g. to acknowledge the Work Order results
        in case of multi-party Work Order processing
        Inputs:
        1. work_order_id is the id of the Work Order.
        2. updater_id is an id of the updating entity. It is optional, if it is
        the same as the transaction sender address.
        3. update_type is a type of the Work Order update that defines how the
        update should be handled.
        If update_type is from 0 to 255, the update sets the receipt status to
        update_type value, refer to Creating a Work Order Receipt in case of
        all other types, the processing is application specific
        4. update_data are update specific data that depend on the
        'workOrderStatus` as follows:
        If the update sets the Work Order Receipt status to completed or
        processed, it is a hash value of the Work Order Response in all other
        cases, update_data are application specific

        5. update_signature is an optional signature of concatenated
        work_order_id, update_type, and update_data. It is required only if the
        updaterId is not the same as the transaction sender address. Hashing
        and signing algorithms are defined by signature_rules.
        6. signature_rules defines hashing and signing algorithms, that are
        separated by forward hash '/', e.g. "SHA-256/RSA-OAEP-4096". It is an
        optional parameter and it is required if signing algorithms are
        different from the algorithms defined for the Worker defined during
        the receipt creation.
        7. id is used for json rpc request
        Outputs:
        error_code is a result of the function, zero is success, otherwise an
        error
        """
        pass
