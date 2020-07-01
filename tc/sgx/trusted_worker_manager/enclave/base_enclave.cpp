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

#include "enclave_common_t.h"

#include <stdlib.h>

#include <cctype>
#include <iterator>

#include <sgx_key.h>
#include <sgx_tcrypto.h>
#include <sgx_trts.h>
#include <sgx_utils.h>  // sgx_get_key, sgx_create_report

#include "auto_handle_sgx.h"

#include "error.h"
#include "avalon_sgx_error.h"
#include "tcf_error.h"
#include "zero.h"

#include "base_enclave.h"
#include "signup_enclave_common.h"
#include "enclave_utils.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// XX External interface                                             XX
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

tcf_err_t ecall_Initialize(uint8_t* persistedSealedEnclaveData,
                           size_t persistedSealedEnclaveDataSize) {
    tcf_err_t result = TCF_SUCCESS;

    // We need to make sure we print a warning if the logging is turned on
    // since it can break confidentiality of workorder execution.
    SAFE_LOG(TCF_LOG_CRITICAL, "enclave initialized with debugging turned on");

    // Initialize Enclave data
    result = persistedSealedEnclaveDataSize > 0 ? \
        CreateEnclaveData(persistedSealedEnclaveData) : CreateEnclaveData();
    return result;
}  // ecall_Initialize

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t ecall_CreateErsatzEnclaveReport(sgx_target_info_t* targetInfo, sgx_report_t* outReport) {
    tcf_err_t result = TCF_SUCCESS;

    try {
        tcf::error::ThrowIfNull(targetInfo, "targetInfo is not valid");
        tcf::error::ThrowIfNull(outReport, "outReport is not valid");

        Zero(outReport, sizeof(*outReport));

        // Create a relatively useless enclave report.  Well....the report
        // itself is not useful for anything except that it can be used to
        // create Intel SGX quotes, which contain potentially useful information
        // (like the enclave basename, mr_enclave, etc.).
        tcf::error::ThrowSgxError(
            sgx_create_report(targetInfo, nullptr, outReport), "Failed to create report.");
    } catch (tcf::error::Error& e) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Error in Avalon enclave(ecall_CreateErsatzEnclaveReport): %04X "
            "-- %s",
            e.error_code(), e.what());
        ocall_SetErrorMessage(e.what());
        result = e.error_code();
    } catch (...) {
        SAFE_LOG(TCF_LOG_ERROR, "Unknown error in Avalon enclave(ecall_CreateErsatzEnclaveReport)");
        result = TCF_ERR_UNKNOWN;
    }

    return result;
}  // ecall_CreateErsatzEnclaveReport
