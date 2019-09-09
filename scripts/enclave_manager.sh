#!/bin/bash

enclave_manager="${TCF_HOME}/examples/enclave_manager/tcf_enclave_manager/enclave_manager.py"

source ${TCF_HOME}/tools/build/_dev/bin/activate

echo "starting enclave manager ..."
python3 $enclave_manager
