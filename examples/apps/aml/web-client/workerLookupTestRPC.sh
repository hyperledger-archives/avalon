#!/bin/bash

# Copyright 2019 Banco Santander S.A.
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

IP=localhost

curl -v -X POST -H "Content-Type: application/json" -d '"{\"jsonrpc\": \"2.0\", \"method\": \"WorkerLookUp\", \"id\": 1, \"params\": {\"workerType\": 1, \"workOrderId\": null}}"' http://$IP:1947
