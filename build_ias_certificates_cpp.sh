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

Cleanup () {
    echo "Cleaning up"
    rm ias-certificates.cpp.tmp -f
    rm RK_PUB.zip -f
    rm AttestationReportSigningCACert.pem.der -f
    rm AttestationReportSigningCACert.pem -f
    rm AttestationReportSigningCACert.pem.der.hex -f
    rm AttestationReportSigningCACert.pem.der.size -f
    exit 0
}

trap 'echo "**ERROR - line $LINENO**"; Cleanup' HUP INT QUIT PIPE TERM ERR

#get certificate from Intel
wget https://software.intel.com/sites/default/files/managed/7b/de/RK_PUB.zip
test -e RK_PUB.zip && echo "Zipped certificated downloaded"

#decompress certificate
unzip RK_PUB.zip
test -e RK_PUB.zip

openssl x509 -outform der -in AttestationReportSigningCACert.pem -out AttestationReportSigningCACert.pem.der
test -e AttestationReportSigningCACert.pem.der
echo "Der certificate derived"

#hexdump the der certificate and remove last comma
hexdump -ve '1/1 "0x%.2x, "' AttestationReportSigningCACert.pem.der| sed 's/, $//' > AttestationReportSigningCACert.pem.der.hex
test -e AttestationReportSigningCACert.pem.der.hex
echo "Der certificate hexdumped"
#grab the size of the der certificate
stat --printf="%s" AttestationReportSigningCACert.pem.der > AttestationReportSigningCACert.pem.der.size
test -e AttestationReportSigningCACert.pem.der.size
echo "Der certificate size retrieved"

echo ""
echo -n "Building ias-certificates.cpp ... "
#replace the placemark in the template with the der certificate
cmd=`echo "sed 's/IAS_REPORT_SIGNING_CA_CERT_DER_PLACEMARK/\`cat AttestationReportSigningCACert.pem.der.hex\`/' < ias-certificates.cpp.template > ias-certificates.cpp.tmp"`
eval $cmd
#repplace the second placemark in the updated template with the der certificate size
cmd=`echo "sed 's/IAS_REPORT_SIGNING_CA_CERT_DER_LEN_PLACEMARK/\`cat AttestationReportSigningCACert.pem.der.size\`/' < ias-certificates.cpp.tmp > ias-certificates.cpp"`
eval $cmd
echo "done"

Cleanup
