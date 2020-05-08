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


from os import urandom, path, environ, getcwd
import errno
import logging
import json
import toml
import unittest
from utility.file_utils import read_json_file

from avalon_sdk.ethereum.ethereum_work_order \
    import EthereumWorkOrderProxyImpl, \
    is_wo_id_in_event, _is_valid_work_order_json
from avalon_sdk.worker.worker_details import WorkerType, WorkerStatus
from utility.hex_utils import hex_to_utf8, pretty_ids


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class TestEthereumWorkOrderProxyImpl(unittest.TestCase):
    def __init__(self, config_file):
        super(TestEthereumWorkOrderProxyImpl, self).__init__()
        if not path.isfile(config_file):
            raise FileNotFoundError("File not found at path: {0}".format(
                path.realpath(config_file)))
        try:
            with open(config_file) as fd:
                self.__config = toml.load(fd)
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise Exception("Could not open config file: %s", e)
        self.__eth_conn = EthereumWorkOrderProxyImpl(self.__config)

    def test_work_order_submit_positive(self):
        read_json = read_json_file(
            "work_order_req.json", ["./"])
        wo_id = urandom(32).hex()
        worker_id = urandom(32).hex()
        requester_id = urandom(32).hex()

        wo_req = json.loads(read_json)["params"]
        wo_req["workOrderId"] = wo_id
        wo_req["workerId"] = worker_id
        wo_req["requesterId"] = requester_id

        result = self.__eth_conn.work_order_submit(wo_id,
                                                   worker_id,
                                                   requester_id,
                                                   json.dumps(wo_req))
        self.assertEqual(result, 0, "Work order should pass")

    def test_work_order_submit_mismatch(self):
        read_json = read_json_file(
            "work_order_req.json", ["./"])
        wo_id = urandom(32).hex()
        worker_id = urandom(32).hex()
        requester_id = urandom(32).hex()

        wo_req = json.loads(read_json)["params"]
        wo_req["workOrderId"] = wo_id
        wo_req["workerId"] = urandom(32).hex()  # Different workerId
        wo_req["requesterId"] = requester_id

        result = self.__eth_conn.work_order_submit(wo_id,
                                                   worker_id,
                                                   requester_id,
                                                   json.dumps(wo_req))
        self.assertEqual(result, 1, "Work order submission should fail")

    def test_work_order_get_result(self):
        pass

    def test_work_order_complete(self):
        """
        This function verifies if work order complete function
        succeeds when the in work order execution is done.
        """
        read_json = read_json_file(
            "work_order_get_result.json", ["./"])
        wo_id = urandom(32).hex()

        result = self.__eth_conn.work_order_complete(wo_id,
                                                     read_json)
        self.assertEqual(
            result, 0, "Work order result submission should succeed")

    def test_work_order_complete_error(self):
        """
        This function verifies if work order complete function
        succeeds when there is an error in work order execution.
        """
        read_json = read_json_file(
            "work_order_get_result_error.json", ["./"])
        wo_id = urandom(32).hex()

        result = self.__eth_conn.work_order_complete(wo_id,
                                                     read_json)
        self.assertEqual(
            result, 0, "Work order result submission should succeed")

    def test_is_wo_id_in_event_positive(self):
        """
        This case mocks an event and verifies the wo_id_in_event function
        for a positive result.
        """
        response_event = {"args": {"workOrderId": b'g7V\xc7A',
                                   "workOrderResponse":
                                   '{"result":{"workloadId":"6563686f2",'
                                   + '"workOrderId": "673756c741",'
                                   + '"workerId":"3686f2d72"},"errorCode": 0}'
                                   }}
        self.assertTrue(is_wo_id_in_event(response_event, wo_id="673756c741"))

    def test_is_wo_id_in_event_wo_id_not_matched(self):
        """
        This case mocks an event and verifies the wo_id_in_event function
        for a negative result. The wo_id does not match.
        """
        response_event = {"args": {"workOrderId": b'g7V\xc7A',
                                   "workOrderResponse":
                                   '{"result":{"workloadId":"6563686f2",'
                                   + '"workOrderId":"673756c74",'
                                   + '"workerId": "3686f2d72"},'
                                   + '"errorCode": 0}'}}
        self.assertFalse(is_wo_id_in_event(
            response_event, wo_id="abcabcabcbc"))

    def test_is_wo_id_in_event_error_result(self):
        """
        This case mocks an event and verifies the wo_id_in_event function
        for a positive result. The event has an error response from
        work order execution.
        """
        response_event = {"args": {"workOrderId": b'g7V\xc7A',
                                   "workOrderResponse": '{"error":{"code":2,'
                                   + '"message": "Indata is empty"},'
                                   + '"errorCode": 2}'}}
        self.assertTrue(is_wo_id_in_event(response_event, wo_id="673756c741"))

    def test_is_wo_id_in_event_no_wo_id(self):
        response_event = {"args": {"workOrderResponse": '{"error":{"code":2,'
                                   + '"message": "Indata is empty"},'
                                   + '"errorCode": 2}'}}
        self.assertFalse(is_wo_id_in_event(response_event, wo_id="673756c741"))

    def test_is_valid_work_order_json(self):
        wo_request = '{"workOrderId":"abcabcabc123123123",'\
                     + '"workerId":"bcdbcdbcd123123123",'\
                     + '"requesterId":"cdecdecde123123123"}'
        self.assertTrue(_is_valid_work_order_json(
            "abcabcabc123123123", "bcdbcdbcd123123123",
            "cdecdecde123123123", wo_request))


def main():
    logging.info("Running test cases...")
    tcf_home = environ.get("TCF_HOME", "../../../../")
    test = TestEthereumWorkOrderProxyImpl(
        tcf_home +
        "/sdk/avalon_sdk/" + "tcf_connector.toml")
    test.test_work_order_submit_positive()
    test.test_work_order_submit_mismatch()
    test.test_work_order_complete()
    test.test_work_order_complete_error()
    test.test_work_order_get_result()
    test.test_is_valid_work_order_json()
    test.test_is_wo_id_in_event_positive()
    test.test_is_wo_id_in_event_wo_id_not_matched()
    test.test_is_wo_id_in_event_error_result()
    test.test_is_wo_id_in_event_no_wo_id()
    # Not properly defined in EEA spec. To be enabled as feature is enabled.
    # test.test_worker_lookup_next()


if __name__ == "__main__":
    main()
