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
from connectors.direct.tcs_listener.tcs_worker_registry_handler import TCSWorkerRegistryHandler

class TestTCSWorkerRegistryHandler(unittest.TestCase):

# ------------------------------------------------------------------------------------------------

    def test_lookup_1(self):
        """
        Test to verify page and lookupTag for next page
        """
        kv_helper = Mock()
        kv_helper.lookup.side_effect = self.handle_lookup_1
        kv_helper.get.side_effect = self.handle_get_1
        worker_reg_handler = TCSWorkerRegistryHandler(kv_helper, 2)
        response = worker_reg_handler.WorkerLookUp()
        self.assertEquals( response, {'totalCount': 2, 'lookupTag': 'worker3', 'ids': ['worker1', 'worker2']} )

    def handle_lookup_1(self, *args):
        if args[0] == "registries":
            return []
        if args[0] == "workers":
            return ["worker1", "worker2", "worker3"]

    def handle_get_1(self, *args):
        if args[1] == "worker1":
            return '{"workerType": 1, "organizationId": "aabbcc1234ddeeff", "applicationTypeId": "aaaa22bb33cc44dd"}'
        if args[1] == "worker2":
            return '{"workerType": 1, "organizationId": "bbbbcc1234ddeeff", "applicationTypeId": "bbaa22bb33cc44dd"}'
        if args[1] == "worker3":
            return '{"workerType": 1, "organizationId": "ccbbcc1234ddeeff", "applicationTypeId": "ccaa22bb33cc44dd"}'

# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

    def test_lookup_2(self):
        """
        Test to verify last page
        """
        kv_helper = Mock()
        kv_helper.lookup.side_effect = self.handle_lookup_2
        kv_helper.get.side_effect = self.handle_get_2
        worker_reg_handler = TCSWorkerRegistryHandler(kv_helper, 2)
        response = worker_reg_handler.WorkerLookUp()
        self.assertEquals( response, {'totalCount': 2, 'lookupTag': 0, 'ids': ['worker1', 'worker2']} )

    def handle_lookup_2(self, *args):
        if args[0] == "registries":
            return []
        if args[0] == "workers":
            return ["worker1", "worker2"]

    def handle_get_2(self, *args):
        if args[1] == "worker1":
            return '{"workerType": 1, "organizationId": "aabbcc1234ddeeff", "applicationTypeId": "aaaa22bb33cc44dd"}'
        if args[1] == "worker2":
            return '{"workerType": 1, "organizationId": "bbbbcc1234ddeeff", "applicationTypeId": "bbaa22bb33cc44dd"}'

# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

    def test_lookup_3(self):
        """
        Test to verify incomplete page
        """
        kv_helper = Mock()
        kv_helper.lookup.side_effect = self.handle_lookup_3
        kv_helper.get.side_effect = self.handle_get_3
        worker_reg_handler = TCSWorkerRegistryHandler(kv_helper, 2)
        response = worker_reg_handler.WorkerLookUp()
        self.assertEquals( response, {'totalCount': 1, 'lookupTag': 0, 'ids': ['worker1']} )

    def handle_lookup_3(self, *args):
        if args[0] == "registries":
            return []
        if args[0] == "workers":
            return ["worker1"]

    def handle_get_3(self, *args):
        if args[1] == "worker1":
            return '{"workerType": 1, "organizationId": "aabbcc1234ddeeff", "applicationTypeId": "aaaa22bb33cc44dd"}'

# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

    def test_lookup_next_1(self):
        """
        Test to verify page and lookupTag for next page
        """
        kv_helper = Mock()
        kv_helper.lookup.side_effect = self.handle_lookup_4
        kv_helper.get.side_effect = self.handle_get_4
        worker_reg_handler = TCSWorkerRegistryHandler(kv_helper, 2)
        response = worker_reg_handler.WorkerLookUpNext(lookupTag='worker1')
        self.assertEquals( response, {'totalCount': 2, 'lookupTag': 'worker3', 'ids': ['worker1', 'worker2']} )

    def handle_lookup_4(self, *args):
        if args[0] == "registries":
            return []
        if args[0] == "workers":
            return ["worker1", "worker2", "worker3"]

    def handle_get_4(self, *args):
        if args[1] == "worker1":
            return '{"workerType": 1, "organizationId": "aabbcc1234ddeeff", "applicationTypeId": "aaaa22bb33cc44dd"}'
        if args[1] == "worker2":
            return '{"workerType": 1, "organizationId": "bbbbcc1234ddeeff", "applicationTypeId": "bbaa22bb33cc44dd"}'
        if args[1] == "worker3":
            return '{"workerType": 1, "organizationId": "ccbbcc1234ddeeff", "applicationTypeId": "ccaa22bb33cc44dd"}'

# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

    def test_lookup_next_2(self):
        """
        Test to verify last page
        """
        kv_helper = Mock()
        kv_helper.lookup.side_effect = self.handle_lookup_5
        kv_helper.get.side_effect = self.handle_get_5
        worker_reg_handler = TCSWorkerRegistryHandler(kv_helper, 2)
        response = worker_reg_handler.WorkerLookUpNext(lookupTag='worker2')
        self.assertEquals( response, {'totalCount': 2, 'lookupTag': 0, 'ids': ['worker2', 'worker3']} )

    def handle_lookup_5(self, *args):
        if args[0] == "registries":
            return []
        if args[0] == "workers":
            return ["worker1", "worker2", "worker3"]

    def handle_get_5(self, *args):
        if args[1] == "worker1":
            return '{"workerType": 1, "organizationId": "aabbcc1234ddeeff", "applicationTypeId": "aaaa22bb33cc44dd"}'
        if args[1] == "worker2":
            return '{"workerType": 1, "organizationId": "bbbbcc1234ddeeff", "applicationTypeId": "bbaa22bb33cc44dd"}'
        if args[1] == "worker3":
            return '{"workerType": 1, "organizationId": "ccbbcc1234ddeeff", "applicationTypeId": "ccaa22bb33cc44dd"}'

# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

    def test_lookup_next_3(self):
        """
        Test to verify incomplete page
        """
        kv_helper = Mock()
        kv_helper.lookup.side_effect = self.handle_lookup_6
        kv_helper.get.side_effect = self.handle_get_6
        worker_reg_handler = TCSWorkerRegistryHandler(kv_helper, 2)
        response = worker_reg_handler.WorkerLookUpNext(lookupTag='worker2')
        self.assertEquals( response, {'totalCount': 1, 'lookupTag': 0, 'ids': ['worker2']} )

    def handle_lookup_6(self, *args):
        if args[0] == "registries":
            return []
        if args[0] == "workers":
            return ["worker1","worker2"]

    def handle_get_6(self, *args):
        if args[1] == "worker1":
            return '{"workerType": 1, "organizationId": "aabbcc1234ddeeff", "applicationTypeId": "aaaa22bb33cc44dd"}'
        if args[1] == "worker2":
            return '{"workerType": 1, "organizationId": "bbbbcc1234ddeeff", "applicationTypeId": "bbaa22bb33cc44dd"}'

# ------------------------------------------------------------------------------------------------


