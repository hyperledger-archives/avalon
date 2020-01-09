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


class WorkOrderReceiptConnector(ABC):
    """
    This class is an abstract base class that contains
    abstract APIs to manage work order receipts.
    """

    def __init__(self):
        super().__init__()

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
