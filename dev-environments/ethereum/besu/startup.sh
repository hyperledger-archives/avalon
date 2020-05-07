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
function error_exit()
{
    echo "[Error]: " ${*}
    exit_status=1
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

# Check if TCF_HOME is defined and current working directory
# is a subtree of TCF_HOME
if [[ -z "$TCF_HOME" ]] || [[ `pwd` != "$TCF_HOME"* ]];
then
    error_exit "TCF_HOME environment variable not defined appropriately. Please check."
fi

# Verify if contract deployments are successful else log error
docker-compose -f docker-compose-truffle.yaml up --exit-code-from truffle-envt-besu\
    || error_exit "Failed to initialize truffle or deploy contracts"
echo "Done"

echo ""
if [ $exit_status -eq 0 ];
then
    echo "Contract deployment successful!!"
else
    echo "Contract deployment failed!!"
fi
echo ""
