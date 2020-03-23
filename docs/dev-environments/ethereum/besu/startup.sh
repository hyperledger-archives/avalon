#!/bin/bash
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


function error_exit()
{
    echo "[Error]: " ${*}
    exit 1
}

echo ""
echo "========================================================="
echo "STEP 1 :: Bring up HL Besu nodes"
echo "========================================================="

docker-compose up -d || error_exit "Failed to bring up Besu network"
echo "Done"

echo ""
echo "========================================================="
echo "STEP 3 :: Initialize truffle project and deploy contracts"
echo "========================================================="
docker-compose -f docker-compose-truffle.yaml up \
|| error_exit "Failed to initialize truffle or deploy contracts"
echo "Done"

echo ""
echo "Contract deployment successful!!"
echo ""
