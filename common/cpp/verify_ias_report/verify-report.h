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

#ifndef VERIFY_REPORT_H
#define VERIFY_REPORT_H

// Verifies enclave quote status
bool verify_enclave_quote_status(const char* ias_report,
                                 int ias_report_len,
                                 int group_out_of_date_is_ok);

// Verifies IAS certificate chain against IAS CA certificate
bool verify_ias_certificate_chain(const char* cert_pem);

// Verifies IAS report signaute by extracting public key from certificate
bool verify_ias_report_signature(const char* ias_attestation_signing_cert_pem,
                                 const char* ias_report,
                                 unsigned int ias_report_len,
                                 char* ias_signature,
                                 unsigned int ias_signature_len);
#endif
