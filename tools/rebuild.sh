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
if [[ -z "$TCF_HOME" ]] ; then
    export TCF_HOME="$(realpath ${SCRIPTDIR}/..)"
fi
if [[ -z "$TCF_ENCLAVE_CODE_SIGN_PEM" ]] ; then
   export TCF_ENCLAVE_CODE_SIGN_PEM="$TCF_HOME/enclave.pem"
   echo "Setting default TCF_ENCLAVE_CODE_SIGN_PEM=$TCF_ENCLAVE_CODE_SIGN_PEM"
fi
VERSION="$(cat $TCF_HOME/VERSION)"


# -----------------------------------------------------------------
# -----------------------------------------------------------------
cred=`tput setaf 1 2>/dev/null`
cgrn=`tput setaf 2 2>/dev/null`
cblu=`tput setaf 4 2>/dev/null`
cmag=`tput setaf 5 2>/dev/null`
cwht=`tput setaf 7 2>/dev/null`
cbld=`tput bold    2>/dev/null`
bred=`tput setab 1 2>/dev/null`
bgrn=`tput setab 2 2>/dev/null`
bblu=`tput setab 4 2>/dev/null`
bwht=`tput setab 7 2>/dev/null`
crst=`tput sgr0    2>/dev/null`

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
yell --------------- AVALON $VERSION BUILD  ---------------
yell --------------- CONFIG AND ENVIRONMENT CHECK ---------------
if [ -z "$SGX_SSL" -a -d "/opt/intel/sgxssl" ] ; then
    export SGX_SSL="/opt/intel/sgxssl"
    echo "Setting default SGX_SSL=$SGX_SSL"
fi

: "${TCF_HOME?Missing environment variable TCF_HOME}"
: "${SGX_SSL?Missing environment variable SGX_SSL}"
: "${SGX_SDK?Missing environment variable SGX_SDK}"
: "${PKG_CONFIG_PATH?Missing environment variable PKG_CONFIG_PATH}"

if [[ ${SGX_MODE} &&  "${SGX_MODE}" == "HW" ]]; then
    echo "SGX mode is set to HW"
else
    echo "Setting default SGX mode to SIM"
    export SGX_MODE=SIM
fi

try command -v python
PY3_VERSION=$(python3 --version | sed 's/Python 3\.\([0-9]\).*/\1/')
if [[ "$PY3_VERSION" -lt 5 ]]; then
    die "must use python3, activate virtualenv first"
fi

# OpenSSL library version >= $DESIRED_OPENSSL_VER
DESIRED_OPENSSL_VER="1.1.1"
# Get library version when possible, otherwise get command version.
try command -v openssl
OPENSSL_VERSION=$(openssl version -v | sed 's/OpenSSL //g' \
   | sed 's/.*Library: //' \
   | sed 's/.*OpenSSL \([^ ]*\) .*/\1/')
echo $OPENSSL_VERSION | egrep -q '^1.1.[1-9]|^1.[2-9]|^[2-9]|^[1-9][0-9]'
if [ $? -ne 0 ] ; then
   echo "WARNING: openssl version is $OPENSSL_VERSION;" \
        " expecting >= $DESIRED_OPENSSL_VER" >&2
   echo "Note: openssl can be a different version as long as" \
        " libssl and libssl-dev are >= $DESIRED_OPENSSL_VER" >&2
fi

# protoc version must be >= 3.
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

yell --------------- "COMMON SGX (WORKLOAD & IOHANDLER)" ---------------
cd $TCF_HOME/common/sgx_workload/

mkdir -p build
cd build
try cmake ..
try make "-j$NUM_CORES"

yell --------------- EXAMPLE WORKLOADS ---------------
cd $TCF_HOME/examples/apps

mkdir -p build
cd build
try cmake ..
try make "-j$NUM_CORES"

yell --------------- COMMON CPP ---------------
cd $TCF_HOME/common/cpp

mkdir -p build
cd build
try cmake ..
try make "-j$NUM_CORES"

yell --------------- TRUSTED WORKER MANAGER COMMON ---------------
cd $TCF_HOME/tc/sgx/trusted_worker_manager/common

mkdir -p build
cd build
try cmake ..
try make "-j$NUM_CORES"

yell --------------- ENCLAVE ---------------
cd $TCF_HOME/tc/sgx/trusted_worker_manager/enclave

mkdir -p build
cd build
try cmake ..
try make "-j$NUM_CORES"

yell --------------- ENCLAVE BRIDGE---------------
cd $TCF_HOME/tc/sgx/trusted_worker_manager/enclave_untrusted/enclave_bridge

mkdir -p build
cd build
try cmake ..
try make "-j$NUM_CORES"

yell --------------- EXAMPLES COMMON PYTHON ---------------
cd $TCF_HOME/common/python
try make "-j$NUM_CORES"
try make install

yell --------------- ENCLAVE MANAGER ---------------
cd $TCF_HOME/examples/enclave_manager
try make "-j$NUM_CORES"
try make install

yell --------------- AVALON SDK ---------------
cd $TCF_HOME/sdk
try python3 setup.py bdist_wheel
try pip3 install dist/*.whl

yell --------------- LMDB LISTENER ---------------
cd $TCF_HOME/shared_kv_storage/db_store/packages
mkdir -p build
cd build
try cmake ..
try make

yell --------------- SHARED KV STORAGE ---------------
cd $TCF_HOME/shared_kv_storage
try make
try make install

yell --------------- AVALON LISTENER ----------------
cd $TCF_HOME/listener
try make "-j$NUM_CORES"
try make install

