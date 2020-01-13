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

#include <assert.h>
#include <stdlib.h>
#include <string.h>

#include "verify-report.h"
#include "verify_certificate.h"
#include "verify_signature.h"
#include "c11_support.h"
#include "crypto_utils.h"
#include "ias-certificates.h"

bool verify_ias_report_signature(
    const char* ias_attestation_signing_cert_pem,
    const char* ias_report,
    unsigned int ias_report_len,
    char* ias_signature,
    unsigned int ias_signature_len)
{
    bool signature_status = verify_signature(ias_attestation_signing_cert_pem,
        ias_report, ias_report_len, ias_signature, ias_signature_len);
    return signature_status;
}

bool verify_ias_certificate_chain(const char* cert_pem)
#ifndef IAS_CA_CERT_REQUIRED
{
    return false; // Fail (conservative approach for simulator-mode
                           // and in absence of CA certificate)
}
#else // IAS_CA_CERT_REQUIRED is defined
{
    bool cert_status = verify_certificate_chain(cert_pem, ias_report_signing_ca_cert_pem);
    return cert_status;
}
#endif // IAS_CA_CERT_REQUIRED

/**
 * Check if isvEnclaveQuoteStatus is "OK"
 * (cf. https://software.intel.com/sites/default/files/managed/7e/3b/ias-api-spec.pdf,
 * pg. 24).
 *
 * @return 0 if verified successfully, 1 otherwise.
 */
bool verify_enclave_quote_status(const char* ias_report,
                                 int ias_report_len,
                                 int group_out_of_date_is_ok)
{
    // Move ias_report into \0 terminated buffer such that we can work
    // with str* functions.
    int buf_len = ias_report_len + 1;
    char buf[buf_len];
    memcpy_s(buf, buf_len, ias_report, ias_report_len);
    buf[ias_report_len] = '\0';

    const int json_string_max_len = 64;
    const char json_string[json_string_max_len] = "\"isvEnclaveQuoteStatus\":\"";
    char* p_begin = strstr(buf, json_string);
    assert(p_begin != NULL);
    p_begin += strnlen(json_string, json_string_max_len);

    const int status_OK_max_len = 8;
    const char status_OK[status_OK_max_len] = "OK\"";
    if (0 == strncmp(p_begin, status_OK, strnlen(status_OK, status_OK_max_len)))
        return true;

    // TODO: expose enum with all possible values for quote status
    if(group_out_of_date_is_ok)
    {
        const int status_outdated_max_len = 64;
        const char status_outdated[status_outdated_max_len] = "GROUP_OUT_OF_DATE\"";
        if (0 == strncmp(p_begin, status_outdated,
                         strnlen(status_outdated, status_outdated_max_len)))
        {
            return true;
        }
    }

    // Quote not ok
    return false;
}
