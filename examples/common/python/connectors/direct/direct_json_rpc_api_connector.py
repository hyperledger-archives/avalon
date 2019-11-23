# Copyright 2019 Intel Corporation
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

import logging
from os.path import isfile, realpath
import errno
import toml

from connectors.interfaces.connector_interface import \
    ConnectorInterface
from connectors.ethereum.ethereum_worker_registry_list_impl import \
    EthereumWorkerRegistryListImpl
from connectors.direct.worker_registry_jrpc_impl import WorkerRegistryJRPCImpl
from connectors.direct.work_order_jrpc_impl import WorkOrderJRPCImpl
from connectors.direct.work_order_receipt_jrpc_impl import WorkOrderReceiptJRPCImpl

logger = logging.getLogger(__name__)


class DirectJsonRpcApiConnector(ConnectorInterface):
    """
    Connector for the direct JSON RPC API.
    It is used in direct model
    1. Worker registry list interacts with blockchain.
    2. Worker registry interacts with json rpc listener.
    3. Work order interacts with json rpc listener.
    4. Work order receipt interacts with json rpc listener.
    """
    def __init__(self, config_file=None, config=None):
        """
        "config_file" is config file path as a string.
        "config" is a dictionary loaded from config_file.
        Either one of config_file or config needs to be passed.
        If both are passed config takes precedence.
        """
        if(config is not None):
            self.__config = config
        else:
            if not isfile(config_file):
                raise FileNotFoundError("File not found at path: {0}".format(realpath(config_file)))
            try:
                with open(config_file) as fd:
                    self.__config = toml.load(fd)
            except IOError as e:
                """
                Catch the exception related to toml file format except File not exists
                exception
                """
                if e.errno != errno.ENOENT:
                    raise Exception('Could not open config file: %s' % e)

        self.__worker_registry_list = None
        self.__worker_registry = None
        self.__work_order = None
        self.__work_order_receipts = None
        self.__blockchain_type = self.__config['blockchain']['type']

    def create_worker_registry_list(self, config):
        if self.__blockchain_type == "Ethereum":
            if self.__worker_registry_list is None:
                self.__worker_registry_list = EthereumWorkerRegistryListImpl(config)
            return self.__worker_registry_list

    def create_worker_registry(self, config):
        if self.__worker_registry is None:
            self.__worker_registry = WorkerRegistryJRPCImpl(config)
        return self.__worker_registry

    def create_work_order(self, config):
        if self.__work_order is None:
            self.__work_order = WorkOrderJRPCImpl(config)
        return self.__work_order

    def create_work_order_receipt(self, config):
        if self.__work_order_receipts is None:
            self.__work_order_receipts = WorkOrderReceiptJRPCImpl(config)
        return self.__work_order_receipts
