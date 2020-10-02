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
FABRIC_VERSION=2.0
CHAIN_CODE_VERSION=1.0
SCRIPT_DIR="$(dirname $(readlink --canonicalize ${BASH_SOURCE}))"
# Minifab url for 0.1.0 stable version
MINIFAB_URL=https://tinyurl.com/s8fmmvx
MINIFAB_INSTALL_DIR=~/.local/bin/
# Command line options
WORK_DIR=$TCF_HOME/mywork
START_FABRIC=0
STOP_FABRIC=0
CLEAN_UP_WORK_DIR=0
EXPOSE_PORTS=

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

while getopts "w:udche" OPTCHAR ; do
    case $OPTCHAR in
        u )
            START_FABRIC=1
            if [[ $STOP_FABRIC == 1 || $CLEAN_UP_WORK_DIR == 1 ]]; then
                echo "Only one of these options should be specified: [u|d|c]"
                exit
            fi
            ;;
        d )
            STOP_FABRIC=1
            if [[ $START_FABRIC == 1 || $CLEAN_UP_WORK_DIR == 1 ]]; then
                echo "Only one of these options should be specified: [u|d|c]"
                exit
            fi
            ;;
        c )
            CLEAN_UP_WORK_DIR=1
            if [[ $START_FABRIC == 1 || $START_FABRIC == 1 ]]; then
                echo "Only one of these options should be specified: [u|d|c]"
                exit
            fi
	    ;;
	e )
	    if [[ $STOP_FABRIC == 1 || $CLEAN_UP_WORK_DIR == 1 ]]; then
		echo "-e can not be used with -d|-c"
		exit
            fi
	    EXPOSE_PORTS=" -e true "
            ;;
        w )
            WORK_DIR=$OPTARG
            ;;
        \?|h )
            BN=$(basename $0)
            echo "$BN: Start or Stop or Clean Hyperledger Fabric setup" 1>&2
            echo "Usage: $BN [-w|[-u|-d|-c|-h]|-?]" 1>&2
            echo "Where:" 1>&2
            echo "   -w       Work directory. Default is $WORK_DIR" 1>&2
            echo "   -u       Bring up Fabric network" 1>&2
            echo "   -d       Bring down Fabric network" 1>&2
            echo "   -e       Expose peers and orderers docker container ports to host" 1>&2
            echo "   -c       Clean up Fabric work directory" 1>&2
            echo "   -? or -h print usage information" 1>&2
            echo "Examples:" 1>&2
            echo "   $BN -u" 1>&2
            echo "   $BN -w $TCF_HOME/mywork -u" 1>&2
            echo "   $BN -w $TCF_HOME/mywork -d" 1>&2
            echo "   $BN -w $TCF_HOME/mywork -c" 1>&2
            echo "   $BN -w $TCF_HOME/mywork -u -e" 1>&2
            exit 2
            ;;
    esac
done

if [ -f "$MINIFAB_INSTALL_DIR/minifab" ]; then
    echo "minifab is already installed in $MINIFAB_INSTALL_DIR"
else
    echo "Installing minifab in $MINIFAB_INSTALL_DIR"
    mkdir -p $MINIFAB_INSTALL_DIR && cd $MINIFAB_INSTALL_DIR && curl -o minifab -sL $MINIFAB_URL && chmod +x minifab
fi

if [[ -z "$TCF_HOME" ]] ; then
    export TCF_HOME="$(realpath ${SCRIPT_DIR}/..)"
fi

export PATH=$MINIFAB_INSTALL_DIR/:$PATH
# Create work dir
mkdir -p $WORK_DIR
cd $WORK_DIR

if [ $STOP_FABRIC == 1 ]; then
    minifab down
elif [ $START_FABRIC == 1 ]; then
    # If we copy chaincode files everytime, go build take more time to generate
    # build artifact.
    check_if_cc_artifacts_exists
    exist=$?
    if [ "$exist" -eq "1" ]; then
        echo "Chain codes are built and use existing built artifacts"
    else
        echo "Copying avalon fabric chaincodes to $WORK_DIR/vars/chaincode"
        mkdir -p $WORK_DIR/vars/chaincode
        cp -R $TCF_HOME/sdk/avalon_sdk/connector/blockchains/fabric/chaincode/* $WORK_DIR/vars/chaincode/
    fi

    # If already fabric network up and running skip start again.
    if [[ ! $(docker ps --format '{{.Names}}' |grep "peer*") ]]; then
        # Start the fabric containers peers, orderers, cas
	# "-e true" argument maps fabric container ports to host ports
        minifab up -i $FABRIC_VERSION $EXPOSE_PORTS
        # Create network profile file for avalon to use
        # profile file is generated in $WORK_DIR/vars/profiles/
        minifab profilegen
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
elif [ $CLEAN_UP_WORK_DIR == 1 ]; then
    minifab cleanup
    rm -rf $WORK_DIR/vars
fi
