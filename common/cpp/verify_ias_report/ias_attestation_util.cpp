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

#include <stdio.h>
#include <string.h>
#include <string>

#include <sgx_utils.h>
#include <sgx_quote.h>

#include "ias_attestation_util.h"
#include "verify-report.h"
#include "tcf_error.h"
#include "parson.h"
#include "jsonvalue.h"
#include "types.h"

bool verify_ias_report_signature(const std::string& signing_cert_pem,
                                 const std::string& ias_report,
                                 const std::string& ias_signature) {
    /* Verify IAS report signature
     * @param signing_cert_pem signing certificate
     * @param ias_report attestion report
     * @param ias_signature attestation report signature
     * Returns true if signature verification success
     * otherwise false
     */

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

bool verify_mr_enclave_value(const std::string& enclave_quote_body,
		             const std::string& mr_enclave) {
    /* Verify MR enclave in the attestation
     * report and compare with the value passed
     * @param enclave_quote_body Enclave quote body
     * @param mr_enclave MR enclave value in hex format
     * Return true if comparision matches otherwise false
     **/
    if (mr_enclave.size() != 0) {
        /* Extract ReportData and MR_ENCLAVE from isvEnclaveQuoteBody
           present in Verification Report */
	ByteArray quote_bytes = Base64EncodedStringToByteArray(
	    enclave_quote_body.c_str());
        sgx_quote_t* quote_body = reinterpret_cast<sgx_quote_t*>(
            quote_bytes.data());
        sgx_report_body_t* report_body = &quote_body->report_body;
        sgx_measurement_t mr_enclave_from_report = *(&report_body->mr_enclave);
        ByteArray mr_enclave_bytes = HexEncodedStringToByteArray(mr_enclave);
	if (memcmp(mr_enclave_from_report.m, mr_enclave_bytes.data(),
	    SGX_HASH_SIZE) == 0) {
            return true;
        }
        else {
            return false;
        }
    }
}
