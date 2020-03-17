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
echo "====================================================="
echo "STEP 1 :: Stop HL Besu network and destroy containers"
echo "====================================================="
docker-compose down
check_and_exit

echo ""
echo "====================================================="
echo "STEP 2 :: Stop truffle setup container and destroy"
echo "====================================================="
docker-compose -f docker-compose-truffle.yaml down
check_and_exit

echo ""
echo "====================================================="
echo "STEP 3 :: Delete persistent blockchain data"
echo "====================================================="
# To clean up all persistent data for a running node
cd ./besu/node1
sudo rm -rf caches database DATABASE_METADATA.json
check_and_exit
cd ../node2
sudo rm -rf caches database DATABASE_METADATA.json
check_and_exit
cd ../../

echo ""
echo "====================================================="
echo "STEP 4 :: Delete truffle project from host"
echo "====================================================="
sudo rm -rf ./my_project
check_and_exit

echo ""
echo "====================================================="
echo "STEP 5 :: Delete event marker from Avalon"
echo "====================================================="
rm -f $TCF_HOME/blockchain_connector/bookmark $TCF_HOME/examples/apps/generic_client/bookmark
check_and_exit

echo "Cleanup Successful!!"
echo ""
