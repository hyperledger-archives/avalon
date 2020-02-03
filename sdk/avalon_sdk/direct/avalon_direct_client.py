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

import logging
from os.path import isfile, realpath
import errno
import toml

from avalon_sdk.ethereum.ethereum_worker_registry_list import \
    EthereumWorkerRegistryListImpl
from avalon_sdk.direct.jrpc.jrpc_worker_registry import JRPCWorkerRegistryImpl
from avalon_sdk.direct.jrpc.jrpc_work_order import JRPCWorkOrderImpl
from avalon_sdk.direct.jrpc.jrpc_work_order_receipt \
     import JRPCWorkOrderReceiptImpl

logger = logging.getLogger(__name__)


class AvalonDirectClient():
    """
    This is class for the direct JSON RPC API client.
    It is used in direct model
    1. Worker registry list interacts with blockchain it is optional.
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
                raise FileNotFoundError("File not found at path: {0}"
                                        .format(realpath(config_file)))
            try:
                with open(config_file) as fd:
                    self.__config = toml.load(fd)
            except IOError as e:
                """
                Catch the exception related to toml file format except for
                the File does not exist exception.
                """
                if e.errno != errno.ENOENT:
                    raise Exception('Could not open config file: %s' % e)

        self.__blockchain_type = self.__config['blockchain']['type']
        if self.__blockchain_type == "Ethereum":
                self.__worker_registry_list = EthereumWorkerRegistryListImpl(
                    self.__config)
        else:
            self.__worker_registry_list = None
        self.__worker_registry = JRPCWorkerRegistryImpl(self.__config)
        self.__work_order = JRPCWorkOrderImpl(self.__config)
        self.__work_order_receipts = JRPCWorkOrderReceiptImpl(self.__config)

    def get_worker_registry_list_instance(self):
            return self.__worker_registry_list

    def get_worker_registry_instance(self):
        return self.__worker_registry

    def get_work_order_instance(self):
        return self.__work_order

    def get_work_order_receipt_instance(self):
        return self.__work_order_receipts
