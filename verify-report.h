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

#include <sgx_quote.h>

typedef enum {
    VERIFY_SUCCESS,
    VERIFY_FAILURE
} verify_status_t;

void get_quote_from_report(const uint8_t* report, const int report_len, sgx_quote_t* quote);
verify_status_t verify_enclave_quote_status(const char* ias_report, int ias_report_len, int group_out_of_date_is_ok);
verify_status_t verify_ias_certificate_chain(const char* optional_cert, int optional_cert_len);
verify_status_t verify_ias_report_signature(char* ias_attestation_signing_cert,
                                            unsigned int ias_attestation_signing_cert_len,
                                            char* ias_report,
                                            unsigned int ias_report_len,
                                            char* ias_signature,
                                            unsigned int ias_signature_len);
#endif
