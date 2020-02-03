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
import json
import toml
from web3 import Web3

from avalon_sdk.ethereum.ethereum_worker_registry_list import \
    EthereumWorkerRegistryListImpl
from avalon_sdk.registry.registry_status import RegistryStatus
from utility.hex_utils import hex_to_utf8, pretty_ids

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


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
                raise Exception('Could not open config file: %s', e)
        self.__eth_conn = EthereumWorkerRegistryListImpl(self.__config)

    def test_registry_add(self):
        self.__org_id = urandom(32)
        self.__uri = "http://127.0.0.1:1947"
        self.__sc_addr = urandom(32)
        self.__app_type_ids = [urandom(32), urandom(32)]
        logging.info(
            'Calling registry_add contract..\n org_id: %s\n ' +
            'uri: %s\n ' +
            'sc_addr: %s\n application_ids: %s', hex_to_utf8(self.__org_id),
            self.__uri, hex_to_utf8(self.__sc_addr),
            pretty_ids(self.__app_type_ids))
        result = self.__eth_conn.registry_add(
            self.__org_id, self.__uri, self.__sc_addr,
            self.__app_type_ids)
        logging.info(
            "registry_add contract status \n %s",
            result)
        self.assertIsNotNone(
            result, "Registry add response not matched")

    def test_registry_update(self):
        self.__new_app_id = [urandom(32)]
        self.__new_uri = 'http://localhost:1947'
        logging.info(
            'Calling registry_update contract..\n org_id: %s\n uri: %s\n ' +
            'sc_addr: %s\n application_ids: %s', hex_to_utf8(self.__org_id),
            self.__new_uri, hex_to_utf8(self.__sc_addr),
            pretty_ids(self.__new_app_id))
        result = self.__eth_conn.registry_update(
            self.__org_id, self.__new_uri, self.__sc_addr, self.__new_app_id)
        logging.info(
            "registry_update contract status \n%s",
            result)
        self.assertIsNotNone(
            result, "Registry update response not matched")

    def test_registry_set_status(self):
        self.__new_status = RegistryStatus.OFF_LINE
        logging.info(
            'Calling registry_set_status contract..\n org_id: %s\n status: %d',
            hex_to_utf8(self.__org_id), self.__new_status.value)
        result = self.__eth_conn.registry_set_status(
            self.__org_id, self.__new_status)
        logging.info(
            "registry_set_status contract status \n%s",
            result)
        self.assertIsNotNone(
            result, "Registry set status response not matched")

    def test_registry_lookup(self):
        logging.info(
            'Calling registry_lookup..\n application_id: %s',
            hex_to_utf8(self.__app_type_ids[0]))
        result = self.__eth_conn.registry_lookup(self.__app_type_ids[0])
        logging.info(
            'registry_lookup contract status [%d, %s, %s]',
            result[0], result[1], pretty_ids(result[2]))
        self.assertEqual(
            result[0], 1, "Registry lookup response total count not matched")
        self.assertEqual(
            result[2][0], self.__org_id,
            "Registry lookup response not matched for org id")

    def test_registry_retrieve(self):
        logging.info('Calling registry_retrieve..\n org_id: %s',
                     hex_to_utf8(self.__org_id))
        result = self.__eth_conn.registry_retrieve(self.__org_id)
        logging.info(
            'registry_retrieve contract status [%s, %s, %s, %d]',
            result[0], hex_to_utf8(result[1]), pretty_ids(result[2]),
            result[3])
        self.assertEqual(
            result[0], self.__new_uri,
            "Registry retrieve response not matched for uri")
        self.assertEqual(
            hex_to_utf8(result[1]),
            hex_to_utf8(self.__sc_addr),
            "Registry retrieve response not matched for " +
            "smart contract address")
        self.assertEqual(
            result[2][0], self.__app_type_ids[0],
            "Registry retrieve response not matched for app id type list " +
            "index 0")
        self.assertEqual(
            result[2][1], self.__app_type_ids[1],
            "Registry retrieve response not matched for app id type list " +
            "index 1")
        self.assertEqual(
            result[2][2], self.__new_app_id[0],
            "Registry retrieve response not matched for app id type list " +
            "index 2")
        self.assertEqual(
            result[3], self.__new_status.value,
            "Registry retrieve response not matched for status")

    def test_registry_lookup_next(self):
        lookup_tag = "test"
        logging.info(
            'Calling registry_lookup_next..\n application_id: %s\n ' +
            'lookup_tag: %s',
            hex_to_utf8(self.__app_type_ids[0]), lookup_tag)
        result = self.__eth_conn.registry_lookup_next(
            self.__app_type_ids[0], lookup_tag)
        logging.info('registry_lookup_next contract status [%d, %s, %s]',
                     result[0], result[1], pretty_ids(result[2]))


def main():
    logging.info("Running test cases...")
    tcf_home = environ.get("TCF_HOME", "../../")
    test = TestEthereumWorkerRegistryListImpl(
        tcf_home +
        "/sdk/avalon_sdk/" + "tcf_connector.toml")
    test.test_registry_add()
    test.test_registry_update()
    test.test_registry_set_status()
    test.test_registry_retrieve()
    test.test_registry_lookup()
    test.test_registry_lookup_next()


if __name__ == '__main__':
    main()
