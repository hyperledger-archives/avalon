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

function die() {
    echo "$(basename $0): $*" >&2
    exit 111
}

function try() {
    "$@" || die "test failed: $*"
}

NUM_CORES=1

if [ "$*" == "" ]; then 
	# build dependencies 
	pip3 install --upgrade setuptools json-rpc wheel toml pyzmq pycryptodomex ecdsa

	echo " --------------- COMMON PYTHON ---------------"
	cd $TCF_HOME/common/python || error_exit "Failed to change to the directory"

	try make "-j$NUM_CORES" 
	try make install

	echo "--------------- COMMON CRYPTO UTILS PYTHON ---------------"
	cd $TCF_HOME/common/crypto_utils || error_exit "Failed to change to the directory"

	try make "-j$NUM_CORES"
	try make install

	echo "--------------- AVALON SDK ---------------"
	cd $TCF_HOME/sdk || error_exit "Failed to change to the directory"

	try python3 setup.py bdist_wheel
	try pip3 install dist/*.whl

	echo "Build complete"

elif [ $1 == "test" ]; then 
	cd $TCF_HOME/common/crypto_utils/tests

	echo -e "*****Running avalon crypto utils tests*****"
	try python3 cryptoutiltest.py
	try python3 signaturetest.py

elif [ $1 == "clean" ]; then
	echo "cleaning up binaries"
	cd $TCF_HOME/common/python
	make clean

	cd $TCF_HOME//common/crypto_utils
	make clean

	cd $TCF_HOME/common/verify_report_utils/
	make clean

	cd $TCF_HOME/sdk
	make clean
else 
	echo "Invalid argument passed"
fi



