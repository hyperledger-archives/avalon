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
from abc import ABC, abstractmethod

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

LISTENER_SLEEP_DURATION = 2  # second

class EventProcessor(ABC):

    async def listener(self, event_filter, *kargs, **kwargs):
        """
        This function defines a listener that runs an infinite loop to
        listen for events from an event source. The optional event_filter
        is also passed to the blockchain specific get_events() function
        call. It puts the raw events into a shared queue which handlers
        would be reading from. It sleeps for a short duration of
        LISTENER_SLEEP_DURATION seconds after fetching and putting into
        the queue, a batch of events.
        """
        logging.info("Started listener for events from blockchain")
        while True:
            # Check for any new event logs since the last poll
            # on this filter. Though using events, this is not
            # fully asynchronous.
            for event in await self.get_events(event_filter, *kargs, **kwargs):
                await self.queue.put(event)
                logging.debug("Event pushed into listener Queue")
            #await asyncio.sleep(LISTENER_SLEEP_DURATION)

    @abstractmethod
    async def get_events(self, event_filter, *kargs, **kwargs):
        """
        This function is meant to be implemented by blockchain specific
        event processor. It gets events from the event source on the
        basis of the event_filter passed in.
        Returns:
            An iterable set/list of events received from event source.
        """
        pass

    async def handler(self, callback, *kargs, **kwargs):
        """
        This function defines a typical event handler that waits on
        a shared queue to get events in an infinite loop. Once it gets
        an event it passes it on to process_and_delegate() which
        thereafter might process and delegate to the callback function.
        """
        logging.info("Started handler to handle events")
        while True:
            event = await self.queue.get()
            logging.debug("Event popped from listener queue")
            self.process_and_delegate(event, callback, *kargs, **kwargs)
            self.queue.task_done()

    @abstractmethod
    def process_and_delegate(self, event, callback, *kargs, **kwargs):
        """
        This function is meant to be implemented by blockchain specific
        event processor. It processes the event passed in to it and then
        passes on the processed event to the callback function for
        appropriate handling.
        """
        pass

    async def sync_handler(self, *kargs, **kwargs):
        """
        Unlike handler(), this function handles only one event at a time.
        It makes a call to process_and_get() with the event received which
        optionally processes the event or returns as it is.
        Returns:
            The processed event.
        """
        logging.info("Started synchronous handler to handle an event")
        event = await self.queue.get()
        logging.debug("Event popped from listener queue")
        processed_event = self.process_and_get(event, *kargs, **kwargs)
        self.queue.task_done()
        return processed_event

    @abstractmethod
    def process_and_get(self, event, *kargs, **kwargs):
        """
        This function is meant to be implemented by blockchain specific
        event processor. It processes the event passed in to it.
        Returns:
            The processed event to the synchronous event handler.
        """
        pass

    async def start(self, event_filter, callback, *kargs, **kwargs):
        """
        This function starts the event processor which boils down to
        creating listener and handler asyncio tasks that run infinitely.
        The listeners and handlers manage events over a shared queue which
        is also instantiated here. This function then waits over the listeners
        to finish using a gather() which is not possible without an external
        factor (as the listeners are in infinite loops).
        """
        loop = asyncio.get_event_loop()

        self.queue = asyncio.Queue()
        self.listeners = self.get_listeners(loop, event_filter)
        self.handlers = self.get_handlers(loop, callback, *kargs, **kwargs)

        await asyncio.gather(*self.listeners)  # infinite loop
        await self.queue.join()  # this code should never run
        await self.stop()  # this code should never run

    async def get_event_synchronously(self, event_filter, *kargs, **kwargs):
        """
        This function gets a single event synchronously using the
        event_filter provided.
        Returns:
            The single event received for the event_filter used.
        """
        self.queue = asyncio.Queue()
        loop = asyncio.get_event_loop()
        self.listeners = self.get_listeners(loop, event_filter)
        self.handlers = self.get_handler(loop, *kargs, **kwargs)

        handler_result = await asyncio.gather(*self.handlers)

        return handler_result

    @abstractmethod
    def get_listeners(self, loop, event_filter):
        """
        This function is meant to be implemented by blockchain specific
        event processor. This function creates one or more asyncio tasks
        for the event loop passed in. The optional event_filter is passed
        to the tasks as well. These tasks are listeners that listen for
        events from some event source.
        Returns:
            A list of listener tasks.
        """
        pass

    @abstractmethod
    def get_handlers(self, loop, callback, *kargs, **kwargs):
        """
        This function is meant to be implemented by blockchain specific
        event processor. This function creates one or more asyncio tasks
        for the event loop passed in. The optional callback is passed
        to the tasks as well. These tasks are handlers that handle the
        events that have been put in a shared queue by the listeners in
        action.
        Returns:
            A list of handler tasks.
        """
        pass

    def get_handler(self, loop, *kargs, **kwargs):
        """
        This function creates a single asyncio task for the event loop passed
        in. This task is the handler that handles the event that has been put
        in a shared queue by one of the listeners in action.
        Returns:
            A list with a single handler task.
        """
        return [loop.create_task(self.sync_handler(*kargs, **kwargs))]

    async def stop(self):
        """
        This function graciously ends the listener and handler tasks.
        """
        for process in self.listeners:
            process.cancel()
        for process in self.handlers:
            process.cancel()
        logging.debug("---exit---")