/* Copyright 2020 Intel Corporation
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
bool verify_dcap_quote(const char* ias_report, int ias_report_len);

// Verifies DCAP report signaute by extracting public key from certificate
bool verify_dcap_quote_signature(const char* dcap_attestation_signing_cert_pem,
    const char* dcap_report, unsigned int dcap_report_len,
    char* dcap_signature, unsigned int dcap_signature_len);
#endif
