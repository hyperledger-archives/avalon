#!/usr/bin/python
# Copyright IBM Corp. 2020 All Rights Reserved.
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
import grpc
from hfc.fabric.peer import create_peer

from avalon_sdk.connector.blockchains.fabric import base

logger = logging.getLogger(__name__)


class EventListener(base.ClientBase):
    """
    Utility class to listen to Fabric block chain events.
    """

    def __init__(self, profile, channel_name, org_name, peer_name, user_name):
        super().__init__(profile, channel_name, org_name, peer_name, user_name)
        endpoint = self.client.get_net_info('peers', self.peer_name, 'url')
        tlscert = self.client.get_net_info(
            'peers', self.peer_name, 'tlsCACerts', 'path')

        peer = create_peer(endpoint=endpoint, tls_cacerts=tlscert)

        self._channel_event_hub = self.channel.newChannelEventHub(
            peer, self.user)
        self._event_regid = ''
        self._event = ''
        self._chaincode = ''

    @property
    def handler(self):
        return self._handler

    @handler.setter
    def handler(self, handler):
        self._handler = handler

    @property
    def chaincode(self):
        return self._chaincode

    @chaincode.setter
    def chaincode(self, chaincode):
        self._chaincode = chaincode

    @property
    def event(self):
        return self._event

    @event.setter
    def event(self, event):
        self._event = event

    async def start_event_handling(self):
        """
        Start event listener and listen for events forever
        Only way to stop the event listener by calling
        stop_event_listener()
        """
        def _event_handler(event, block_num, txnid, status):
            logger.debug(
                'Event: {0}\nblock_num: {1}\ntxid: {2}\nstatus: {3}'.format(
                    event, block_num, txnid, status))
            try:
                self._handler(event, block_num, txnid, status)
            except Exception as ex:
                logger.error('Handler error: {0}'.format(ex))

        # Event hub object with latest block
        stream = self._channel_event_hub.connect(
            filtered=False, start='newest')

        self._event_regid = self._channel_event_hub.registerChaincodeEvent(
            self._chaincode, self._event,
            onEvent=_event_handler)
        try:
            await asyncio.gather(stream, return_exceptions=True)
        except Exception as ex:
            # This is expected when event hub gets disconnected
            logger.error("Channel event hub connect failed: {}".format(ex))

    async def stop_event_handling(self, seconds=0):
        """
        Stop event listener.
        """
        await asyncio.sleep(seconds)
        self._channel_event_hub.unregisterChaincodeEvent(self._event_regid)
        self._channel_event_hub.disconnect()

    async def get_single_event(self):
        """
        Start event listener and listen for particular event.
        Once we got the particular event then unregister and
        close the event listenerhub.
        """
        def _event_handler(event, block_num, txnid, status):
            logger.debug(
                'Event: {0}\nblock_num: {1}\ntxid: {2}\nstatus: {3}'.format(
                    event, block_num, txnid, status))
            try:
                # When to stop event handling?
                # Based the flag return by the _handler
                is_done = self._handler(event, block_num, txnid, status)
                if is_done:
                    asyncio.get_event_loop().run_until_complete(
                        self.stop_event_handling())
            except Exception as ex:
                logger.error('Handler error: {0}'.format(ex))

        # Event hub object with latest block
        stream = self._channel_event_hub.connect(filtered=False,
                                                 start='newest')

        self._event_regid = self._channel_event_hub.registerChaincodeEvent(
            self._chaincode, self._event,
            onEvent=_event_handler)
        try:
            # wait for the connect() to get the stream of events
            # it will call the event handler function(_event_handler)
            # it will be unblocked only when call disconnect()
            await asyncio.gather(stream, return_exceptions=True)
        except Exception as ex:
            # This is expected when event hub gets disconnected
            logger.error("Channel event hub connect failed: {}".format(ex))
