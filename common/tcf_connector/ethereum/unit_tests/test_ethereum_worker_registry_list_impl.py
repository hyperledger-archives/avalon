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

import binascii
import errno
import logging
from os import path, urandom, environ
import unittest

import toml

from tcf_connector.ethereum.ethereum_worker_registry_list_impl import \
    EthereumWorkerRegistryListImpl
from utils.tcf_types import RegistryStatus

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

class TestEthereumWorkerRegistryListImpl(unittest.TestCase):
    def __init__(self, config_file):
        super(TestEthereumWorkerRegistryListImpl, self).__init__()
        if not path.isfile(config_file):
            raise FileNotFoundError("File not found at path: {0}".format(
                path.realpath(config_file)))
        try:
            with open(config_file) as fd:
                self.__config = toml.load(fd)
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise Exception('Could not open config file: %s',e)
        self.__eth_conn = EthereumWorkerRegistryListImpl(self.__config)
    
    def test_registry_add(self):
        self.__org_id = urandom(32)
        self.__uri = "http://worker1:8008"
        self.__sc_addr = urandom(32)
        self.__app_type_ids = [urandom(32), urandom(32)]
        logging.info('Calling registry_add contract..\n org_id: %s\n uri: %s\n \
            sc_addr: %s application_ids: %s', binascii.hexlify(self.__org_id),
            self.__uri,binascii.hexlify(self.__sc_addr),self.__app_type_ids)
        result = self.__eth_conn.registry_add(self.__org_id,  self.__uri, self.__sc_addr,
            self.__app_type_ids)
        logging.info('registry_add contract status %s', result)
        self.assertEqual(result['status'], 'added', "Registry add response not matched")

    def test_registry_update(self):
        self.__new_app_id = [urandom(32)]
        self.__new_uri = 'http://worker2:8008'
        logging.info('Calling registry_update contract..\n org_id: %s\n uri: %s\n \
            sc_addr: %s application_ids: %s',binascii.hexlify(self.__org_id),
            self.__new_uri,binascii.hexlify(self.__sc_addr),self.__new_app_id)
        result = self.__eth_conn.registry_update(self.__org_id,  self.__new_uri,
            self.__sc_addr, self.__new_app_id)
        logging.info('registry_update contract status %s', result)
        self.assertEqual(result['status'], 'added', "Registry update response not matched")
    
    def test_registry_set_status(self):
        self.__new_status = RegistryStatus.OFF_LINE
        logging.info('Calling registry_set_status contract..\n org_id: %s\n status: %d',
            binascii.hexlify(self.__org_id), self.__new_status.value)
        result = self.__eth_conn.registry_set_status(self.__org_id, self.__new_status)
        logging.info('registry_set_status contract status %s', result)
        self.assertEqual(result['status'], 'added', "Registry set status response not matched")
    
    def test_registry_lookup(self):
        logging.info('Calling registry_lookup..\n application_id: %s', 
            binascii.hexlify(self.__app_type_ids[0]))
        result = self.__eth_conn.registry_lookup(self.__app_type_ids[0])
        logging.info('registry_lookup contract status %s', result)
        self.assertEqual(result[0], 1, "Registry lookup response total count not matched")
        self.assertEqual(result[2][0], self.__org_id, 
            "Registry lookup response not matched for org id")


    def test_registry_retrieve(self):
        logging.info('Calling registry_retrieve..\n org_id: %s\n', binascii.hexlify(self.__org_id))
        result = self.__eth_conn.registry_retrieve(self.__org_id)
        logging.info('registry_retrieve contract status %s', result)
        self.assertEqual(result[0], self.__new_uri, 
            "Registry retrieve response not matched for uri")
        self.assertEqual(binascii.hexlify(result[1]).decode("utf8"), 
            binascii.hexlify(self.__sc_addr).decode("utf8"), 
            "Registry retrieve response not matched for smart contract address")
        self.assertEqual(result[2][0], self.__app_type_ids[0], 
            "Registry retrieve response not matched for app id type list index 0")
        self.assertEqual(result[2][1], self.__app_type_ids[1], 
            "Registry retrieve response not matched for app id type list index 1")
        self.assertEqual(result[2][2], self.__new_app_id[0],
            "Registry retrieve response not matched for app id type list index 2")
        self.assertEqual(result[3], self.__new_status.value,
            "Registry retrieve response not matched for status")

    def test_registry_lookup_next(self):
        lookup_tag = "test"
        logging.info('Calling registry_lookup_next..\n application_id: %s lookup_tag: %s',
            binascii.hexlify(self.__app_type_ids[0]), lookup_tag)
        result = self.__eth_conn.registry_lookup_next(self.__app_type_ids[0], lookup_tag)
        logging.info('registry_lookup_next contract status %s', result)



def main():
    logging.info("Running test cases...")
    tcf_home = environ.get("TCF_HOME", "../../")
    test = TestEthereumWorkerRegistryListImpl(tcf_home + "/common/tcf_connector/" + "tcf_connector.toml")
    test.test_registry_add()
    test.test_registry_update()
    test.test_registry_set_status()
    test.test_registry_retrieve()
    test.test_registry_lookup()
    test.test_registry_lookup_next()

if __name__ == '__main__':
    main()
