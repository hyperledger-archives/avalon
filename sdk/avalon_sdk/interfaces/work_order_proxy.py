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
from sdk.avalon_sdk.interfaces.work_order import WorkOrder


class WorkOrderProxy(ABC, WorkOrder):
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
        Function to inform the Worker that it should start
        encryption key generation for this requester.
        This API is for proxy model.
        Params
            tag is an optional parameter.
            If it is zero, the transaction sender's address
            is used as a tag.
        Returns
            An error code, 0 - success, otherwise an error.
        """
        pass

    @abstractmethod
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
        pass
