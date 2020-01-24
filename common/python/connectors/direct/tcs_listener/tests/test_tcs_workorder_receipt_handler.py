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

import unittest
from unittest.mock import Mock
from connectors.direct.tcs_listener.tcs_workorder_receipt_handler import TCSWorkOrderReceiptHandler

class TestTCSWorkOrderReceiptHandler(unittest.TestCase):

# ------------------------------------------------------------------------------------------------

    def test_lookup_1(self):
        """
        Test to verify page and lookupTag for next page
        """
        kv_helper = Mock()
        kv_helper.lookup.side_effect = self.handle_lookup_1
        kv_helper.get.side_effect = self.handle_get_1
        workorder_receipt_handler = TCSWorkOrderReceiptHandler(kv_helper, 2)
        response = workorder_receipt_handler.WorkOrderReceiptLookUp()
        self.assertEquals( response, {'totalCount': 2, 'lookupTag': 'workorder3', 'ids': ['workorder1', 'workorder2']} )

    def handle_lookup_1(self, *args):
        if args[0] == "wo-receipts":
            return ["workorder1", "workorder2", "workorder3"]

    def handle_get_1(self, *args):
        if args[1] == "workorder1":
            return '{"workerServiceId": "10", "workerId": "0x111111", "requesterId": "0x1111", "requestCreateStatus": 1}'
        if args[1] == "workorder2":
            return '{"workerServiceId": "20", "workerId": "0x211111", "requesterId": "0x2111", "requestCreateStatus": 1}'
        if args[1] == "workorder3":
            return '{"workerServiceId": "30", "workerId": "0x311111", "requesterId": "0x3111", "requestCreateStatus": 1}'

# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
    def test_lookup_2(self):
        """
        Test to verify last page
        """
        kv_helper = Mock()
        kv_helper.lookup.side_effect = self.handle_lookup_2
        kv_helper.get.side_effect = self.handle_get_2
        workorder_receipt_handler = TCSWorkOrderReceiptHandler(kv_helper, 2)
        response = workorder_receipt_handler.WorkOrderReceiptLookUp()
        self.assertEquals( response, {'totalCount': 2, 'lookupTag': 0, 'ids': ['workorder1', 'workorder2']} )

    def handle_lookup_2(self, *args):
        if args[0] == "wo-receipts":
            return ["workorder1", "workorder2"]

    def handle_get_2(self, *args):
        if args[1] == "workorder1":
            return '{"workerServiceId": "10", "workerId": "0x111111", "requesterId": "0x1111", "requestCreateStatus": 1}'
        if args[1] == "workorder2":
            return '{"workerServiceId": "20", "workerId": "0x211111", "requesterId": "0x2111", "requestCreateStatus": 1}'

# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
    def test_lookup_3(self):
        """
        Test to verify incomplete page
        """
        kv_helper = Mock()
        kv_helper.lookup.side_effect = self.handle_lookup_3
        kv_helper.get.side_effect = self.handle_get_3
        workorder_receipt_handler = TCSWorkOrderReceiptHandler(kv_helper, 2)
        response = workorder_receipt_handler.WorkOrderReceiptLookUp()
        self.assertEquals( response, {'totalCount': 1, 'lookupTag': 0, 'ids': ['workorder1']} )

    def handle_lookup_3(self, *args):
        if args[0] == "wo-receipts":
            return ["workorder1", "workorder2"]

    def handle_get_3(self, *args):
        if args[1] == "workorder1":
            return '{"workerServiceId": "10", "workerId": "0x111111", "requesterId": "0x1111", "requestCreateStatus": 1}'

# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
    def test_lookup_next_1(self):
        """
        Test to verify page and lookupTag for next page
        """
        kv_helper = Mock()
        kv_helper.lookup.side_effect = self.handle_lookup_4
        kv_helper.get.side_effect = self.handle_get_4
        workorder_receipt_handler = TCSWorkOrderReceiptHandler(kv_helper, 2)
        response = workorder_receipt_handler.WorkOrderReceiptLookUpNext(lastLookUpTag='workorder1')
        self.assertEquals( response, {'totalCount': 2, 'lookupTag': 'workorder3', 'ids': ['workorder1', 'workorder2']} )

    def handle_lookup_4(self, *args):
        if args[0] == "wo-receipts":
            return ["workorder1", "workorder2", "workorder3"]

    def handle_get_4(self, *args):
        if args[1] == "workorder1":
            return '{"workerServiceId": "10", "workerId": "0x111111", "requesterId": "0x1111", "requestCreateStatus": 1}'
        if args[1] == "workorder2":
            return '{"workerServiceId": "20", "workerId": "0x211111", "requesterId": "0x2111", "requestCreateStatus": 1}'
        if args[1] == "workorder3":
            return '{"workerServiceId": "30", "workerId": "0x311111", "requesterId": "0x3111", "requestCreateStatus": 1}'

# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

    def test_lookup_next_2(self):
        """
        Test to verify last page
        """
        kv_helper = Mock()
        kv_helper.lookup.side_effect = self.handle_lookup_5
        kv_helper.get.side_effect = self.handle_get_5
        workorder_receipt_handler = TCSWorkOrderReceiptHandler(kv_helper, 2)
        response = workorder_receipt_handler.WorkOrderReceiptLookUpNext(lastLookUpTag='workorder2')
        self.assertEquals( response, {'totalCount': 2, 'lookupTag': 0, 'ids': ['workorder2', 'workorder3']} )

    def handle_lookup_5(self, *args):
        if args[0] == "wo-receipts":
            return ["workorder1", "workorder2", "workorder3"]

    def handle_get_5(self, *args):
        if args[1] == "workorder1":
            return '{"workerServiceId": "10", "workerId": "0x111111", "requesterId": "0x1111", "requestCreateStatus": 1}'
        if args[1] == "workorder2":
            return '{"workerServiceId": "20", "workerId": "0x211111", "requesterId": "0x2111", "requestCreateStatus": 1}'
        if args[1] == "workorder3":
            return '{"workerServiceId": "30", "workerId": "0x311111", "requesterId": "0x3111", "requestCreateStatus": 1}'

# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

    def test_lookup_next_3(self):
        """
        Test to verify incomplete page
        """
        kv_helper = Mock()
        kv_helper.lookup.side_effect = self.handle_lookup_6
        kv_helper.get.side_effect = self.handle_get_6
        workorder_receipt_handler = TCSWorkOrderReceiptHandler(kv_helper, 2)
        response = workorder_receipt_handler.WorkOrderReceiptLookUpNext(lastLookUpTag='workorder2')
        self.assertEquals( response, {'totalCount': 1, 'lookupTag': 0, 'ids': ['workorder2']} )

    def handle_lookup_6(self, *args):
        if args[0] == "wo-receipts":
            return ["workorder1", "workorder2"]

    def handle_get_6(self, *args):
        if args[1] == "workorder1":
            return '{"workerServiceId": "10", "workerId": "0x111111", "requesterId": "0x1111", "requestCreateStatus": 1}'
        if args[1] == "workorder2":
            return '{"workerServiceId": "20", "workerId": "0x211111", "requesterId": "0x2111", "requestCreateStatus": 1}'

# ------------------------------------------------------------------------------------------------

