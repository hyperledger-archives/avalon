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

#include <assert.h>
#include <stdlib.h>
#include <string.h>

#include "verify-dcap-quote.h"
#include "verify-dcap-quote.h"

#include <sgx_dcap_quoteverify.h>
#include "hex_string.h"
#include "sgx_dcap_ql_wrapper.h"
#include "sgx_quote_3.h"
#include "sgx_report.h"
#include "sgx_error.h"
#include "sgx_qve_header.h"
#include "sgx_ql_quote.h"
#include "utils.h"

bool verify_dcap_quote_signature(
    const char* dcap_attestation_signing_cert_pem,
    const char* dcap_report,
    unsigned int dcap_report_len,
    char* signature,
    unsigned int signature_len) {
    // TODO: Implement DCAP quote signature
    return true;
}

bool verify_dcap_quote(const char* dcap_quote, int dcap_quote_len) {
    int ret = 0;
    time_t current_time = 0;
    uint32_t supplemental_data_size = 0;
    uint8_t *p_supplemental_data = NULL;
    quote3_error_t dcap_ret = SGX_QL_ERROR_UNEXPECTED;
    sgx_ql_qv_result_t quote_verification_result = SGX_QL_QV_RESULT_UNSPECIFIED;
    uint32_t collateral_expiration_status = 1;

    dcap_ret = sgx_qv_get_quote_supplemental_data_size(&supplemental_data_size);
    if (dcap_ret == SGX_QL_SUCCESS && \
        supplemental_data_size == sizeof(sgx_ql_qv_supplemental_t)) {
        printf("\tInfo: sgx_qv_get_quote_supplemental_data_size successfully returned.\n");
        p_supplemental_data = (uint8_t*)malloc(supplemental_data_size);
    }
    else {
        printf("\tError: sgx_qv_get_quote_supplemental_data_size failed: 0x%04x\n", dcap_ret);
        supplemental_data_size = 0;
    }

    // Set current time. This is only for sample purposes,
    // in production mode a trusted time should be used.
    current_time = time(NULL);


    ByteArray quote = Base64EncodedStringToByteArray(dcap_quote);
    // call DCAP quote verify library for quote verification
    // here you can choose 'untrusted' quote verification
    // by specifying parameter '&qve_report_info'
    // if '&qve_report_info' is NOT NULL, this API will call Intel QvE
    // to verify quote if '&qve_report_info' is NULL, this API will call
    // 'untrusted quote verify lib' to verify quote, this mode doesn't rely on
    // SGX capable system, but the results can not be cryptographically authenticated
    dcap_ret = sgx_qv_verify_quote(
        quote.data(),
        (uint32_t)quote.size(),
        NULL,
        current_time,
        &collateral_expiration_status,
        &quote_verification_result,
        NULL, // &qve_report_info
        supplemental_data_size,
        p_supplemental_data);
    if (dcap_ret == SGX_QL_SUCCESS) {
        printf("\tInfo: App: sgx_qv_verify_quote successfully returned.\n");
    }
    else {
        printf("\tError: App: sgx_qv_verify_quote failed: 0x%04x\n", dcap_ret);
    }

    //check verification result
    switch (quote_verification_result) {
        case SGX_QL_QV_RESULT_OK:
            printf("\tInfo: App: Verification completed successfully.\n");
            ret = 0;
            break;
        case SGX_QL_QV_RESULT_CONFIG_NEEDED:
        case SGX_QL_QV_RESULT_OUT_OF_DATE:
        case SGX_QL_QV_RESULT_OUT_OF_DATE_CONFIG_NEEDED:
        case SGX_QL_QV_RESULT_SW_HARDENING_NEEDED:
        case SGX_QL_QV_RESULT_CONFIG_AND_SW_HARDENING_NEEDED:
            printf("\tWarning: App: Verification completed with Non-terminal result: %x\n", quote_verification_result);
            ret = 1;
            break;
        case SGX_QL_QV_RESULT_INVALID_SIGNATURE:
        case SGX_QL_QV_RESULT_REVOKED:
        case SGX_QL_QV_RESULT_UNSPECIFIED:
        default:
            printf("\tError: App: Verification completed with Terminal result: %x\n", quote_verification_result);
            ret = -1;
            break;
    }
    if (ret == 0 || ret == 1) {
        return true;
    }
    else {
        return false;
    }
}
