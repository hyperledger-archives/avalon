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
#

import logging
from os.path import isfile, realpath
import errno
import toml

from tcf_connector.connector_adaptor_factory_interface import \
    ConnectorAdaptorFactoryInterface
from tcf_connector.ethereum.ethereum_worker_registry_list_impl import \
    EthereumWorkerRegistryListImpl
from tcf_connector.ethereum.ethereum_worker_registry_impl import \
    EthereumWorkerRegistryImpl

logger = logging.getLogger(__name__)

class BlockchainAdaptorFactoryImpl(ConnectorAdaptorFactoryInterface):
    """
    Adaptor for Ethereum blockchain
    It is used in proxy model
    1. Worker registry list adaptor interact with blockchain
    2. Worker registry adaptor interact with blockchain
    3. Work order adaptor interact with blockchain
    4. Work order receipt interact with blockchain
    """
    def __init__(self, config_file):
        if not isfile(config_file):
            raise FileNotFoundError("File not found at path: {0}".format(realpath(config_file)))
        try:
            with open(config_file) as fd:
                self.__config = toml.load(fd)
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise Exception('Could not open config file: %s' % e)
        self.__worker_registry_list = None
        self.__worker_registry = None
        self.__work_order = None
        self.__work_order_receipts = None
        self.__blockchain_type = self.__config['blockchain']['type']

    def create_worker_registry_list_adaptor(self):
        if self.__blockchain_type == "Ethereum":
            if self.__worker_registry_list is None:
                self.__worker_registry_list = EthereumWorkerRegistryListImpl(config)
            return self.__worker_registry_list

    def create_worker_registry_adaptor(self, config):
        if self.__blockchain_type == "Ethereum":
            if self.__worker_registry is None:
                self.__worker_registry = EthereumWorkerRegistryImpl(config)
            return self.__worker_registry

    def create_work_order_adaptor(self, config):
        """
        TODO: Yet to implement for proxy model
        """
        return None

    def create_work_order_receipt_adaptor(self, config):
        """
        TODO: Yet to implement for proxy model
        """
        return None

