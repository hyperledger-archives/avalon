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
rm -f $SRCDIR/common/cpp/verify_ias_report/ias-certificates.cpp

# Remove LMDB files
echo "******** DELETE LMDB FILES **************"
rm -f $SRCDIR/Kv_Shared*

#--------------- KV STORAGE ---------------
cd $SRCDIR/shared_kv_storage
make clean

#--------------- KME WORKLOAD ---------------
cd $SRCDIR/tc/sgx/trusted_worker_manager/enclave/kme/workload
rm -rf build

# --------------- COMMON CPP ---------------
cd $SRCDIR/common/cpp
rm -rf build

# --------------- COMMON CPP TESTS---------------
cd $SRCDIR/common/cpp/tests
rm -rf build

# --------------- COMMON INTEL SGX WORKLOAD ---------------
cd $SRCDIR/common/sgx_workload
rm -rf build

# --------------- INTEL SGX COMMON ---------------
cd $SRCDIR/tc/sgx/trusted_worker_manager/common
rm -rf build

# --------------- WORKLOADS -------------
cd $SRCDIR/examples/apps
rm -rf build

# --------------- ENCLAVE ---------------
cd $SRCDIR/tc/sgx/trusted_worker_manager/enclave
rm -rf build deps

# --------------- ENCLAVE BRIDGE ---------------
cd $SRCDIR/tc/sgx/trusted_worker_manager/enclave_untrusted/enclave_bridge
rm -rf build

# --------------- COMMON PYTHON ---------------
cd $SRCDIR/common/python
make clean

# --------------- CRYPTO UTILS ---------------
cd $SRCDIR/common/crypto_utils
make clean

# --------------- VERIFY REPORT UTILS ---------------
cd $SRCDIR/common/verify_report_utils/
make clean

# --------------- SDK ---------------
cd $SRCDIR/sdk
make clean

# --------------- ENCLAVE MANAGER ---------------
cd $SRCDIR/enclave_manager
make clean

#--------------- AVALON LISTENER ----------------
cd $SRCDIR/listener
make clean
