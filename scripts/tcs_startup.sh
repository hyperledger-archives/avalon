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

KV_STORAGE="kv_storage"
enclave_manager="${TCF_HOME}/examples/enclave_manager/tcf_enclave_manager/enclave_manager.py"
listener="${TCF_HOME}/common/python/connectors/direct/tcs_listener/tcs_listener.py"
version="$(cat ${TCF_HOME}/VERSION)"
# Default values
START_KV_STORAGE=1 # default if -s not passed

# Trap handler
trap 'stop_tcs_components' HUP INT QUIT ABRT ALRM TERM

start_tcs_components()
{
    # Read Listener port from config file
    listener_port=`grep listener_port ${TCF_HOME}/config/tcs_config.toml \
        | awk {'print $3'}`
    if [ -z "$listener_port" ]; then
        listener_port=1947
    fi

    if [ $START_KV_STORAGE = 1 ] ; then
    	echo "Starting Avalon KV Storage $version ..."
    	python3 $KV_STORAGE --bind http://avalon-lmdb:9090 & 
    	echo "Avalon KV Storage started"
    fi

    echo "Starting Avalon Enclave Manager $version ..."
    python3 $enclave_manager --lmdb_url http://avalon-lmdb:9090 &
    echo "Avalon Enclave Manager started"

    sleep 5s

    echo "Starting Avalon Listener $version ..."
    python3 $listener --bind_uri $listener_port --lmdb_url http://avalon-lmdb:9090 &
    echo "Avalon Listener started"

    if [ "$YES" != "1" ] ; then
        while true; do
        echo "If you wish to exit the program, press y and enter"
        read -t 5 yn
        case $yn in
            y ) stop_tcs_components;;
            * ) echo " ";;
        esac
        done
    fi
}

stop_tcs_components()
{
    echo "TCS successfully ended."
    pkill -f "$listener"
    pkill -f "$enclave_manager"
    pkill -f "$KV_STORAGE"
    exit
}


while getopts "styh" OPTCHAR ; do
    case $OPTCHAR in
        s )
            START_KV_STORAGE=0
            ;;
        y )
            YES=1
            ;;
        t )
            stop_tcs_components
            ;;
        \?|h )
            BN=$(basename $0)
            echo "$BN: Start or Stop TCS" 1>&2
            echo "Usage: $BN [-s|-t|-y|-h|-?]" 1>&2
            echo "Where:" 1>&2
            echo "   -t       terminate the program" 1>&2
            echo "   -y       do not prompt to end program" 1>&2
            echo "   -s       do not start KV storage component" 1>&2
            echo "   -? or -h print usage information" 1>&2
            echo "Examples:" 1>&2
            echo "   $BN" 1>&2
            echo "   $BN -t" 1>&2
            echo "   $BN -y -s" 1>&2
            exit 2
            ;;
    esac
done
shift `expr $OPTIND - 1`

start_tcs_components
