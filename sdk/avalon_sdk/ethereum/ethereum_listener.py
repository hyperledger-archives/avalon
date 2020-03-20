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

import asyncio
import logging
from utility.hex_utils import is_valid_hex_str
from avalon_sdk.ethereum.ethereum_wrapper import get_keccak_for_text
from avalon_sdk.http_client.http_jrpc_client import HttpJrpcClient

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

LISTENER_SLEEP_DURATION = 5  # second


class BlockchainInterface:
    def __init__(self, config):
        # TODO: store list of contracts?
        self._config = config
        self._uri_client = HttpJrpcClient(config["ethereum"]["event_provider"])

    def newListener(self, contract, event, fromBlock='latest'):
        # Filter to get events from latest block by default
        return contract.events[event].createFilter(fromBlock=fromBlock)


class EventProcessor:
    def __init__(self, config):
        self._config = config
        self._uri_client = HttpJrpcClient(config["ethereum"]["event_provider"])
        self._wo_completed_hash = get_keccak_for_text(
            "workOrderCompleted(bytes32,bytes32,uint256,string,"
            + "uint256,bytes4)")
        self._wo_submitted_hash = get_keccak_for_text(
            "workOrderSubmitted(bytes32,bytes32,bytes32,string,"
            + "uint256,address,bytes4)")

    async def listener(self, event_filter):
        logging.info("Started listener for events from blockchain")
        while True:
            # Check for any new event logs since the last poll
            # on this filter. Though using events, this is not
            # fully asynchronous.
            for event in event_filter.get_new_entries():
                await self.queue.put(event)
                logging.debug("Event pushed into listener Queue")
            await asyncio.sleep(LISTENER_SLEEP_DURATION)

    async def handler(self, callback, *kargs, **kwargs):
        logging.info("Started handler to handle events")
        while True:
            event = await self.queue.get()
            logging.debug("Event popped from listener queue")

            callback(event, *kargs, **kwargs)
            self.queue.task_done()

    async def sync_handler(self, *kargs, **kwargs):
        logging.info("Started synchronous handler to handle an event")
        event = await self.queue.get()
        logging.debug("Event popped from listener queue")

        self.queue.task_done()
        return event

    async def start(self, event_filter, callback, *kargs, **kwargs):
        self.queue = asyncio.Queue()
        loop = asyncio.get_event_loop()
        self.listeners = [loop.create_task(
            self.listener(event_filter)) for _ in range(1)]
        self.handlers = [loop.create_task(self.handler(
            callback, *kargs, **kwargs)) for _ in range(1)]

        await asyncio.gather(*self.listeners)  # infinite loop
        await self.queue.join()  # this code should never run
        await self.stop()  # this code should never run

    async def get_event_synchronously(self, event_filter, *kargs, **kwargs):
        """
        Get a single event synchronously using the event_filter
        provided.
        Returns an event received for the event_filter used.
        """
        self.queue = asyncio.Queue()
        loop = asyncio.get_event_loop()
        self.listeners = [loop.create_task(
            self.listener(event_filter)) for _ in range(1)]
        self.handlers = [loop.create_task(self.sync_handler(*kargs, **kwargs))]

        handler_result = await asyncio.gather(*self.handlers)

        return handler_result

    async def stop(self):
        for process in self.listeners:
            process.cancel()
        for process in self.handlers:
            process.cancel()
        logging.debug("---exit---")
