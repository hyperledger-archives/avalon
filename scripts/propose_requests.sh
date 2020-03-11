#! /bin/bash

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

ClientDir=/project/avalon/examples/apps/generic_client

python3 ${ClientDir}/generic_client.py --uri "http://avalon-listener:${1:-1947}" \
 --workload_id "heart-disease-eval" \
 --in_data "Data: 25 10 1 67  102 125 1 95 5 10 1 11 36 1" -o
    
