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

# Since fabric 1.4.4 is takes less time to instantiate the chaincodes
# default fabric version is set to 1.4.4
FABRIC_VERSION=1.4.4
CHAIN_CODE_VERSION=1.0
MINIFAB=~/mywork/minifab
WORK_DIR=~/mywork

# Default chaincode path is different for 1.4.4 and 2.0
DEFAULT_CHAIN_CODE_PATH=""
if expr $FABRIC_VERSION '=' 1.4.4>/dev/null; then
    DEFAULT_CHAIN_CODE_PATH=/opt/gopath/src/github.com/chaincode
elif expr $FABRIC_VERSION '=' 2.0>/dev/null; then
    DEFAULT_CHAIN_CODE_PATH=/go/src/github.com/chaincode
fi

check_if_cc_artifacts_exists()
{
    chain_codes=("registry", "worker", "order", "receipt")
    artifact_path="$WORK_DIR/vars/chaincode/"
    if expr $FABRIC_VERSION '=' 1.4.4>/dev/null; then
        # In 1.4.4 go chain code build targets will be
        # in $WORK_DIR/vars/chaincode/<chaincode_name>/go/vendor
        lang="/go/"
        artifact_name="vendor"
    elif expr $FABRIC_VERSION '=' 2.0>/dev/null; then
        # In 2.0 chain code build targets will be in
        # $WORK_DIR/vars/chaincode/<chaincode_name>/
        # <chaincode_name>_go_<chain_code_version>.tar.gz
        lang=""
        artifact_name="_go_$CHAIN_CODE_VERSION.tar.gz"
    fi
    for i in $chain_codes
    do
        chaincode_artifact=$artifact_path$i$lang$artifact_name
        if [ ! -f $chaincode_artifact ]; then
            return 0
        else
            continue
        fi
    done
    return 1
}
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
# If we copy chaincode files everytime, go build take more time to generate
# build artifcat.
if check_if_cc_artifacts_exists; then
    echo "Chain codes are built and use existing built artifacts"
else
    mkdir -p ./vars/chaincode
    cp -R $TCF_HOME/sdk/avalon_sdk/fabric/chaincode/* vars/chaincode/
fi

# If already fabric network up and running skip start again.
if [[ ! $(docker ps --format '{{.Names}}' |grep "peer*") ]]; then
    minifab up -i $FABRIC_VERSION
    # Create blockmark file with block number 0
    # This file will be used by generic client to
    # register event
    echo "0">$WORK_DIR/vars/blockmark
    # Since cli container is creating go package by downloading
    # go external dependencies and it need proxy configurations
    # to access internet. Passing proxy settings for cli.
    docker rm -f cli
    docker run -dit --name cli --network minifab -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd)/vars:/vars \
-v $(pwd)/vars/chaincode:$DEFAULT_CHAIN_CODE_PATH \
-e "http_proxy=$http_proxy" -e "https_proxy=$https_proxy" \
-e "no_proxy=$no_proxy" \
-e "HTTP_PROXY=$http_proxy" -e "HTTPS_PROXY=$https_proxy" \
-e "NO_PROXY=$no_proxy" \
hyperledger/fabric-tools:$FABRIC_VERSION
fi
# If chaincode already instantiated then don't start it again.
if [[ ! $(docker ps --format '{{.Names}}' |grep "dev-*" |grep "registry_*") ]]; then
    echo "Installing and instantiating registry chain code.."
    minifab install,approve,instantiate -n registry -v $CHAIN_CODE_VERSION
fi
if [[ ! $(docker ps --format '{{.Names}}' |grep "dev-*" |grep "worker_*") ]]; then
    echo "Installing and instantiating worker chain code.."
    minifab install,approve,instantiate -n worker -v $CHAIN_CODE_VERSION
fi
if [[ ! $(docker ps --format '{{.Names}}' |grep "dev-*" |grep "order_*") ]]; then
    echo "Installing and instantiating order chain code.."
    minifab install,approve,instantiate -n order -v $CHAIN_CODE_VERSION
fi
if [[ ! $(docker ps --format '{{.Names}}' |grep "dev-*" |grep "receipt_*") ]]; then
    echo "Installing and instantiating receipt chain code.."
    minifab install,approve,instantiate -n receipt -v $CHAIN_CODE_VERSION
fi
echo "Started fabric network..."
docker ps --format '{{.Names}}'

