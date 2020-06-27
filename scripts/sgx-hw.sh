#!/bin/bash

# This script updates the spid and ias_api_key in enclave config file.
# Usage:
# export following variables in your terminal:
# export MYSPID='spid = "<spid_value>"'
# export MYIAS='ias_api_key = "<ias key value>"'
# Run the script:
# ./scripts/sgx-hw.sh config/singleton_enclave_config.toml

if [[ -z "$MYSPID" ]] ; then
    echo "MYSPID is not defined"
    exit 1
fi

if [[ -z "$MYIAS" ]] ; then
    echo "MYIAS is not defined"
    exit 1
fi

a=$(sed -n '/spid =/=' $1)
sed -i "${a}s/.*/${MYSPID}/" $1
a=$(sed -n '/ias_api_key =/=' $1)
sed -i "${a}s/.*/${MYIAS}/" $1
