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
from avalon_sdk.connector.interfaces.work_order import WorkOrder


class WorkOrderProxy(WorkOrder):
    """
    This class is an abstract base class that contains
    abstract APIs to manage work orders.
    This interface is going to be used by proxy model.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def encryption_key_start(self, tag, id=None):
        """
        Inform the Worker that it should start
        encryption key generation for this requester.
        This API is for the proxy model.

        Parameters:
        tag       is an optional parameter.
                  If it is zero, the transaction sender's address
                  is used as a tag
        id        Optional JSON RPC request ID

        Returns:
        0 on success, otherwise an error code.
        """
        pass

    @abstractmethod
    def work_order_complete(self, work_order_id, work_order_response):
        """
        This function is called by the Worker Service to
        complete a Work Order successfully or in error.
        This API is for the proxy model.

        Parameters:
        work_order_id       Unique ID to identify the work order request
        work_order_response Work order response data in a string

        Returns:
        errorCode           0 on success or non-zero on error.
        """
        pass
