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

from avalon import base

logger = logging.getLogger(__name__)

class EventListener(base.ClientBase):
    def __init__(self, profile, channel_name, org_name, peer_name, user_name):
        super().__init__(profile, channel_name, org_name, peer_name, user_name)
        endpoint = self.client.get_net_info('peers', self.peer_name, 'url')
        tlscert = self.client.get_net_info('peers', self.peer_name, 'tlsCACerts', 'path')

        peer = create_peer(endpoint=endpoint, tls_cacerts=tlscert)

        self._channel_event_hub = self.channel.newChannelEventHub(peer, self.user)
        self._event_regid = ''
        self._last_block = 0
        self._config = 'blockmark'
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

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        self._config = config
        try:
            with open(self._config, 'r') as file:
                data = file.read()
                if len(data) > 0:
                    self._last_block = int(data)
            logger.info('Loaded block mark: %s', self._last_block)
        except IOError:
            pass

    def saveConfig(self):
        with open(self._config, 'w') as file:
            file.write(str(self._last_block))
            logger.info('Saved blockmark: %s', self._last_block)

    async def startEventHandling(self):
        def eventHandler(event, block_num, txnid, status):
            logger.info('Event: {0}\nblock_num: {1}\ntxid: {2}\nstatus: {3}'.format(
                event, block_num, txnid, status))
            try:
                self._handler(event, block_num, txnid, status)
                self._last_block = block_num
            except Exception as ex:
                logger.error('Handler error: {0}'.format(ex))

        self._event_regid = self._channel_event_hub.registerChaincodeEvent(self._chaincode,
            self._event, start=self._last_block, onEvent=eventHandler)
        logger.info('Event handler registered!')
        try:
            await self._channel_event_hub.connect(False)
        except grpc.RpcError as ex:
            # This is expected when event hub gets disconnected
            self.saveConfig()

    async def stopEventHandling(self, seconds):
        await asyncio.sleep(seconds)
        self._channel_event_hub.unregisterChaincodeEvent(self._event_regid)
        self._channel_event_hub.disconnect()
