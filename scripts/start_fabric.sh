#! /bin/bash

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

MINIFAB=~/mywork/minifab
if [ -f "$MINIFAB" ]; then
    echo "minifab is already installed in ~/mywork"
else
    mkdir -p ~/mywork && cd ~/mywork && curl -o minifab -sL https://tinyurl.com/twrt8zv && chmod +x minifab
fi

if [[ ! -v TCF_HOME ]]; then
    echo "TCF_HOME is not set"
    exit
fi
cd ~/mywork
export PATH=~/mywork/:$PATH
minifab cleanup
mkdir -p ./vars/chaincode
cp -R $TCF_HOME/sdk/avalon_sdk/fabric/chaincode/* vars/chaincode/
minifab up
# Since cli container is creating go package by downloading
# go external dependencies and it need proxy configurations
# to access internet. Passing proxy settings for cli.
docker rm -f cli
docker run -dit --name cli --network minifab -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd)/vars:/vars \
-v $(pwd)/vars/chaincode:/go/src/github.com/chaincode \
-e "http_proxy=$http_proxy" -e "https_proxy=$https_proxy" \
-e "no_proxy=$no_proxy,localhost,orderer3.example.com,orderer2.example.com,orderer1.example.com,peer2.org1.example.com,peer1.org1.example.com,peer2.org0.example.com,peer1.org0.example.com" \
-e "HTTP_PROXY=$http_proxy" -e "HTTPS_PROXY=$https_proxy" \
-e "NO_PROXY=$no_proxy,localhost,orderer3.example.com,orderer2.example.com,orderer1.example.com,peer2.org1.example.com,peer1.org1.example.com,peer2.org0.example.com,peer1.org0.example.com" \
hyperledger/fabric-tools:2.0
echo "Installing and instantiating registry chain code.."
minifab install,approve,instantiate -n registry -v 1.0
echo "Installing and instantiating worker chain code.."
minifab install,approve,instantiate -n worker -v 1.0
echo "Installing and instantiating order chain code.."
minifab install,approve,instantiate -n order -v 1.0
echo "Installing and instantiating receipt chain code.."
minifab install,approve,instantiate -n receipt -v 1.0