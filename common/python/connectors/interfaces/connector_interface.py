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

from abc import ABC, abstractmethod


class ConnectorInterface(ABC):
    """
    ConnectorInterface has below methods
    1. Create worker registry list.
    2. Create worker registry.
    3. Create work order.
    4. Create work order receipt.
    Parameter “config” is a dictionary containing configuration in TOML format.
    The type of the adaptor(direct/proxy) is chosen based on the configuration.
    The configuration also contains information required to construct
    and initialize the adaptor, e.g.  URI, user key/log-in info,
    smart contract address, etc.
    Return value is “None” on error or an instantiated object on success.

    """
    def __init__(self):
        super().__init__()

    @abstractmethod
    def create_worker_registry_list(self, config):
        pass

    @abstractmethod
    def create_worker_registry(self, config):
        pass

    @abstractmethod
    def create_work_order(self, config):
        pass

    @abstractmethod
    def create_work_order_receipt(self, config):
        pass
