/* Copyright 2019 Intel Corporation
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

#include <string>
#include <stdio.h>
#include <iostream>
#include <string.h>

#include "ias_attestation_util.h"
#include "verify-report.h"
#include "tcf_error.h"
#include "parson.h"
#include "jsonvalue.h"

bool verify_ias_report_signature(const std::string& signing_cert_pem,
                                   const std::string& ias_report,
				   const std::string& ias_signature) {

    // Parse JSON serialized IAS report
    JsonValue report_parsed(json_parse_string(ias_report.c_str()));
    const char* verification_report = json_value_get_string(report_parsed.value);

    bool sig_status = verify_ias_report_signature(signing_cert_pem.c_str(),
                        verification_report,
                        strlen(verification_report),
                        (char*) ias_signature.c_str(),
                        ias_signature.length());

    return sig_status;
}

bool verify_quote(const std::string& ias_report, int group_out_of_date_is_ok) {

    // Parse JSON serialized IAS report
    JsonValue report_parsed(json_parse_string(ias_report.c_str()));
    const char* verification_report = json_value_get_string(report_parsed.value);

    bool quote_status = verify_enclave_quote_status(verification_report,
                          strlen(verification_report),
                          group_out_of_date_is_ok);

    return quote_status;
}

