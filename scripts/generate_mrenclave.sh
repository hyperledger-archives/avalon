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

if [ "$1" == "" ]; then
    echo 'Parse the output of the SGX tool to extract the MRENCLAVE value'
    echo 'and save it to file $TCF_HOME/metadata_info.txt by default'
    echo 'Usage: generate_mrenclave.sh <library location> <output file(optional)>'
    exit
fi

LIB="$1"
if [ -z "$2" ];then
	OUT_FILE="${TCF_HOME}/metadata_info.txt"
else
	OUT_FILE=$2
fi	

sgx_metadata="sgx_sign dump -enclave ${LIB} -dumpfile /dev/stdout"
mrenclave_search_pattern="/metadata->enclave_css.body.enclave_hash.m:/{flag=1; next} \
        /metadata->enclave_css.body.isv_prod_id:/{flag=0} flag"
first_two_lines="head -n2"
merge_lines="sed N;s/\n//"
strip_trailing_space="sed -e s/[[:blank:]]*$//"

mrenclave_hex_bytes="$(awk "$mrenclave_search_pattern" <($sgx_metadata) |\
        ($first_two_lines) | ($merge_lines) | ($strip_trailing_space))"

echo $mrenclave_hex_bytes > ${OUT_FILE}
