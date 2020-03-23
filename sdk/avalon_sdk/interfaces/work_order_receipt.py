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
        Create a work order receipt.

        Parameters:
        work_order_id           ID of the Work Order
        worker_id               Worker id that should execute the Work Order
        worker_service_id       ID of the Worker Service that
                                hosts the Worker
        requester_id            ID of the requester
        receipt_create_status   Initial receipt status defined
                                in EEA spec 7.1.1
        work_order_request_hash Hash value of the work order request as
                                defined in EEA spec 6.7.
        id                      Optional JSON RPC request ID

        Returns:
        0 on success, otherwise an error code.

        receipt_create_status values are:
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
        5 to 254 - are reserved
        255      - indicates any status
        >255     - application-specific values
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
        Update a Work Order Receipt.
        This API is implemented by a work order receipts smart contract and it
        can be called by one of the following participants:
        - By or on the behalf of the Worker identified during the receipt
          creation, e.g. to notify about the work order completion
        - By or on the behalf of other Workers, e.g. to submit an oracle
          notification
        - By the Work Order Receipt creator (requester)
        - By other participants, e.g. to acknowledge the Work Order results
          in case of multi-party Work Order processing

        Parameters::
        work_order_id    Work Order ID that was sent in the
                         corresponding work_order_submit request
        updater_id       ID of the updating entity. It is optional if it
                         is the same as the transaction sender address
        update_type      Type of the Work Order update that defines
                         how the update should be handled.
                         If update_type is from 0 to 255, the update sets
                         the receipt status to update_type value. Refer to
                         Creating a Work Order Receipt. For other values,
                         the processing is application-specific
        update_data      Update-specific data that depends on the
                         updater type defined in EEA spec 7.1.2.
                         If the update sets the Work Order Receipt status
                         to completed or processed, it is a hash value of
                         the Work Order Response. In all other
                         cases, update_data are application-specific
        update_signature Optional signature of concatenated
                         work_order_id, update_type, and update_data.
                         It is required only if the updater_id is not the
                         same as the transaction sender address. Hashing and
                         signing algorithms are defined by signature_rules
        signature_rules  Defines hashing and signing algorithms,
                         that are separated by forward slash '/'.
                         E.g. "SHA-256/RSA-OAEP-4096". Optional parameter
                         but required if signing algorithms are different
                         from the algorithms defined for the Worker defined
                         during receipt creation
        id               Optional JSON RPC request ID

        Returns:
        Zero on success, otherwise an error code.
        """
        pass

    @abstractmethod
    def work_order_receipt_retrieve(self, work_order_id, id=None):
        """
        Retrieve a work order receipt.

        Parameters:
        work_order_id    ID of the Work Order to be retrieved
        id               Optional JSON RPC request ID

        Outputs:
        On success, return worker_service_id, requester_id, work_order_id,
        receipt_create_status, and work_order_request_hash, as defined in
        work_order_receipt_create().

        receipt_create_status matches the status at the time of the
        receipt creation if there has not been any receipt updates
        changing its status. Otherwise it matches the status set by
        the latest receipt update.
        """
        pass

    @abstractmethod
    def work_order_receipt_update_retrieve(self, work_order_id,
                                           updater_id,
                                           update_index, id=None):
        """
        Retrieving an update to a work order receipt.

        Parameters:
        work_order_id Work Order ID that was sent in the
                      corresponding work_order_submit request
        updater_id    ID of the updating entity. Ignored if null
        update_index  Index of the update to retrieve
                      Value "0xFFFFFFFF" is reserved to retrieve the
                      last received update
        id            Optional JSON RPC request ID

        Returns:
        On success, return updater_id, update_type, update_data,
        update_signature, signature_rules as defined
        work_order_receipt_update(), and update_count.

        If updater_id is null, update_count is the total number of
        updates for this receipt, otherwise it is the total number
        of updates made by updater_id.
        """
        pass

    @abstractmethod
    def work_order_receipt_lookup(self, worker_service_id,
                                  worker_id,
                                  requester_id,
                                  receipt_status, id=None):
        """
        Lookup a work order receipt.

        Parameters:
        worker_service_id Worker Service ID whose receipts will be
                          retrieved
        worker_id         Worker Id whose receipts are requested
        requester_id      ID of the entity requesting receipts
        receipt_status    Defines the status of the receipts retrieved
        id                Optional JSON RPC request ID

        Returns:
        On success, return tuple containing matching count, lookup tag,
        and list of work order receipt ids:
        total_count   Total number of receipts matching the lookup
                      criteria. If this number is bigger than the size
                      of the ids array, the caller should use a lookup_tag
                      to call work_order_receipt_lookup_next() to retrieve
                      the remainder of the receipt IDs
        lookup_tag    Optional parameter. If returned, it means that
                      there are more matching receipts. They can be retrieved
                      by calling work_order_receipt_lookup_next() with
                      this tag as input
        ids           Array of the Work Order receipt IDs that match the input

        """
        pass

    @abstractmethod
    def work_order_receipt_lookup_next(self, worker_service_id,
                                       worker_id,
                                       requester_id,
                                       receipt_status,
                                       last_lookup_tag, id=None):
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
                          this tag as an input parameter
        ids               Array of the Work Order receipt IDs that match the
                          input criteria from the corresponding call to
                          work_order_receipt_lookup().
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
        Update a Work Order Receipt.
        This API is implemented by a Work Order Receipts smart contract and
        it can be called by one of the following participants:
        - By or on the behalf of the Worker identified during the receipt
        creation, e.g. to notify about the work order completion
        - By or on the behalf of other Workers, e.g. to submit an oracle
        notification
        - By the Work Order Receipt creator (requester)
        - By other participants, e.g. to acknowledge the Work Order results
        in case of multi-party Work Order processing

        Parameters:
        work_order_id    Work Order ID that was sent in the
                         corresponding work_order_submit request
        updater_id       ID of the updating entity. It is optional if it
                         is the same as the transaction sender address
        update_type      Type of the Work Order update that defines
                         how the update should be handled.
                         If update_type is from 0 to 255, the update sets
                         the receipt status to update_type value. Refer to
                         Creating a Work Order Receipt. For other values,
                         the processing is application-specific
        update_data      Update-specific data that depends on the
                         updater type defined in EEA spec 7.1.2.
                         If the update sets the Work Order Receipt status
                         to completed or processed, it is a hash value of
                         the Work Order Response. In all other
                         cases, update_data are application-specific
        update_signature Optional signature of concatenated
                         work_order_id, update_type, and update_data.
                         It is required only if the updater_id is not the
                         same as the transaction sender address. Hashing and
                         signing algorithms are defined by signature_rules
        signature_rules  Defines hashing and signing algorithms,
                         that are separated by forward slash '/'.
                         E.g. "SHA-256/RSA-OAEP-4096". Optional parameter
                         but required if signing algorithms are different
                         from the algorithms defined for the Worker defined
                         during receipt creation
        id               Optional JSON RPC request ID
        """
        pass
