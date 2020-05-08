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
from avalon_sdk.connector.blockchains.ethereum.ethereum_wrapper \
    import get_keccak_for_text

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

LISTENER_SLEEP_DURATION = 5  # second


class BlockchainInterface:
    """Ethereum blockchain interface to event processor."""

    def __init__(self, config):
        # TODO: store list of contracts?
        self._config = config

    def newListener(self, contract, event, fromBlock='latest'):
        """Create a filter to get events from latest block by default."""
        return contract.events[event].createFilter(fromBlock=fromBlock)


class EventProcessor:
    """
    This class provides an event processor to capture events
    then send these events to event listeners.
    """

    def __init__(self, config):
        self._config = config
        self._wo_completed_hash = get_keccak_for_text(
            "workOrderCompleted(bytes32,bytes32,uint256,string,"
            + "uint256,bytes4)")
        self._wo_submitted_hash = get_keccak_for_text(
            "workOrderSubmitted(bytes32,bytes32,bytes32,string,"
            + "uint256,address,bytes4)")

    async def listener(self, event_filter):
        """
        Listen to new events since the last poll on this filter.
        Although this method uses events, it is not fully asynchronous.
        """
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
        """Start event handler to handle events."""
        logging.info("Started handler to handle events")
        while True:
            event = await self.queue.get()
            logging.debug("Event popped from listener queue")

            callback(event, *kargs, **kwargs)
            self.queue.task_done()

    async def sync_handler(self, check_event_callback=None, *kargs, **kwargs):
        """Start a synchronous event handler to handle an event."""
        logging.info("Started synchronous handler to handle an event")
        while True:

            event = await self.queue.get()
            logging.debug("Event popped from listener queue")
            self.queue.task_done()

            # Break out of the loop if check_event_callback method is
            # None(caller does not want to check the event).
            # Also break if it is defined and returns True when called
            # else continue waiting for a True return value.
            if check_event_callback is None or \
                    check_event_callback(event, *kargs, **kwargs) is True:
                break

        return event

    async def start(self, event_filter, callback, *kargs, **kwargs):
        """Start event processor in an infinite loop."""
        self.queue = asyncio.Queue()
        loop = asyncio.get_event_loop()
        self.listeners = [loop.create_task(
            self.listener(event_filter)) for _ in range(1)]
        self.handlers = [loop.create_task(self.handler(
            callback, *kargs, **kwargs)) for _ in range(1)]

        await asyncio.gather(*self.listeners)  # infinite loop
        await self.queue.join()  # this code should never run
        await self.stop()  # this code should never run

    async def get_event_synchronously(self, event_filter,
                                      callback, *kargs, **kwargs):
        """
        Get a single event synchronously using the event_filter
        provided.

        Returns an event received for the event_filter used.
        """
        self.queue = asyncio.Queue()
        loop = asyncio.get_event_loop()
        self.listeners = [loop.create_task(
            self.listener(event_filter)) for _ in range(1)]
        self.handlers = [loop.create_task(
            self.sync_handler(callback, *kargs, **kwargs))]

        handler_result = await asyncio.gather(*self.handlers)

        return handler_result

    async def stop(self):
        """Stop the event processor that was started with start()."""
        for process in self.listeners:
            process.cancel()
        for process in self.handlers:
            process.cancel()
        logging.debug("---exit---")
