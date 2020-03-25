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
echo "STEP 1 :: Create specific network for Ganache setup"
echo "========================================================="

docker network create -d bridge --subnet=172.18.0.0/16 ganache_local_net \
|| error_exit "Failed to create docker network for Ganache"
echo "Done"

echo ""
echo "========================================================="
echo "STEP 2 :: Start Ganache cli locally"
echo "========================================================="

docker run -d -p 8545:8545 --network=ganache_local_net --hostname=local-ganache \
--name=local-ganache trufflesuite/ganache-cli:v6.9.1 || error_exit "Failed to start Ganache container"
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
