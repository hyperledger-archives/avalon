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
import unittest
import toml
from os import path, environ
import errno
import secrets
import json

from avalon_sdk.direct.worker_registry_jrpc_client \
    import WorkerRegistryJRPCClient
from avalon_sdk.worker.worker_details import WorkerType, WorkerStatus

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


class TestWorkerRegistryJRPCImpl(unittest.TestCase):
    def __init__(self, config_file):
        super(TestWorkerRegistryJRPCImpl, self).__init__()
        if not path.isfile(config_file):
            raise FileNotFoundError(
                "File not found at path: {0}".format(
                    path.realpath(config_file)))
        try:
            with open(config_file) as fd:
                self.__config = toml.load(fd)
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise Exception('Could not open config file: %s', e)

        self.__worker_registry_wrapper = WorkerRegistryJRPCClient(
            self.__config)
        self.__worker_id = secrets.token_hex(32)
        self.__worker_type = WorkerType.TEE_SGX
        self.__org_id = secrets.token_hex(32)
        self.__details = json.dumps(
            {"workOrderSyncUri":
             "http://worker-order:8008".encode("utf-8").hex()})
        self.__app_ids = [secrets.token_hex(32), secrets.token_hex(32)]

    def test_worker_register(self):
        req_id = 12
        logging.info(
            'Calling test_worker_register with\n worker_id %s\n' +
            ' worker_type %d\n details %s\n org_id %s\n app_ids %s\n',
            self.__worker_id, self.__worker_type.value, self.__details,
            self.__org_id, self.__app_ids)
        res = self.__worker_registry_wrapper.worker_register(
            self.__worker_id, self.__worker_type,
            self.__org_id, self.__app_ids, self.__details, req_id)
        logging.info('Result: %s\n', res)
        self.assertEqual(
            res['id'], req_id,
            "test_worker_registry Response id doesn't match")
        self.assertEqual(
            res['error']['code'], 0,
            "WorkerRegistry Response error code doesn't match")
        self.assertEqual(
            res['error']['message'], 'Successfully Registered',
            "WorkerRegistry Response error message doesn't match")

    def test_worker_update(self):
        req_id = 13
        self.__details = json.dumps(
            {
                "workOrderSyncUri":
                "http://worker-order:8008".encode("utf-8").hex(),
                "workOrderNotifyUri":
                "http://worker-notify:8008".encode("utf-8").hex()
            })
        logging.info(
            'Calling test_worker_update with\n worker_id %s\n details %s\n',
            self.__worker_id, self.__details)
        res = self.__worker_registry_wrapper.worker_update(
            self.__worker_id, self.__details, req_id)
        logging.info('Result: %s\n', res)
        self.assertEqual(
            res['id'], req_id,
            "worker_update Response id doesn't match")
        self.assertEqual(
            res['error']['code'], 0,
            "worker_update Response error code doesn't match")
        self.assertEqual(
            res['error']['message'], "Successfully Updated",
            "worker_update Response error message doesn't match")

    def test_worker_set_status(self):
        req_id = 14
        self.__status = WorkerStatus.OFF_LINE
        logging.info(
            'Calling test_worker_set_status with\n worker_id %s\n status %d\n',
            self.__worker_id, self.__status.value)
        res = self.__worker_registry_wrapper.worker_set_status(
            self.__worker_id, self.__status, req_id)
        logging.info('Result: %s\n', res)
        self.assertEqual(
            res['id'], req_id, "worker_set_status Response id doesn't match")
        self.assertEqual(
            res['error']['code'], 0,
            "worker_set_status Response error code doesn't match")
        self.assertEqual(
            res['error']['message'], "Successfully Set Status",
            "worker_set_status Response error message doesn't match")

    def test_worker_retrieve(self):
        req_id = 15
        logging.info(
            'Calling test_worker_retrieve with\n worker_id %s\n',
            self.__worker_id)
        res = self.__worker_registry_wrapper.worker_retrieve(
            self.__worker_id, req_id)
        logging.info('Result: %s\n', res)
        self.assertEqual(
            res['id'], req_id, "worker_retrieve Response id doesn't match")
        self.assertEqual(
            res['result']['workerType'], self.__worker_type.value,
            "worker_retrieve Response result workerType doesn't match")
        self.assertEqual(
            res['result']['organizationId'], self.__org_id,
            "worker_retrieve Response result organizationId doesn't match")
        self.assertEqual(
            res['result']['applicationTypeId'][0],
            self.__app_ids[0], "worker_retrieve Response result " +
            "applicationTypeId[0] doesn't match")
        self.assertEqual(
            res['result']['applicationTypeId'][1],
            self.__app_ids[1], "worker_retrieve Response result" +
            " applicationTypeId[1] doesn't match")
        self.assertEqual(
            res['result']['details'], json.loads(self.__details),
            "worker_retrieve Response result details doesn't match")
        self.assertEqual(
            res['result']['status'], self.__status.value,
            "worker_retrieve Response result status doesn't match")

    def test_worker_lookup(self):
        req_id = 16
        logging.info(
            'Calling testworker_lookup with\n worker type %d\n org_id %s\n ' +
            'application ids %s\n',
            self.__worker_type.value, self.__org_id, self.__app_ids)
        res = self.__worker_registry_wrapper.worker_lookup(
            self.__worker_type, self.__org_id, self.__app_ids, req_id)
        logging.info('Result: %s\n', res)
        self.assertEqual(
            res['id'], req_id, "worker_lookup Response id doesn't match")
        self.assertEqual(
            res['result']['totalCount'], 1,
            "worker_lookup Response totalCount doesn't match")
        self.assertEqual(
            res['result']['lookupTag'], self.__worker_id,
            "worker_lookup Response lookup tag doesn't match")
        self.assertEqual(
            res['result']['ids'][0], self.__worker_id,
            "worker_lookup Response worker id doesn't match")

    def test_worker_lookup_next(self):
        req_id = 17
        logging.info(
            'Calling worker_lookup_next with\n worker type %d\n' +
            ' org_id %s\n app_ids %s\n lookUpTag %s\n',
            self.__worker_type.value, self.__org_id, self.__app_ids,
            "sample tag")
        res = self.__worker_registry_wrapper.worker_lookup_next(
            "sample tag", self.__worker_type, self.__org_id, self.__app_ids,
            req_id)
        logging.info('Result: %s\n', res)
        self.assertEqual(
            res['id'], req_id, "worker_lookup_next Response id doesn't match")
        """
        self.assertEqual(
            res['result']['totalCount'], 0,
            "worker_lookup_next Response totalCount doesn't match")
        self.assertEqual(
            res['result']['lookupTag'], '',
            "worker_lookup_next Response lookup tag doesn't match")
        self.assertEqual(
            res['result']['ids'][0], '0x0000a3',
            "worker_lookup_next Response worker id doesn't match")
        """


def main():
    logging.info("Running test cases...\n")
    tcf_home = environ.get("TCF_HOME", "../../")
    test = TestWorkerRegistryJRPCImpl(
        tcf_home + "/sdk/avalon_sdk/" +
        "tcf_connector.toml")
    test.test_worker_register()
    test.test_worker_update()
    test.test_worker_set_status()
    test.test_worker_retrieve()
    test.test_worker_lookup()
    test.test_worker_lookup_next()


if __name__ == '__main__':
    main()
