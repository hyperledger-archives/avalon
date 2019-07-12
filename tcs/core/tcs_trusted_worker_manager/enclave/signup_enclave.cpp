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

#include "enclave_t.h"

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

#include "crypto.h"
#include "error.h"
#include "tcf_error.h"
#include "zero.h"

#include "auto_handle_sgx.h"

#include "base_enclave.h"
#include "enclave_data.h"
#include "enclave_utils.h"
#include "signup_enclave.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// XX Declaration of static helper functions                         XX
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

static void CreateSignupReportData(const char* pOriginatorPublicKeyHash,
    const EnclaveData& enclaveData,
    sgx_report_data_t* pReportData);

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t ecall_CalculateSealedEnclaveDataSize(size_t* pSealedEnclaveDataSize) {
    tcf_err_t result = TCF_SUCCESS;

    try {
        tcf::error::ThrowIfNull(pSealedEnclaveDataSize, "Sealed signup data size pointer is NULL");

        *pSealedEnclaveDataSize = EnclaveData::cMaxSealedDataSize;
    } catch (tcf::error::Error& e) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Error in tcf enclave(ecall_CalculateSealedEnclaveDataSize): %04X -- %s",
            e.error_code(), e.what());
        ocall_SetErrorMessage(e.what());
        result = e.error_code();
    } catch (...) {
        SAFE_LOG(
            TCF_LOG_ERROR, "Unknown error in tcf enclave(ecall_CalculateSealedEnclaveDataSize)");
        result = TCF_ERR_UNKNOWN;
    }

    return result;
}  // ecall_CalculateSealedEnclaveDataSize

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t ecall_CalculatePublicEnclaveDataSize(size_t* pPublicEnclaveDataSize) {
    tcf_err_t result = TCF_SUCCESS;

    try {
        tcf::error::ThrowIfNull(pPublicEnclaveDataSize, "Publicp signup data size pointer is NULL");

        *pPublicEnclaveDataSize = EnclaveData::cMaxPublicDataSize;
    } catch (tcf::error::Error& e) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Error in tcf enclave(ecall_CalculatePublicEnclaveDataSize): %04X -- %s",
            e.error_code(), e.what());
        ocall_SetErrorMessage(e.what());
        result = e.error_code();
    } catch (...) {
        SAFE_LOG(
            TCF_LOG_ERROR, "Unknown error in tcf enclave(ecall_CalculatePublicEnclaveDataSize)");
        result = TCF_ERR_UNKNOWN;
    }

    return result;
}  // ecall_CalculatePublicEnclaveDataSize

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t ecall_CreateEnclaveData(const sgx_target_info_t* inTargetInfo,
    const char* inOriginatorPublicKeyHash,
    char* outPublicEnclaveData,
    size_t inAllocatedPublicEnclaveDataSize,
    size_t* outPublicEnclaveDataSize,
    uint8_t* outSealedEnclaveData,
    size_t inAllocatedSealedEnclaveDataSize,
    size_t* outSealedEnclaveDataSize,
    sgx_report_t* outEnclaveReport) {
    tcf_err_t result = TCF_SUCCESS;

    try {
        tcf::error::ThrowIfNull(inTargetInfo, "Target info pointer is NULL");
        tcf::error::ThrowIfNull(
            inOriginatorPublicKeyHash, "Originator public key hash pointer is NULL");

        tcf::error::ThrowIfNull(outPublicEnclaveData, "Public enclave data pointer is NULL");
        tcf::error::ThrowIfNull(outPublicEnclaveDataSize, "Public data size pointer is NULL");

        tcf::error::ThrowIfNull(outSealedEnclaveData, "Sealed enclave data pointer is NULL");
        tcf::error::ThrowIfNull(outSealedEnclaveDataSize, "Sealed data size pointer is NULL");

        tcf::error::ThrowIfNull(outEnclaveReport, "SGX report pointer is NULL");

        (*outPublicEnclaveDataSize) = 0;
        Zero(outPublicEnclaveData, inAllocatedPublicEnclaveDataSize);

        (*outSealedEnclaveDataSize) = 0;
        Zero(outSealedEnclaveData, inAllocatedSealedEnclaveDataSize);

        // Create the enclave data
        EnclaveData enclaveData;

        tcf::error::ThrowIf<tcf::error::ValueError>(
            inAllocatedPublicEnclaveDataSize < enclaveData.get_public_data_size(),
            "Public enclave data buffer size is too small");

        tcf::error::ThrowIf<tcf::error::ValueError>(
            inAllocatedSealedEnclaveDataSize < enclaveData.get_sealed_data_size(),
            "Sealed enclave data buffer size is too small");

        // pass back the actual size of the enclave data
        (*outPublicEnclaveDataSize) = enclaveData.get_public_data_size();
        (*outSealedEnclaveDataSize) = enclaveData.get_sealed_data_size();

        // Create the report data we want embedded in the enclave report.
        sgx_report_data_t reportData = {0};
        CreateSignupReportData(inOriginatorPublicKeyHash, enclaveData, &reportData);

        sgx_status_t ret = sgx_create_report(inTargetInfo, &reportData, outEnclaveReport);
        tcf::error::ThrowSgxError(ret, "Failed to create enclave report");

        // Seal up the signup data into the caller's buffer.
        // NOTE - the attributes mask 0xfffffffffffffff3 seems rather
        // arbitrary, but according to SGX SDK documentation, this is
        // what sgx_seal_data uses, so it is good enough for us.
        sgx_attributes_t attribute_mask = {0xfffffffffffffff3, 0};
        ret = sgx_seal_data_ex(SGX_KEYPOLICY_MRENCLAVE, attribute_mask,
            0,        // misc_mask
            0,        // additional mac text length
            nullptr,  // additional mac text
            enclaveData.get_private_data_size(),
            reinterpret_cast<const uint8_t*>(enclaveData.get_private_data().c_str()),
            static_cast<uint32_t>(*outSealedEnclaveDataSize),
            reinterpret_cast<sgx_sealed_data_t*>(outSealedEnclaveData));
        tcf::error::ThrowSgxError(ret, "Failed to seal signup data");

        // Give the caller a copy of the signing and encryption keys
        strncpy_s(outPublicEnclaveData, inAllocatedPublicEnclaveDataSize,
            enclaveData.get_public_data().c_str(),
            enclaveData.get_public_data_size());
    } catch (tcf::error::Error& e) {
        SAFE_LOG(TCF_LOG_ERROR, "Error in tcf enclave(ecall_CreateEnclaveData): %04X -- %s",
            e.error_code(), e.what());
        ocall_SetErrorMessage(e.what());
        result = e.error_code();
    } catch (...) {
        SAFE_LOG(TCF_LOG_ERROR, "Unknown error in tcf enclave(ecall_CreateEnclaveData)");
        result = TCF_ERR_UNKNOWN;
    }

    return result;
}  // ecall_CreateEnclaveData

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t ecall_UnsealEnclaveData(const uint8_t* inSealedEnclaveData,
    size_t inSealedEnclaveDataSize,
    char* outPublicEnclaveData,
    size_t inAllocatedPublicEnclaveDataSize,
    size_t* outPublicEnclaveDataSize) {
    tcf_err_t result = TCF_SUCCESS;

    try
    {
        tcf::error::ThrowIfNull(inSealedEnclaveData, "SealedEnclaveData pointer is NULL");

        tcf::error::ThrowIfNull(outPublicEnclaveData, "Public enclave data pointer is NULL");
        tcf::error::ThrowIfNull(outPublicEnclaveDataSize, "Public data size pointer is NULL");

        (*outPublicEnclaveDataSize) = 0;
        Zero(outPublicEnclaveData, inAllocatedPublicEnclaveDataSize);

        // Unseal the enclave data
        EnclaveData enclaveData(inSealedEnclaveData);

        tcf::error::ThrowIf<tcf::error::ValueError>(
            inAllocatedPublicEnclaveDataSize < enclaveData.get_public_data_size(),
            "Public enclave data buffer size is too small");

        (*outPublicEnclaveDataSize) = enclaveData.get_public_data_size();

        // Give the caller a copy of the signing and encryption keys
        strncpy_s(outPublicEnclaveData, inAllocatedPublicEnclaveDataSize,
            enclaveData.get_public_data().c_str(),
            enclaveData.get_public_data_size());
    } catch (tcf::error::Error& e) {
        SAFE_LOG(TCF_LOG_ERROR, "Error in tcf enclave(ecall_UnsealEnclaveData): %04X -- %s",
            e.error_code(), e.what());
        ocall_SetErrorMessage(e.what());
        result = e.error_code();
    } catch (...) {
        SAFE_LOG(TCF_LOG_ERROR, "Unknown error in tcf enclave(ecall_UnsealEnclaveData)");
        result = TCF_ERR_UNKNOWN;
    }

    return result;
}  // ecall_UnsealEnclaveData

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// XX Internal helper functions                                      XX
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void CreateSignupReportData(const char* pOriginatorPublicKeyHash,
    const EnclaveData& enclaveData,
    sgx_report_data_t* pReportData) {
    // We will put the following in the report data SHA256(PPK|PEK|OPK_HASH)

    // WARNING - WARNING - WARNING - WARNING - WARNING - WARNING - WARNING
    //
    // If anything in this code changes the way in which the actual enclave
    // report data is represented, the corresponding code that verifies
    // the report data has to be change accordingly.
    //
    // WARNING - WARNING - WARNING - WARNING - WARNING - WARNING - WARNING
    std::string hashString;

    hashString.append(enclaveData.get_serialized_signing_key());
    hashString.append(enclaveData.get_serialized_encryption_key());

    // Canonicalize the originator public key hash string to ensure a consistent
    // format.
    std::transform(pOriginatorPublicKeyHash,
        pOriginatorPublicKeyHash + strlen(pOriginatorPublicKeyHash), std::back_inserter(hashString),
        [](char c) {
            return c;  // do nothing
        });

    // Now we put the SHA256 hash into the report data for the
    // report we will request.
    //
    // NOTE - we are putting the hash directly into the report
    // data structure because it is (64 bytes) larger than the SHA256
    // hash (32 bytes) but we zero it out first to ensure that it is
    // padded with known data.
    Zero(pReportData, sizeof(*pReportData));
    sgx_status_t ret = sgx_sha256_msg(reinterpret_cast<const uint8_t*>(hashString.c_str()),
        static_cast<uint32_t>(hashString.size()),
        reinterpret_cast<sgx_sha256_hash_t*>(pReportData));
    tcf::error::ThrowSgxError(ret, "Failed to retrieve SHA256 hash of report data");
}  // CreateSignupReportData
