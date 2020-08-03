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


class BlockchainConnectorInterface(ABC):
    """
    Interface for blockchain to sync workers, work order
    and receipts from avalon to blockchain and vice versa
    """

    @abstractmethod
    def sync_registries(self):
        """
        Sync registry entries from avalon to blockchain and
        avalon to blockchain
        """
        pass

    @abstractmethod
    async def sync_workers(self):
        """
        Sync workers from avalon to blockchain and blockchain to
        avalon
        """
        pass

    @abstractmethod
    async def sync_work_orders(self):
        """
        Sync work orders from avalon to blockchain and blockchain to
        avalon
        """
        pass

    @abstractmethod
    def sync_work_order_receipts(self):
        """
        Sync work order receipts from avalon to blockchain and
        blockchain to avalon
        """
        pass

    @abstractmethod
    def start_wo_submitted_event_listener(self, handler_func):
        """
        Start event listeners for workOrderSubmittedEvent
        @param handler_func is call back function to handle event.
        """
        pass

    @abstractmethod
    def start(self):
        """
        Start the connector service
        """
        pass
