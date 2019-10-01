/* Copyright 2018 Intel Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef IAS_CA_CERT_H
#define IAS_CA_CERT_H

//IAS attestation verification report signing certification authority certificate
/*
This certificate is the root of trust for enclave attestation verification.
This is in PEM format of the SGX root certificate as can be downloaded from
https://software.intel.com/sites/default/files/managed/7b/de/RK_PUB.zip
*/
#ifdef __cplusplus
extern "C" {
#endif
extern const char ias_report_signing_ca_cert_pem[];
#ifdef __cplusplus
}
#endif
#endif
