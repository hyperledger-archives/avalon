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
from hfc.fabric.peer import create_peer
from hfc.fabric.client import Client

logger = logging.getLogger(__name__)


def get_net_info(netinfo, *key_path):
    """
    Get the info from network_info
    :param key_path: path of the key, e.g., a.b.c means info['a']['b']['c']
        :return: The value, or None
    """
    result = netinfo
    if result:
        for k in key_path:
            try:
                result = result[k]
            except KeyError:
                logger.warning(f'No key path {key_path} exists'
                               f' in net info')
                return None
    return result


async def get_stream_result(stream):
    res = []
    async for v in stream:
        logger.debug('Responses of send_transaction:\n {}'.format(v))
        res.append(v)
    return res


class ClientBase:
    def __init__(self, profile, channel_name, org_name, peer_name, user_name):
        self.client = Client(profile)
        self._channel_name = channel_name
        self._org_name = org_name
        self._peer_name = peer_name
        self._user_name = user_name

        self._user = self.client.get_user(self._org_name, self._user_name)
        endpoint = self.client.get_net_info('peers', self._peer_name, 'url')
        tlscert = self.client.get_net_info(
            'peers', self._peer_name, 'tlsCACerts', 'path')
        loop = asyncio.get_event_loop()

        peer = create_peer(endpoint=endpoint, tls_cacerts=tlscert)

        loop.run_until_complete(self.client.init_with_discovery(
            self._user, peer, self._channel_name))

        self._channel = self.client.new_channel(self._channel_name)

    @property
    def channel_name(self):
        return self._channel_name

    @property
    def channel(self):
        return self._channel

    @property
    def org_name(self):
        return self._org_name

    @property
    def peer_name(self):
        return self._peer_name

    @property
    def user_name(self):
        return self._user_name

    @property
    def user(self):
        return self._user
