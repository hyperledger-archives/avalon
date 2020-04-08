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

from os import urandom, path, environ
import errno
import logging
import toml
import json
import unittest
from web3 import Web3

from avalon_sdk.connector.blockchains.ethereum.ethereum_worker_registry \
    import EthereumWorkerRegistryImpl
from avalon_sdk.worker.worker_details import WorkerType, WorkerStatus
from utility.hex_utils import hex_to_utf8, pretty_ids


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class TestEthereumWorkerRegistryImpl(unittest.TestCase):
    def __init__(self, config_file):
        super(TestEthereumWorkerRegistryImpl, self).__init__()
        if not path.isfile(config_file):
            raise FileNotFoundError("File not found at path: {0}".format(
                path.realpath(config_file)))
        try:
            with open(config_file) as fd:
                self.__config = toml.load(fd)
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise Exception("Could not open config file: %s", e)
        self.__eth_conn = EthereumWorkerRegistryImpl(self.__config)

    def test_worker_register(self):
        self.__worker_id = urandom(32).hex()
        self.__worker_type = WorkerType.TEE_SGX
        self.__details = json.dumps(
            {"workOrderSyncUri": "http://worker-order:8008"})
        self.__org_id = urandom(32).hex()
        self.__application_ids = [urandom(32).hex(),
                                  urandom(32).hex(),
                                  urandom(32).hex()]
        logging.info(
            "Calling worker_register contract..\n worker_id: %s\n " +
            "worker_type: %d\n " +
            "orgId: %s\n applicationIds %s\n details %s",
            self.__worker_id, self.__worker_type.value,
            self.__org_id, self.__application_ids,
            self.__details)
        result = self.__eth_conn.worker_register(
            self.__worker_id, self.__worker_type,
            self.__org_id, self.__application_ids, self.__details)
        logging.info(
            "worker_register status \n %s",
            result)
        self.assertIsNotNone(
            result, "transaction execution failed")

    def test_worker_set_status(self):
        self.__status = WorkerStatus.DECOMMISSIONED
        logging.info(
            "Calling worker_set_status..\n worker_id: %s\n status: %d",
            self.__worker_id, self.__status.value)
        result = self.__eth_conn.worker_set_status(
            self.__worker_id, self.__status)
        logging.info(
            "worker_set_status status \n%s",
            result)
        self.assertIsNotNone(result, "worker set status response not matched")

    def test_worker_update(self):
        self.__new_details = json.dumps({
            "torkOrderSyncUri": "http://worker-order:8008",
            "workOrderNotifyUri": "http://worker-order-notify:9909"
        })
        logging.info(
            "Calling worker_update..\n worker_id: %s\n details: %s",
            self.__worker_id, self.__new_details)
        result = self.__eth_conn.worker_update(
            self.__worker_id, self.__new_details)
        logging.info(
            "worker_update status \n %s",
            result)
        self.assertIsNotNone(
            result, "worker update response not matched")

    def test_worker_lookup(self):
        logging.info(
            "Calling worker_lookup..\n worker_type: %d\n orgId: %s\n " +
            "applicationId: %s",
            self.__worker_type.value,
            self.__org_id,
            self.__application_ids[0])
        result = self.__eth_conn.worker_lookup(
            self.__worker_type, self.__org_id,
            self.__application_ids[0])["result"]
        logging.info(
            "worker_lookup status [%d, %s, %s]",
            result["totalCount"], result["lookupTag"], result["ids"])
        match = self.__worker_id in result["ids"]
        self.assertEqual(
            result["totalCount"], 1, "Worker lookup response should match")
        self.assertTrue(
            match, "Worker lookup response worker id doesn't match")

    def test_worker_retrieve(self):
        logging.info(
            "Calling worker_retrieve..\n worker_id: %s",
            self.__worker_id)
        result = self.__eth_conn.worker_retrieve(self.__worker_id)["result"]
        logging.info(
            "worker_retrieve status [%d, %s, %s, %s, %s]", result["status"],
            result["workerType"], result["organizationId"],
            result["applicationTypeId"],
            result["details"])
        self.assertEqual(
            result["workerType"], self.__worker_type.value,
            "Worker retrieve response worker type doesn't match")
        self.assertEqual(
            result["organizationId"], self.__org_id,
            "Worker retrieve response organization id doesn't match")
        self.assertEqual(
            result["applicationTypeId"][0], self.__application_ids[0],
            "Worker retrieve response application id[0] doesn't match")
        self.assertEqual(
            result["applicationTypeId"][1], self.__application_ids[1],
            "Worker retrieve response application id[1] doesn't match")
        self.assertEqual(
            result["details"], json.loads(self.__new_details),
            "Worker retrieve response worker details doesn't match")
        self.assertEqual(
            result["status"], self.__status.value,
            "Worker retrieve response worker status doesn't match")

    def test_worker_lookup_next(self):
        lookUpTag = ""
        logging.info(
            "Calling worker_lookup_next..\n worker_type: %d\n" +
            "orgId: %s\n applicationId:%s\n lookUpTag: %s",
            self.__worker_type.value, self.__org_id,
            self.__application_ids[0], lookUpTag)
        result = self.__eth_conn.worker_lookup_next(
            self.__worker_type, self.__org_id, self.__application_ids[0],
            lookUpTag)
        logging.info(result)
        logging.info("worker_lookup_next status [%d, %s, %s]",
                     result[0], result[1], result[2])
        self.assertEqual(
            result[0], 0, "worker_lookup_next response count doesn't match")


def main():
    logging.info("Running test cases...")
    tcf_home = environ.get("TCF_HOME", "../../")
    test = TestEthereumWorkerRegistryImpl(
        tcf_home +
        "/sdk/avalon_sdk/" + "tcf_connector.toml")
    test.test_worker_register()
    test.test_worker_update()
    test.test_worker_set_status()
    test.test_worker_lookup()
    test.test_worker_retrieve()
    # Not properly defined in EEA spec. To be enabled as feature is enabled.
    # test.test_worker_lookup_next()


if __name__ == "__main__":
    main()
