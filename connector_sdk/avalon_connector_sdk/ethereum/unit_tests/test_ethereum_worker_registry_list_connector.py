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

from os import urandom, path, environ
import errno
import logging
import toml
import json
import unittest
from web3 import Web3

from avalon_connector_sdk.ethereum.ethereum_worker_registry_list_connector \
    import EthereumWorkerRegistryListConnectorImpl
from avalon_client_sdk.utility.tcf_types import RegistryStatus
from utility.hex_utils import hex_to_utf8, pretty_ids


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class TestEthereumWorkerRegistryConnector(unittest.TestCase):
    def __init__(self, config_file):
        super(TestEthereumWorkerRegistryConnector, self).__init__()
        if not path.isfile(config_file):
            raise FileNotFoundError("File not found at path: {0}".format(
                path.realpath(config_file)))
        try:
            with open(config_file) as fd:
                self.__config = toml.load(fd)
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise Exception("Could not open config file: %s", e)
        self.__eth_conn = EthereumWorkerRegistryListConnectorImpl(
            self.__config)

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
            "registry_add contract status \n{'status': %s', \n" +
            "'txn_receipt': %s}",
            result["status"],
            json.dumps(
                json.loads(Web3.toJSON(result["txn_receipt"])), indent=4))
        self.assertEqual(
            result['status'], 'added', "Registry add response not matched")

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
            "registry_update contract status \n{'status': %s', \n" +
            "'txn_receipt': %s}",
            result["status"],
            json.dumps(
                json.loads(Web3.toJSON(result["txn_receipt"])), indent=4))
        self.assertEqual(
            result['status'], 'added', "Registry update response not matched")

    def test_registry_set_status(self):
        self.__new_status = RegistryStatus.OFF_LINE
        logging.info(
            'Calling registry_set_status contract..\n org_id: %s\n status: %d',
            hex_to_utf8(self.__org_id), self.__new_status.value)
        result = self.__eth_conn.registry_set_status(
            self.__org_id, self.__new_status)
        logging.info(
            "registry_set_status contract status \n{'status': %s', \n" +
            "'txn_receipt': %s}",
            result["status"],
            json.dumps(json.loads(Web3.toJSON(result["txn_receipt"])),
                       indent=4))
        self.assertEqual(
            result['status'], 'added',
            "Registry set status response not matched")


def main():
    logging.info("Running test cases...")
    tcf_home = environ.get("TCF_HOME", "../../")
    test = TestEthereumWorkerRegistryConnector(
        tcf_home +
        "/client_sdk/avalon_client_sdk/" + "tcf_connector.toml")
    test.test_registry_add()
    test.test_registry_update()
    test.test_registry_set_status()


if __name__ == "__main__":
    main()
