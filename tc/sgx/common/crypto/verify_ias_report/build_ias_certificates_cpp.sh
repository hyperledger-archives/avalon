#!/bin/bash

# Copyright 2018 Intel Corporation
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

# if we are not running in hardware mode then we can just copy
# the simulator version and use it

if [ -f ias-certificates.cpp ]; then rm ias-certificates.cpp; fi

if [ "${SGX_MODE}" != "HW" ]; then
    cp ias-certificates.template ias-certificates.cpp || exit 1
    # Note: use cp instead of ln or ln -s so timestamps work properly for dependencies in makefile
    exit 0
fi

Cleanup () {
    echo "Cleaning up"
    rm ias-certificates.cpp.tmp -f
    rm RK_PUB.zip -f
    rm AttestationReportSigningCACert.pem -f
}

trap 'echo "**ERROR - line $LINENO**"; Cleanup; exit 1' HUP INT QUIT PIPE TERM ERR

#get certificate from Intel
wget https://software.intel.com/sites/default/files/managed/7b/de/RK_PUB.zip
test -e RK_PUB.zip
echo "Zipped certificated downloaded"

unzip -o RK_PUB.zip
test -e AttestationReportSigningCACert.pem

echo ""
echo -n "Building ias-certificates.cpp ... "
#replace the placemark in the template with the der certificate
sed -e '/IAS_REPORT_SIGNING_CA_CERT_PEM_PLACEMARK/ r ./AttestationReportSigningCACert.pem' \
    -e 's/IAS_REPORT_SIGNING_CA_CERT_PEM_PLACEMARK//' < ias-certificates.template > ias-certificates.cpp
test -e ias-certificates.cpp
echo "done"

Cleanup
exit 0
