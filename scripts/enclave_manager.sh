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

enclave_manager="${TCF_HOME}/examples/enclave_manager/tcf_enclave_manager/enclave_manager.py"

source ${TCF_HOME}/tools/build/_dev/bin/activate

echo "starting enclave manager ..."
python3 $enclave_manager
