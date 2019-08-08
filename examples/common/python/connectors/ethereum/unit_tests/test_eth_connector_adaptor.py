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

from os import urandom
import logging

from connectors.blockchain_adaptor_factory import BlockchainAdaptorFactoryImpl as BCAdaptorFactory

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

class TestEthConnectorAdaptor():
    def __init__(self):
        self.__eth_adaptor = BCAdaptorFactory('tcf_connector.toml')

    def test_direct_registry_adaptor(self):
        orgId = urandom(32)
        uri = "http://worker1:8008"
        scAddr = urandom(20)
        appTypeIds = [urandom(32), urandom(32)]
        logging.info('Calling registryAdd contract..\n orgId: {}\n uri: {}\n scAddr: {} applicationIds: {}'.format(
            orgId, uri,scAddr,appTypeIds))
        self.__eth_adaptor.get_direct_registry_instance().RegistryAdd(orgId, uri, scAddr, appTypeIds)

def main():
    logging.info("Running test cases...")
    test = TestEthConnectorAdaptor()
    test.test_direct_registry_adaptor()
    
if __name__ == '__main__':
    main()
