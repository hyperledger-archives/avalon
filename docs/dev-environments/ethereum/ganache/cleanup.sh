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

check_and_exit()
{
    if [ $? -ne 0 ]
    then
        echo "Script failed."
        exit 1
    else
        echo "Done."
    fi
}

echo ""
echo "=================================================="
echo "STEP 1 :: Stop Ganache cli and destroy container"
echo "=================================================="
docker stop local-ganache
docker rm local-ganache
check_and_exit

echo ""
echo "=================================================="
echo "STEP 2 :: Stop truffle setup container and destroy"
echo "=================================================="
docker-compose -f ./docker-compose-truffle.yaml down
check_and_exit

echo ""
echo "=================================================="
echo "STEP 3 :: Delete ganache network"
echo "=================================================="
docker network rm ganache_local_net

echo ""
echo "=================================================="
echo "STEP 4 :: Delete truffle project from host"
echo "=================================================="
sudo rm -rf ./my_project
check_and_exit

echo "Cleanup Successful!!"
echo ""
