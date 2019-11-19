#! /bin/bash

# Copyright 2019 Intel Corporation
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
echo_client_path="${TCF_HOME}/examples/apps/echo/client"
# Read Listener port from config file
listener_port=`grep listener_port ${TCF_HOME}/config/tcs_config.toml | awk {'print $3'}`

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

SAVE_FILE=$(mktemp /tmp/tcf-test.XXXXXXXXX)
INPUT_FOLDERS=(json_requests worker work_orders signature)

function cleanup {
    yell "Clearing enclave files and database files"
    rm -f ${TCF_HOME}/config/Kv*
    rm -f ${SAVE_FILE}
}

trap cleanup EXIT
#------------------------------------------------------------------------------------------------

yell "#------------------------------------------------------------------------------------------------"
yell "#------------------------------------------------------------------------------------------------"
cd ${TCF_HOME}/tests
yell "#------------------------------------------------------------------------------------------------"
yell "#------------------------------------------------------------------------------------------------"

for folder in "${INPUT_FOLDERS[@]}"
do
    yell "Start testing folder:: $folder ............"
    yell "#------------------------------------------------------------------------------------------------"
    # Delay is introduced for user readability
    sleep 5s
    try python3 ${TCF_HOME}/tests/Demo.py \
        --logfile __screen__ --loglevel warn \
        --input_dir ${TCF_HOME}/tests/$folder/ \
        --connect_uri "http://localhost:$listener_port" work_orders/output.json > /dev/null

    yell "#------------------------------------------------------------------------------------------------"
    yell "#------------------------------------------------------------------------------------------------"
done

yell "Start testing echo client ................"
yell "#------------------------------------------------------------------------------------------------"
# Testing echo client with enabling requester signature and input data hash
try $echo_client_path/echo_client.py -m "Hello world" -rs -dh

yell "#------------------------------------------------------------------------------------------------"
yell "#------------------------------------------------------------------------------------------------"
sleep 10s
yell "#------------------------------------------------------------------------------------------------"
yell "#------------------------------------------------------------------------------------------------"
yell "Start unit testing ................"
yell "#------------------------------------------------------------------------------------------------"

cd ${TCF_HOME}/tests/test_utility
try nose2

yell "#------------------------------------------------------------------------------------------------"
yell "#------------------------------------------------------------------------------------------------"

yell completed all tests
yell "#------------------------------------------------------------------------------------------------"
yell "#------------------------------------------------------------------------------------------------"

exit 0
