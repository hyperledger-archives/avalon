#!/bin/bash

source ${TCF_HOME}/tools/build/_dev/bin/activate

testsDir=${TCF_HOME}/tests

python3 ${testsDir}/Demo.py --input_dir ${testsDir}/json_requests/ \
    --connect_uri "http://tcs:8080" ${testsDir}/work_orders/output.json
