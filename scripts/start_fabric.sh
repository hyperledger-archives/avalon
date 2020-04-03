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
WORK_DIR=~/mywork
MINIFAB=$WORK_DIR/minifab
# Minifab url for 0.1.0 stable version
MINIFAB_URL=https://tinyurl.com/s8fmmvx

# Default chaincode path is different for 1.4.4 and 2.0
DEFAULT_CHAIN_CODE_PATH=""
if expr $FABRIC_VERSION '=' 1.4.4>/dev/null; then
    DEFAULT_CHAIN_CODE_PATH=/opt/gopath/src/github.com/chaincode
elif expr $FABRIC_VERSION '=' 2.0>/dev/null; then
    DEFAULT_CHAIN_CODE_PATH=/go/src/github.com/chaincode
fi

check_if_cc_artifacts_exists()
{
    artifact_path="$WORK_DIR/vars/chaincode"
    if expr $FABRIC_VERSION '=' 1.4.4>/dev/null; then
        # In 1.4.4 go chain code build targets will be
        # in $WORK_DIR/vars/chaincode/<chaincode_name>/go/vendor
        lang="go"
        artifact_name="vendor"
    elif expr $FABRIC_VERSION '=' 2.0>/dev/null; then
        # In 2.0 chain code build targets will be in
        # $WORK_DIR/vars/chaincode/<chaincode_name>/
        # <chaincode_name>_go_<chain_code_version>.tar.gz
        lang=""
        artifact_name="_go_$CHAIN_CODE_VERSION.tar.gz"
    fi
    exists=1
    for i in "registry" "worker" "order" "receipt" ;
    do
        chaincode_artifact="$artifact_path/$i/$lang/$artifact_name"
        if [ -f "$chaincode_artifact" ]; then
            continue
        else
            exists=0
            break
        fi
    done
    return $exists
}

if [ -f "$MINIFAB" ]; then
    echo "minifab is already installed in $MINIFAB"
else
    echo "Installing minifab in $MINIFAB"
    mkdir -p $WORK_DIR && cd $WORK_DIR && curl -o minifab -sL $MINIFAB_URL && chmod +x minifab
fi

if [[ ! -v TCF_HOME ]]; then
    echo "TCF_HOME is not set"
    exit
fi

cd $WORK_DIR
export PATH=$WORK_DIR/:$PATH

if [[ $1 != "" && $1 == "stop" ]]; then
    minifab down
elif [[ $1 != "" && $1 == "start" ]]; then
    # If we copy chaincode files everytime, go build take more time to generate
    # build artifact.
    check_if_cc_artifacts_exists
    exist=$?
    if [ "$exist" -eq "1" ]; then
        echo "Chain codes are built and use existing built artifacts"
    else
        echo "Copying avalon fabric chaincodes to $WORK_DIR/vars/chaincode"
        mkdir -p ./vars/chaincode
        cp -R $TCF_HOME/sdk/avalon_sdk/fabric/chaincode/* vars/chaincode/
    fi

    # If already fabric network up and running skip start again.
    if [[ ! $(docker ps --format '{{.Names}}' |grep "peer*") ]]; then
        # Start the fabric containers peers, orderers, cas
        minifab up -i $FABRIC_VERSION
        # Create network profile file for avalon to use
        # profile file is generated in $WORK_DIR/vars/profiles/
        minifab profilegen
        # Create blockmark file with block number 0
        # This file will be used by generic client to
        # register event
        echo "0">$WORK_DIR/vars/blockmark
        # Delete the old blockmark files.
        rm -rf $TCF_HOME/blockchain_connector/blockmark
        rm -rf $TCF_HOME/examples/apps/generic_client/blockmark
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
else
    echo "Invalid input: $1"
    echo "Valid inputs are 'start' or 'stop'"
fi
