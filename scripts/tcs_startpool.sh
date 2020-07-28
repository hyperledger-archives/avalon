#!/bin/bash

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

KV_STORAGE="kv_storage"
ENCLAVE_MANAGER_KME="${TCF_HOME}/enclave_manager/avalon_enclave_manager/kme/kme_enclave_manager.py"
ENCLAVE_MANAGER_WPE="${TCF_HOME}/enclave_manager/avalon_enclave_manager/wpe/wpe_enclave_manager.py"
LISTENER="avalon_listener"
VERSION="$(cat ${TCF_HOME}/VERSION)"

# Default values
COMPONENTS="$ENCLAVE_MANAGER_KME $ENCLAVE_MANAGER_WPE" # #KV_STORAGE added if -s passed
START_STOP_AVALON_SERVICES=0 # default if -s not passed
LMDB_URL="http://localhost:9090" # -l default
LISTENER_URL="http://localhost:1947"
ENCLAVE_ZMQ_URL="tcp://localhost:5555"

#Variables
COUNT=1
PORT=1948
WORKER_ID=0
declare -A WORKERPOOL

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
}

start_kme()
{
    # Incrementing PORT number and workerid for New kme
    ((PORT++))
    ((WORKER_ID++))
    WORKER="kme-worker-"$WORKER_ID
    KME_URL="http://localhost:"$PORT

    # START_STOP_AVALON_SERVICES doesn't control enclave manager. It will be
    # once enclave manager runs as separate container.
    echo "Starting Avalon KME ..."
    python3 $ENCLAVE_MANAGER_KME --lmdb_url $LMDB_URL --bind $KME_URL --worker_id $WORKER &
    echo "Avalon KME started at $KME_URL"

}

start_wpe()
{
    WORKER="kme-worker-"$WORKER_ID
    echo $WORKER
    # START_STOP_AVALON_SERVICES doesn't control enclave manager. It will be
    # once enclave manager runs as separate container.
    echo "Starting Avalon WPE ..."
    python3 $ENCLAVE_MANAGER_WPE --lmdb_url $LMDB_URL --kme_listener_url $KME_URL  --worker_id $WORKER &
    echo "Avalon WPE started"
}

build_wpe()
{

    # Remove any previously generated mrenclave text file
    rm -f $TCF_HOME/wpe_mr_enclave.txt &> /dev/null

    # Reset the config file to original version
    FILE=$TCF_HOME/config/wpe_config.toml.b
    if test -f "$FILE"; then
        echo "--------Reseting the config file-----------"
        mv $TCF_HOME/config/wpe_config.toml{.b,}
    fi

    # Changing library name in wpe_config.toml file to support multiple Workerpool
    # Saving the original file with .b extension and rewriting the new library name 
    echo "Writing to config file"
    cp $TCF_HOME/config/wpe_config.toml $TCF_HOME/config/wpe_config.toml.b
    # Check line by line and replace enclave lib file name appended with integer COUNT
    while read a; do
        echo ${a//libavalon-wpe-enclave.signed.so/libavalon-wpe-enclave-$COUNT.signed.so}
    done < $TCF_HOME/config/wpe_config.toml > $TCF_HOME/config/wpe_config.toml.t 
    mv $TCF_HOME/config/wpe_config.toml{.t,}

    # Building the code 
    cd $TCF_HOME/tools/build
    export ENCLAVE_TYPE=wpe
    export WORKLOADS=$1
    echo "Building WPE with WORKLOADS: $1 "
    make  &> /dev/null
    
    # Renaming the enclave lib file as per the wpe_config.toml file 
    echo "Renaming to lib file name"
    mv $TCF_HOME/tc/sgx/trusted_worker_manager/enclave/build/lib/libavalon-wpe-enclave{,-$COUNT}.signed.so
    mv $TCF_HOME/tc/sgx/trusted_worker_manager/enclave/build/lib/libavalon-wpe-enclave{,-$COUNT}.so
    mv $TCF_HOME/tc/sgx/trusted_worker_manager/enclave/build/lib/libavalon-wpe-enclave{,-$COUNT}.signed.so.meta
    
    # Increment the count for next workerpool
    ((COUNT++))
}

reset_config_file()
{
    echo "--------Reseting the config file-----------"
    mv $TCF_HOME/config/wpe_config.toml{.b,} &> /dev/null
    sleep 10
}

check_file()
{
    while(true)
    do
        FILE=$TCF_HOME/wpe_mr_enclave.txt
        if test -f "$FILE"; then
            echo "------------------------------------------------$FILE exists."
            cat $TCF_HOME/wpe_mr_enclave.txt
            return
        fi  
    done
}

stop_avalon_components()
{
    for i in $COMPONENTS ; do
        pkill -f "$i"
    done
    echo "Hyperledger Avalon successfully ended."
    pkill -f "$ENCLAVE_MANAGER_KME"
    pkill -f "$ENCLAVE_MANAGER_WPE"
    if [ $START_STOP_AVALON_SERVICES = 1 ] ; then
        pkill -f "$KV_STORAGE"
        pkill -f "$LISTENER"
    fi
    mv $TCF_HOME/config/wpe_config.toml{.b,} &> /dev/null
    exit
}

stop_avalon_components_forcefully()
{
    ps -ef | grep bin/$LISTENER | grep -v grep | awk '{print $2}' | xargs -r kill -9 ;
    ps -ef | grep bin/$KV_STORAGE | grep -v grep | awk '{print $2}' | xargs -r kill -9;
    ps -ef | grep $ENCLAVE_MANAGER_KME | grep -v grep | awk '{print $2}' | xargs -r kill -9;
    ps -ef | grep $ENCLAVE_MANAGER_WPE | grep -v grep | awk '{print $2}' | xargs -r kill -9;

    allPorts=("bind zmq_url remote_storage_url")
    for i in $allPorts ; do
	 # Port number of listener, zmq and kv storage is picked from listener toml file.
         # grep command reads the line as string from toml file which contails the url.Eg: bind = "http://localhost:1947".
	 # awk command separates the string  into 3 parts, based on ":" such as "http,//localhost,1947".
	 # sed truncates the last char of the string. eg, " is removed from the 3rd part i.e 1947". 
	 # Hence the PORT stores the port value of the url. eg PORT=1947
	 
	 PORT=$(grep  $i ${TCF_HOME}/listener/listener_config.toml | awk -F':' '{print $3}' | sed 's/.$//i')
	 
	 #Below command kills the PID which occupied port. lsof command lists the PIDs holding the $PORT.
	 echo $PORT | lsof -t -i | xargs -r kill -9;
    done
    mv $TCF_HOME/config/wpe_config.toml{.b,} &> /dev/null
    echo "Hyperledger Avalon forcefully terminated"
    exit
}

start_program()
{

    echo "******************Welcome to Hyperledger Avalon*****************\n" 
    read -p 'Number of Worker Pool (KME) required: ' kme_count

    for (( i=1; i<=$kme_count; i++ ))
    do
        echo "Hyperledger Avalon currently supports the following service:
        1. Echo-result          code: er
        2. Heart-disease-eval   code: hd
        3. Inside-out-eval      code: io
        4. Simple-wallet        code: sw 
        5. All services         code: all"
        read -p "Workload that need to be support by worker pool $i: " -a arr
        read -p "Number of Workerorder Processing Enclave WPE required for WorkerPool $i: " wpe_count
        WORKERPOOL[$i, 1]=$wpe_count
        for wpes in "${arr[@]}"; do 
        case $wpes in
            er )
                WPE="echo-result;$WPE"
                
                ;;
            hd)
                WPE="heart-disease-eval;$WPE"
                ;;
            io)
                WPE="inside-out-eval;$WPE"
                ;;
            sw)
                WPE="simple-wallet;$WPE"
                ;;
            all)
                WPE="echo-result;heart-disease-eval;inside-out-eval;simple-wallet"
                ;;
        esac
        done
        WORKERPOOL[$i, 2]=$WPE

    done
    echo "Received Input :"
    echo ${WORKERPOOL[*]}

    echo "Initializing the build process"
    cd $TCF_HOME/tools/build
    export ENCLAVE_TYPE=kme
    make clean  &> /dev/null
    echo "Building KME"
    make   &> /dev/null
    start_avalon_components

    for (( i=1; i<=$kme_count; i++ ))
    do

        build_wpe ${WORKERPOOL[$i, 2]}
        check_file
        sleep 20
        start_kme
        for (( j=1; j<=${WORKERPOOL[$i, 1]}; j++ ))
        do
            echo "Waiting for 20 seconds for registration"
            sleep 20
            echo "Starting WPE"
            start_wpe 
            sleep 20
            
        done 
    done
    
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

start_program
