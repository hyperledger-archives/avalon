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


class ValidChainCodeMethods():
    """
    Valid chain code methods has all fabric chain code names
    and their API names it supports along with their arguments
    """

    def __init__(self):
        self._cc_methods = {
            "order": {
                "workOrderSubmit": {
                    "callparams": [
                        {"type": "bytes32", "name": "workOrderId"},
                        {"type": "bytes32", "name": "workerId"},
                        {"type": "bytes32", "name": "requesterId"},
                        {"type": "string", "name": "workOrderRequest"}],
                    "isQuery": False
                },
                "workOrderComplete": {
                    "callparams": [
                        {"type": "bytes32", "name": "workOrderId"},
                        {"type": "string", "name": "workOrderResponse"}],
                    "isQuery": False
                },
                "workOrderGet": {
                    "callparams": [
                        {"type": "bytes32", "name": "workOrderId"}],
                    "isQuery": True
                }
            },
            "receipt": {
                "workOrderReceiptCreate": {
                    "callparams": [
                       {"type": "bytes32", "name": "workOrderId"},
                       {"type": "bytes32", "name": "workerId"},
                       {"type": "bytes32", "name": "workerServiceId"},
                       {"type": "bytes32", "name": "requesterId"},
                       {"type": "uint256", "name": "receiptCreateStatus"},
                       {"type": "bytes", "name": "workOrderRequestHash"}],
                    "isQuery": False
                },
                "workOrderReceiptRetrieve": {
                    "callparams": [
                        {"type": "bytes32", "name": "workOrderId"}],
                    "isQuery": True
                },
                "workOrderReceiptLookUp": {
                    "callparams": [
                        {"type": "bytes32", "name": "workerServiceId"},
                        {"type": "bytes32", "name": "workerId"},
                        {"type": "bytes32", "name": "requesterId"},
                        {"type": "uint256", "name": "receiptStatus"}],
                    "isQuery": True
                },
                "workOrderReceiptLookUpNext": {
                    "callparams": [
                        {"type": "bytes32", "name": "workerServiceId"},
                        {"type": "bytes32", "name": "workerId"},
                        {"type": "bytes32", "name": "requesterId"},
                        {"type": "uint256", "name": "receiptStatus"},
                        {"type": "bytes", "name": "lastLookUpTag"}],
                    "isQuery": True
                },
                "query": {
                    "callparams": [
                        {"type": "bytes32", "name": "workOrderReceiptId"}],
                    "isQuery": True
                }
            },
            "worker": {
                "workerRegister": {
                    "callparams": [
                      {"type": "bytes32", "name": "workerID"},
                      {"type": "uint256", "name": "workerType"},
                      {"type": "bytes32", "name": "organizationID"},
                      {"type": "bytes32[]", "name": "applicationTypeId"},
                      {"type": "string", "name": "details"}],
                    "isQuery": False
                },
                "workerUpdate": {
                    "callparams": [
                        {"type": "bytes32", "name": "workerID"},
                        {"type": "string", "name": "details"}],
                    "isQuery": False
                },
                "workerSetStatus": {
                    "callparams": [
                        {"type": "bytes32", "name": "workerID"},
                        {"type": "uint256", "name": "status"}],
                    "isQuery": False
                },
                "workerLookUp": {
                    "callparams": [
                        {"type": "uint256", "name": "workerType"},
                        {"type": "bytes32", "name": "organizationId"},
                        {"type": "bytes32", "name": "applicationTypeId"}],
                    "isQuery": True
                },
                "workerLookUpNext": {
                    "callparams": [
                        {"type": "uint256", "name": "workerType"},
                        {"type": "bytes32", "name": "organizationId"},
                        {"type": "bytes32", "name": "applicationTypeId"},
                        {"type": "bytes", "name": "newLookUpTag"}],
                    "isQuery": True
                },
                "workerRetrieve": {
                    "callparams": [
                        {"type": "bytes32", "name": "workerId"}],
                    "isQuery": True
                },
                "query": {
                    "callparams": [
                        {"type": "bytes32", "name": "workerId"}],
                    "isQuery": True
                }
            },
            "registry": {
                "registryAdd": {
                    "callparams": [
                        {"type": "bytes32", "name": "orgID"},
                        {"type": "string", "name": "uri"},
                        {"type": "bytes32", "name": "scAddr"},
                        {"type": "bytes32[]", "name": "appTypeIds"}],
                    "isQuery": False
                },
                "registryUpdate": {
                    "callparams": [
                        {"type": "bytes32", "name": "orgID"},
                        {"type": "string", "name": "uri"},
                        {"type": "bytes32", "name": "scAddr"},
                        {"type": "bytes32[]", "name": "appTypeIds"}],
                    "isQuery": False
                },
                "registrySetStatus": {
                    "callparams": [
                        {"type": "bytes32", "name": "orgID"},
                        {"type": "uint256", "name": "status"}],
                    "isQuery": False
                },
                "registryLookUp": {
                    "callparams": [
                        {"type": "bytes32", "name": "appTypeId"}],
                    "isQuery": True
                },
                "registryLookUpNext": {
                    "callparams": [
                        {"type": "bytes32", "name": "appTypeId"},
                        {"type": "bytes", "name": "newLookUpTag"}],
                    "isQuery": True
                },
                "registryRetrieve": {
                    "callparams": [
                        {"type": "bytes32", "name": "workerId"}],
                    "isQuery": True
                },
                "query": {
                    "callparams": [
                        {"type": "bytes32", "name": "registryId"}],
                    "isQuery": True
                }
            }
        }

    def get_valid_cc_methods(self):
        return self._cc_methods
