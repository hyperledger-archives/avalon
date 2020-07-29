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

yell() {
    echo "$0: $*" >&2;
}

die() {
    yell "$*"
    exit 111
}

try() {
    "$@" || die "test failed: $*"
}

# In minifab is instantiating worker chain code in one of peer.
# If worker chain code call goes to other peer then fresh instantiation will take some
# time, so run test will wait for about 1min.

yell "Wait for fabric blockchain connector to register worker"
sleep 60s

SCRIPTDIR="$(dirname $(readlink --canonicalize ${BASH_SOURCE}))"
SRCDIR="$(realpath ${SCRIPTDIR}/..)"
generic_client_path="${TCF_HOME}/examples/apps/generic_client"
WORKER_ID="singleton-worker-1"

yell "Start testing fabric generic client for echo result workload ................"
yell "#------------------------------------------------------------------------------------------------"
try $generic_client_path/generic_client.py --blockchain fabric \
        --workload_id "echo-result" \
        --in_data "Hello Fabric proxy model" -o --worker_id $WORKER_ID

yell "Start testing fabric generic client for heart disease eval workload ................"
yell "#------------------------------------------------------------------------------------------------"
try $generic_client_path/generic_client.py --blockchain fabric \
        --workload_id "heart-disease-eval" \
        --in_data "Data: 25 10 1 67  102 125 1 95 5 10 1 11 36 1" -o \
        --worker_id $WORKER_ID

yell "#------------------------------------------------------------------------------------------------"
yell "#------------------------------------------------------------------------------------------------"

yell completed all tests
yell "#------------------------------------------------------------------------------------------------"
yell "#------------------------------------------------------------------------------------------------"

exit 0
