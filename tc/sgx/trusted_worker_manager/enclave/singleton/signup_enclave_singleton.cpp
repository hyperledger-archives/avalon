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

#include "singleton_enclave_t.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <algorithm>
#include <cctype>
#include <iterator>

#include <sgx_key.h>
#include <sgx_tcrypto.h>
#include <sgx_trts.h>
#include <sgx_utils.h>  // sgx_get_key, sgx_create_report
#include <sgx_quote.h>

#include "crypto.h"
#include "error.h"
#include "avalon_sgx_error.h"
#include "tcf_error.h"
#include "zero.h"
#include "jsonvalue.h"
#include "parson.h"

#include "auto_handle_sgx.h"

#include "base_enclave.h"
#include "enclave_data.h"
#include "enclave_utils.h"
#include "verify-ias-report.h"
#include "signup_enclave_util.h"
#include "epid_signup_helper.h"
#include "dcap_signup_helper.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// XX Declaration of static helper functions                         XX
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

static void CreateSignupReportData(EnclaveData* enclave_data,
    sgx_report_data_t* report_data);

static void CreateReportData(const std::string& enclave_signing_key,
    sgx_report_data_t* report_data);

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t ecall_CreateSignupData(const sgx_target_info_t* inTargetInfo,
    char* outPublicEnclaveData,
    size_t inAllocatedPublicEnclaveDataSize,
    uint8_t* outSealedEnclaveData,
    size_t inAllocatedSealedEnclaveDataSize,
    sgx_report_t* outEnclaveReport) {
    tcf_err_t result = TCF_SUCCESS;

    try {
        tcf::error::ThrowIfNull(inTargetInfo, "Target info pointer is NULL");

        tcf::error::ThrowIfNull(outPublicEnclaveData,
            "Public enclave data pointer is NULL");
        tcf::error::ThrowIfNull(outSealedEnclaveData,
            "Sealed enclave data pointer is NULL");
        tcf::error::ThrowIfNull(outEnclaveReport,
            "Intel SGX report pointer is NULL");

        Zero(outPublicEnclaveData, inAllocatedPublicEnclaveDataSize);
        Zero(outSealedEnclaveData, inAllocatedSealedEnclaveDataSize);

        // Get instance of enclave data
        EnclaveData* enclaveData = EnclaveData::getInstance();

        tcf::error::ThrowIf<tcf::error::ValueError>(
            inAllocatedPublicEnclaveDataSize < enclaveData->get_public_data_size(),
            "Public enclave data buffer size is too small");

        tcf::error::ThrowIf<tcf::error::ValueError>(
            inAllocatedSealedEnclaveDataSize < enclaveData->get_sealed_data_size(),
            "Sealed enclave data buffer size is too small");

        // Create the report data we want embedded in the enclave report.
        sgx_report_data_t reportData = {0};
        CreateSignupReportData(enclaveData, &reportData);

        sgx_status_t ret = sgx_create_report(
            inTargetInfo, &reportData, outEnclaveReport);
        tcf::error::ThrowSgxError(ret, "Failed to create enclave report");

        // Seal up the signup data into the caller's buffer.
        // NOTE - the attributes mask 0xfffffffffffffff3 seems rather
        // arbitrary, but according to Intel SGX SDK documentation, this is
        // what sgx_seal_data uses, so it is good enough for us.
        sgx_attributes_t attribute_mask = {0xfffffffffffffff3, 0};
        ret = sgx_seal_data_ex(SGX_KEYPOLICY_MRENCLAVE, attribute_mask,
            0,        // misc_mask
            0,        // additional mac text length
            nullptr,  // additional mac text
            enclaveData->get_private_data_size(),
            reinterpret_cast<const uint8_t*>(enclaveData->get_private_data().c_str()),
            static_cast<uint32_t>(enclaveData->get_sealed_data_size()),
            reinterpret_cast<sgx_sealed_data_t*>(outSealedEnclaveData));
        tcf::error::ThrowSgxError(ret, "Failed to seal signup data");

        // Give the caller a copy of the signing and encryption keys
        strncpy_s(outPublicEnclaveData, inAllocatedPublicEnclaveDataSize,
            enclaveData->get_public_data().c_str(),
            enclaveData->get_public_data_size());
    } catch (tcf::error::Error& e) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Error in Avalon enclave(ecall_CreateSignupData): %04X -- %s",
            e.error_code(), e.what());
        ocall_SetErrorMessage(e.what());
        result = e.error_code();
    } catch (...) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Unknown error in Avalon enclave(ecall_CreateSignupData)");
        result = TCF_ERR_UNKNOWN;
    }

    return result;
}  // ecall_CreateSignupData

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// XX Helper functions                                      XX
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void CreateSignupReportData(EnclaveData* enclave_data,
    sgx_report_data_t* report_data) {

    // We will put the following in the report data
    // SINGLETON_ENCLAVE: REPORT_DATA[0:31] - SHA256(PUB SIG KEY)
    //                    REPORT_DATA[32:63] - Not used
    
    // WARNING - WARNING - WARNING - WARNING - WARNING - WARNING - WARNING
    //
    // If anything in this code changes the way in which the actual enclave
    // report data is represented, the corresponding code that verifies
    // the report data has to be change accordingly.
    //
    // WARNING - WARNING - WARNING - WARNING - WARNING - WARNING - WARNING

    std::string enclave_signing_key = \
        enclave_data->get_serialized_signing_key();

    // NOTE - we are putting the hash directly into the report
    // data structure because it is (64 bytes) larger than the SHA256
    // hash (32 bytes) but we zero it out first to ensure that it is
    // padded with known data.

    Zero(report_data, sizeof(*report_data));
    ComputeSHA256Hash(enclave_signing_key, report_data->d);
    
}  // CreateSignupReportData

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t ecall_VerifyEnclaveInfoEpid(const char* enclave_info,
    const char* mr_enclave) {

    tcf_err_t result = TCF_SUCCESS;
    EpidSignupHelper signup_helper;
    result = signup_helper.verify_enclave_info(enclave_info, mr_enclave);


    // Verify Report Data by comparing hash of report data in
    // Verification Report with computed report data
    sgx_report_data_t computed_report_data = {0};
    CreateReportData(signup_helper.get_enclave_id(), &computed_report_data);

    //Compare computedReportData with expectedReportData
    sgx_report_data_t expected_report_data = signup_helper.get_report_data();
    tcf::error::ThrowIf<tcf::error::ValueError>(
        memcmp(computed_report_data.d, expected_report_data.d,
        SGX_REPORT_DATA_SIZE)  != 0,
        "Invalid Report data: computedReportData does not match expectedReportData");
    return result;
}  // ecall_VerifyEnclaveInfoEpid

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

tcf_err_t ecall_VerifyEnclaveInfoDcap(const char* enclave_info,
    const char* mr_enclave) {
    tcf_err_t tresult = TCF_SUCCESS;
    DcapSignupHelper signup_helper;
    tresult = signup_helper.verify_enclave_info(enclave_info, mr_enclave);

    tcf::error::ThrowIf<tcf::error::ValueError>(
        tresult != TCF_SUCCESS,
        "Trusted enclave info verification failed");
    // Verify Report Data by comparing hash of report data in
    // Verification Report with computed report data
    sgx_report_data_t computed_report_data = {0};
    CreateReportData(signup_helper.get_enclave_id(), &computed_report_data);

    //Compare computedReportData with expectedReportData
    sgx_report_data_t expected_report_data = signup_helper.get_report_data();
    tcf::error::ThrowIf<tcf::error::ValueError>(
        memcmp(computed_report_data.d, expected_report_data.d,
        SGX_REPORT_DATA_SIZE)  != 0,
        "Invalid Report data: computedReportData does not match expectedReportData");
    Log(TCF_LOG_INFO, "After ecall_VerifyEnclaveInfoDcap");
    return tresult;

}  // ecall_VerifyEnclaveInfoDcap

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void CreateReportData(const std::string& enclave_signing_key,
    sgx_report_data_t* report_data)
{
    // We will put the following in the report data
    // SINGLETON_ENCLAVE: REPORT_DATA[0:31] - SHA256(PUB SIG KEY)
    //

    // NOTE - we are putting the hash directly into the report
    // data structure because it is (64 bytes) larger than the SHA256
    // hash (32 bytes) but we zero it out first to ensure that it is
    // padded with known data.

    Zero(report_data, sizeof(*report_data));
    ComputeSHA256Hash(enclave_signing_key, report_data->d);
    
}  // CreateReportData
