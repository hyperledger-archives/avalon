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

exit_status=0
function log_error()
{
    echo "[Error]: " ${*}
    exit_status=1
}

echo ""
echo "=================================================="
echo "STEP 1 :: Stop Ganache cli and destroy container"
echo "=================================================="

# Check if the containers do not exist at all. If they do not exist, cleanup should not fail.
if [ ! -z "$(docker ps -aq -f status=running -f name=local-ganache)" ];
then 
    docker stop local-ganache || log_error "Failed to stop Ganache container"
fi
echo "Done"

if [ ! -z "$(docker ps -aq -f name=local-ganache)" ]; 
then 
    docker rm local-ganache || log_error "Failed to delete Ganache container"
fi
echo "Done"

echo ""
echo "=================================================="
echo "STEP 2 :: Stop truffle setup container and destroy"
echo "=================================================="

docker-compose -f docker-compose-truffle.yaml down || log_error "Failed to cleanup truffle setup"

echo "Done"

echo ""
echo "=================================================="
echo "STEP 3 :: Delete ganache network"
echo "=================================================="

# Check if the network does not exist at all. If it does not exist, cleanup should not fail.  
if [ ! -z "$(docker network ls -q -f name=ganache_local_net)" ];
then
    docker network rm ganache_local_net || log_error "Failed to cleanup docker network for Ganache"
fi
echo "Done"

echo ""
if [ $exit_status -eq 0 ]; then
    echo "Cleanup successful!!"
else
    echo "Cleanup failed!!"
fi
echo ""
