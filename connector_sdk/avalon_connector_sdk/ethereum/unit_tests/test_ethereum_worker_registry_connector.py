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
import binascii
import json
import unittest
from web3 import Web3

from avalon_connector_sdk.ethereum.ethereum_worker_registry_connector \
    import EthereumWorkerRegistryConnectorImpl
from avalon_client_sdk.utility.tcf_types import WorkerType, WorkerStatus
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
        self.__eth_conn = EthereumWorkerRegistryConnectorImpl(self.__config)

    def test_worker_register(self):
        self.__worker_id = urandom(32)
        self.__worker_type = WorkerType.TEE_SGX
        self.__details = json.dumps(
            {"workOrderSyncUri":
             "http://worker-order:8008".encode("utf-8").hex()})
        self.__org_id = urandom(32)
        self.__application_ids = [urandom(32), urandom(32)]
        logging.info(
            "Calling worker_register contract..\n worker_id: %s\n " +
            "worker_type: %d\n " +
            "orgId: %s\n applicationIds %s\n details %s",
            hex_to_utf8(self.__worker_id), self.__worker_type.value,
            hex_to_utf8(self.__org_id), pretty_ids(self.__application_ids),
            self.__details)
        result = self.__eth_conn.worker_register(
            self.__worker_id, self.__worker_type,
            self.__org_id, self.__application_ids, self.__details)
        self.assertIsNotNone(
            result["txn_receipt"], "transaction execution failed")
        logging.info(
            "worker_register status \n{'status': %s', \n'txn_receipt': %s}",
            result["status"],
            json.dumps(json.loads(Web3.toJSON(result["txn_receipt"])),
                       indent=4))
        self.assertEqual(
            result["status"], "added", "worker register response not matched")

    def test_worker_set_status(self):
        self.__status = WorkerStatus.DECOMMISSIONED
        logging.info(
            "Calling worker_set_status..\n worker_id: %s\n status: %d",
            hex_to_utf8(self.__worker_id), self.__status.value)
        result = self.__eth_conn.worker_set_status(
            self.__worker_id, self.__status)
        logging.info(
            "worker_set_status status \n{'status': %s', \n'txn_receipt': %s}",
            result["status"],
            json.dumps(json.loads(Web3.toJSON(result["txn_receipt"])),
                       indent=4))
        self.assertEqual(result["status"], "added",
                         "worker set status response not matched")

    def test_worker_update(self):
        self.__new_details = json.dumps({
            "workOrderSyncUri":
            "http://worker-order:8008".encode("utf-8").hex(),
            "workOrderNotifyUri":
            "http://worker-order-notify:9909".encode("utf-8").hex()
        })
        logging.info(
            "Calling worker_update..\n worker_id: %s\n details: %s",
            hex_to_utf8(self.__worker_id), self.__new_details)
        result = self.__eth_conn.worker_update(
            self.__worker_id, self.__new_details)
        logging.info(
            "worker_update status \n{'status': %s', \n'txn_receipt': %s}",
            result["status"],
            json.dumps(
                json.loads(Web3.toJSON(result["txn_receipt"])), indent=4))
        self.assertEqual(
            result["status"], "added", "worker update response not matched")


def main():
    logging.info("Running test cases...")
    tcf_home = environ.get("TCF_HOME", "../../")
    test = TestEthereumWorkerRegistryConnector(
        tcf_home +
        "/client_sdk/avalon_client_sdk/" + "tcf_connector.toml")
    test.test_worker_register()
    test.test_worker_update()
    test.test_worker_set_status()


if __name__ == "__main__":
    main()
