#!/bin/bash

# Copyright 2018 Intel Corporation
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

SCRIPTDIR="$(dirname $(readlink --canonicalize ${BASH_SOURCE}))"
SRCDIR="$(realpath ${SCRIPTDIR}/..)"
TCF_ENCLAVE_CODE_SIGN_PEM=${SCRIPTDIR}/../enclave.pem

#TCF_ENCLAVE_CODE_SIGN_PEM is used by other files, hence setting environment
export TCF_ENCLAVE_CODE_SIGN_PEM=${SCRIPTDIR}/../enclave.pem

# -----------------------------------------------------------------
# -----------------------------------------------------------------
cred=`tput setaf 1`
cgrn=`tput setaf 2`
cblu=`tput setaf 4`
cmag=`tput setaf 5`
cwht=`tput setaf 7`
cbld=`tput bold`
bred=`tput setab 1`
bgrn=`tput setab 2`
bblu=`tput setab 4`
bwht=`tput setab 7`
crst=`tput sgr0`

function recho () {
    echo "${cbld}${cred}" $@ "${crst}" >&2
}

function becho () {
    echo "${cbld}${cblu}" $@ "${crst}" >&2
}

function yell() {
    becho "$(basename $0): $*" >&2
}

function die() {
    recho "$(basename $0): $*" >&2
    exit 111
}

function try() {
    "$@" || die "test failed: $*"
}

# -----------------------------------------------------------------
# CHECK ENVIRONMENT
# -----------------------------------------------------------------
yell --------------- CONFIG AND ENVIRONMENT CHECK ---------------

: "${TCF_HOME?Missing environment variable TCF_HOME}"
: "${TCF_ENCLAVE_CODE_SIGN_PEM?Missing environment variable TCF_ENCLAVE_CODE_SIGN_PEM}"
: "${SGX_SSL?Missing environment variable SGX_SSL}"
: "${SGX_SDK?Missing environment variable SGXSDKInstallPath}"
: "${PKG_CONFIG_PATH?Missing environment variable PKG_CONFIG_PATH}"

# Set proxy for Intel Architectural Enclave Service Manager
if [[ ${SGX_MODE} &&  "${SGX_MODE}" == "HW" ]]; then
    # Add proxy settings
    echo "proxy type = manual" >> /etc/aesmd.conf
    echo "aesm proxy = $http_proxy" >> /etc/aesmd.conf

    # Starting aesm service
    echo "Starting aesm service"
    /opt/intel/libsgx-enclave-common/aesm/aesm_service &
else
    echo "Setting default SGX mode to SIM"
    # Setting default SGX mode as SIM
    export SGX_MODE=SIM
fi

try command -v python
PY3_VERSION=$(python3 --version | sed 's/Python 3\.\([0-9]\).*/\1/')
if [[ "$PY3_VERSION" -lt 5 ]]; then
    die "must use python3, activate virtualenv first"
fi

# OpenSSL library version >= 1.1.0h.
# Get library version when possible, otherwise get command version.
try command -v openssl
OPENSSL_VERSION=$(openssl version -v;openssl version -v | sed 's/.*Library: //' \
   | sed 's/.*OpenSSL \([^ ]*\) .*/\1/')
echo $OPENSSL_VERSION | egrep -q '^1.1.0[h-z]|^1.1.[1-9]|^1.[2-9]|^[2-9]|^[1-9][0-9]'
if [ $? -ne 0 ] ; then
   echo "WARNING: openssl version is $OPENSSL_VERSION; expecting >= 1.1.0h" >&2
   echo 'Note: openssl can be a different version as long as libssl and libssl-dev are >= 1.1.0h' >&2
fi

try command -v protoc
PROTOC_VERSION=$(protoc --version | sed 's/libprotoc \([0-9]\).*/\1/')
if [[ "$PROTOC_VERSION" -lt 3 ]]; then
    echo "protoc must be version3 or higher" >&2
fi

try command -v cmake
try command -v swig
try command -v make
try command -v g++

if [ ! -d "${TCF_HOME}" ]; then
    die TCF_HOME directory does not exist
fi

# Automatically determine how many cores the host system has
# (for use with multi-threaded make)
#NUM_CORES=$(grep -c '^processor' /proc/cpuinfo)
#if [ "$NUM_CORES " == " " ]; then
#    NUM_CORES=4
#fi
# Set to 1 as the build fails when > 1.
NUM_CORES=1

# -----------------------------------------------------------------
# BUILD
# -----------------------------------------------------------------
yell --------------- COMMON SGX WORKLOAD ---------------
cd $SRCDIR/common/sgx_workload

mkdir -p build
cd build
try cmake ..
try make "-j$NUM_CORES"

yell --------------- EXAMPLE WORKLOADS ---------------
cd $SRCDIR/examples/apps

mkdir -p build
cd build
try cmake ..
try make "-j$NUM_CORES"

yell --------------- TC SGX COMMON ---------------
cd $SRCDIR/tc/sgx/common

mkdir -p build
cd build
try cmake ..
try make "-j$NUM_CORES"

yell --------------- ENCLAVE ---------------
cd $SRCDIR/tc/sgx/trusted_worker_manager/enclave

mkdir -p build
cd build
try cmake ..
try make "-j$NUM_CORES"

yell --------------- EXAMPLES COMMON PYTHON ---------------
cd $SRCDIR/examples/common/python
try make "-j$NUM_CORES"
try make install

yell --------------- ENCLAVE MANAGER ---------------
cd $SRCDIR/examples/enclave_manager
try make "-j$NUM_CORES"
try make install
