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

PY3_VERSION=$(python3 --version | sed 's/Python 3\.\([0-9]\).*/\1/')
if [[ $PY3_VERSION -lt 5 ]]; then
    echo activate python3 first
    exit
fi

SCRIPTDIR="$(dirname $(readlink --canonicalize ${BASH_SOURCE}))"
SRCDIR="$(realpath ${SCRIPTDIR}/..)"

# Remove private pem file used to sign enclave binary
rm -f $SRCDIR/enclave.pem

# Remove generated ias-certificate file
rm -f $SRCDIR/tc/sgx/common/crypto/verify_ias_report/ias-certificates.cpp

# Remove LMDB files
echo "******** DELETE LMDB FILES **************"
rm -f $SRCDIR/config/Kv_Shared*

# --------------- EXAMPLES COMMON ---------------
cd $SRCDIR/common/python
make clean

# --------------- EXAMPLES ENCLAVE MANAGER ---------------
cd $SRCDIR/examples/enclave_manager
SGX_MODE=${SGX_MODE:-SIM} make clean

# --------------- COMMON SGX WORKLOAD ---------------
rm -rf $SRCDIR/common/sgx_workload/build

# --------------- ENCLAVE ---------------
cd $SRCDIR/tc/sgx/trusted_worker_manager/enclave
rm -rf build deps

cd $SRCDIR/common/cpp
rm -rf build

# --------------- WORKLOADS -------------
cd $SRCDIR/examples/apps
rm -rf build

