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

# Remove LMDB files
echo "******** DELETE LMDB FILES **************"
rm -f $SRCDIR/config/Kv_Shared*

# --------------- TCS CORE COMMON ---------------
cd $SRCDIR/tcs/core/common/python
make clean

# --------------- TCF COMMON ---------------
cd $SRCDIR/common
make clean

# --------------- CORE ---------------
cd $SRCDIR/tcs/core/tcs_trusted_worker_manager/enclave
rm -rf build deps

cd $SRCDIR/tcs/core/common
rm -rf build

# --------------- WORKLOADS -------------
cd $SRCDIR/workloads
rm -rf build

