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
ENCLAVE_MANAGER="${TCF_HOME}/enclave_manager/avalon_enclave_manager/singleton/singleton_enclave_manager.py"
LISTENER="avalon_listener"
VERSION="$(cat ${TCF_HOME}/VERSION)"
# Default values
COMPONENTS="$ENCLAVE_MANAGER" # #KV_STORAGE added if -s passed
START_STOP_AVALON_SERVICES=0 # default if -s not passed
LMDB_URL="http://localhost:9090" # -l default
LISTENER_URL="http://localhost:1947"
ENCLAVE_ZMQ_URL="tcp://localhost:5555"

# Trap handler
trap 'stop_avalon_components' HUP INT QUIT ABRT ALRM TERM

is_sync_mode()
{
    return grep "sync_workload_execution" ${TCF_HOME}/listener/listener_config.toml | awk -F'=' '{print $2}'
}

start_avalon_components()
{
    if [ $START_STOP_AVALON_SERVICES = 1 ] ; then
        echo "Starting Avalon KV Storage $VERSION ..."
        $KV_STORAGE --bind $LMDB_URL & 
        echo "Avalon KV Storage started"
    fi
    
    # START_STOP_AVALON_SERVICES doesn't control enclave manager. It will be
    # once enclave manager runs as seperate container.
    echo "Starting Avalon Enclave Manager $VERSION ..."
    python3 $ENCLAVE_MANAGER --lmdb_url $LMDB_URL &
    echo "Avalon Enclave Manager started"

    if [ $START_STOP_AVALON_SERVICES = 1 ] ; then
        echo "Starting Avalon Listener $VERSION ..."
        is_sync_mode
        is_sync_mode_on=$?
        if [ "$is_sync_mode_on" -eq "1" ]; then
	        $LISTENER --bind $LISTENER_URL --lmdb_url $LMDB_URL --zmq_url $ENCLAVE_ZMQ_URL &
        else
            $LISTENER --bind $LISTENER_URL --lmdb_url $LMDB_URL &
        fi
	    echo "Avalon Listener started"
    fi

    sleep 5s
    check_avalon_components

    if [ "$YES" != "1" ] ; then
        while true; do
            echo "If you wish to exit the program, press y and enter"
            read -t 5 yn
            case $yn in
                y ) stop_avalon_components;;
                * ) echo " ";;
            esac
        done
    fi
}

check_avalon_components()
{
    for i in $COMPONENTS ; do
        pgrep -f "$i"
        if [ $? != 0 ] ; then
            echo "Terminating Avalon because component not running:"
            echo "$i"
            stop_avalon_components
        fi
    done
}

stop_avalon_components()
{
    for i in $COMPONENTS ; do
        pkill -f "$i"
    done
    echo "Hyperledger Avalon successfully ended."
    pkill -f "$ENCLAVE_MANAGER"
    if [ $START_STOP_AVALON_SERVICES = 1 ] ; then
        pkill -f "$KV_STORAGE"
        pkill -f "$LISTENER"
    fi

    exit
}

stop_avalon_components_forcefully()
{
    ps -ef | grep bin/$LISTENER | grep -v grep | awk '{print $2}' | xargs -r kill -9 ;
    ps -ef | grep bin/$KV_STORAGE | grep -v grep | awk '{print $2}' | xargs -r kill -9;
    ps -ef | grep $ENCLAVE_MANAGER | grep -v grep | awk '{print $2}' | xargs -r kill -9;

    allPorts=("bind zmq_url remote_storage_url")
    for i in $allPorts ; do
	 # Port number of listerner, zmq and kv storage is picked from listener toml file.
         # grep command reads the line as string from toml file which contails url.eg: bind = "http://localhost:1947".
	 # awk command seperates the string  into 3, based on ":" such as "http,//localhost,1947".
	 # sed truncates the last char of the string. eg, " is removed from the 3rd part i.e 1947". 
	 # Hence the PORT stores the port value of the url. eg PORT=1947
	 
	 PORT=$(grep  $i ${TCF_HOME}/listener/listener_config.toml | awk -F':' '{print $3}' | sed 's/.$//i')
	 
	 #Below command kills the PID which occupied port. lsof command lists the PIDs holding the $PORT.
	 echo $PORT | lsof -t -i | xargs -r kill -9;
    done

    echo "Hyperledger Avalon forcefully terminated"
    exit
}

while getopts "l:styhf" OPTCHAR ; do
    case $OPTCHAR in
        s )
            START_STOP_AVALON_SERVICES=1
            COMPONENTS="$COMPONENTS $KV_STORAGE $LISTENER"
            ;;
        l )
            LMDB_URL=$OPTARG
            ;;
        y )
            YES=1
            ;;
        t )
            stop_avalon_components
            ;;
        f )
            stop_avalon_components_forcefully
            ;;
        \?|h )
            BN=$(basename $0)
            echo "$BN: Start or Stop Hyperledger Avalon" 1>&2
            echo "Usage: $BN [-l|-s|-t|-y|-h|-?]" 1>&2
            echo "Where:" 1>&2
            echo "   -l       LMDB server URL. Default is $LMDB_URL" 1>&2
            echo "   -t       terminate the program gracefully" 1>&2
            echo "   -y       do not prompt to end program" 1>&2
            echo "   -s       also start or stop KV storage component" 1>&2
            echo "   -f       forcefully kill avalon" 1>&2
            echo "   -? or -h print usage information" 1>&2
            echo "Examples:" 1>&2
            echo "   $BN -s" 1>&2
            echo "   $BN -t -s" 1>&2
            echo "   $BN -y -l http://avalon-lmdb:9090" 1>&2
            exit 2
            ;;
    esac
done
shift `expr $OPTIND - 1`

start_avalon_components
