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

#include <string.h>

#include "enclave_common_t.h"

#include "avalon_sgx_error.h"
#include "zero.h"
#include "enclave_utils.h"
#include "signup_enclave_common.h"
#include "enclave_data.h"


// Initializing singleton class object which gets initialized when
// getInstance is called
EnclaveData* EnclaveData::instance = 0;

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t CreateEnclaveData(uint8_t* persistedSealedEnclaveData) {
    tcf_err_t result = TCF_SUCCESS;
    try {
        // Initialize Enclave data
        EnclaveData* enclaveData = persistedSealedEnclaveData == nullptr ? \
            EnclaveData::getInstance() \
            : EnclaveData::getInstance(persistedSealedEnclaveData);
    } catch (...) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Unknown error in while creating enclave data");
        result = TCF_ERR_UNKNOWN;
    }
    return result;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t ecall_CalculateSealedEnclaveDataSize(size_t* pSealedEnclaveDataSize) {
    tcf_err_t result = TCF_SUCCESS;

    try {
        tcf::error::ThrowIfNull(pSealedEnclaveDataSize, "Sealed signup data size pointer is NULL");
        EnclaveData* enclaveData = EnclaveData::getInstance();
        *pSealedEnclaveDataSize = enclaveData->get_sealed_data_size();
    } catch (tcf::error::Error& e) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Error in Avalon enclave(ecall_CalculateSealedEnclaveDataSize): %04X -- %s",
            e.error_code(), e.what());
        ocall_SetErrorMessage(e.what());
        result = e.error_code();
    } catch (...) {
        SAFE_LOG(
            TCF_LOG_ERROR, "Unknown error in Avalon enclave(ecall_CalculateSealedEnclaveDataSize)");
        result = TCF_ERR_UNKNOWN;
    }

    return result;
}  // ecall_CalculateSealedEnclaveDataSize

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t ecall_CalculatePublicEnclaveDataSize(size_t* pPublicEnclaveDataSize) {
    tcf_err_t result = TCF_SUCCESS;

    try {
        tcf::error::ThrowIfNull(pPublicEnclaveDataSize,
            "Public signup data size pointer is NULL");
        EnclaveData* enclaveData = EnclaveData::getInstance();
        *pPublicEnclaveDataSize = enclaveData->get_public_data_size();
    } catch (tcf::error::Error& e) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Error in Avalon enclave(ecall_CalculatePublicEnclaveDataSize): %04X -- %s",
            e.error_code(), e.what());
        ocall_SetErrorMessage(e.what());
        result = e.error_code();
    } catch (...) {
        SAFE_LOG(
            TCF_LOG_ERROR, "Unknown error in Avalon enclave(ecall_CalculatePublicEnclaveDataSize)");
        result = TCF_ERR_UNKNOWN;
    }

    return result;
}  // ecall_CalculatePublicEnclaveDataSize

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t ecall_UnsealEnclaveData(char* outPublicEnclaveData,
    size_t inAllocatedPublicEnclaveDataSize) {
    tcf_err_t result = TCF_SUCCESS;

    try
    {
        tcf::error::ThrowIfNull(outPublicEnclaveData,
            "Public enclave data pointer is NULL");

        Zero(outPublicEnclaveData, inAllocatedPublicEnclaveDataSize);

        // Unseal the enclave data
        EnclaveData* enclaveData = EnclaveData::getInstance();

        tcf::error::ThrowIf<tcf::error::ValueError>(
            inAllocatedPublicEnclaveDataSize < enclaveData->get_public_data_size(),
            "Public enclave data buffer size is too small");

        // Give the caller a copy of the signing and encryption keys
        strncpy_s(outPublicEnclaveData, inAllocatedPublicEnclaveDataSize,
            enclaveData->get_public_data().c_str(),
            enclaveData->get_public_data_size());
    } catch (tcf::error::Error& e) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Error in Avalon enclave(ecall_UnsealEnclaveData): %04X -- %s",
            e.error_code(), e.what());
        ocall_SetErrorMessage(e.what());
        result = e.error_code();
    } catch (...) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Unknown error in Avalon enclave(ecall_UnsealEnclaveData)");
        result = TCF_ERR_UNKNOWN;
    }

    return result;
}  // ecall_UnsealEnclaveData

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t ecall_RefreshWorkerEncryptionKey(
    char* outPublicEnclaveData,
    size_t inAllocatedPublicEnclaveDataSize,
    uint8_t* outSealedEnclaveData,
    size_t inAllocatedSealedEnclaveDataSize) {

    tcf_err_t result = TCF_SUCCESS;

    try {

        tcf::error::ThrowIfNull(outSealedEnclaveData,
            "Sealed enclave data pointer is NULL");

        Zero(outPublicEnclaveData, inAllocatedPublicEnclaveDataSize);
        Zero(outSealedEnclaveData, inAllocatedSealedEnclaveDataSize);

        EnclaveData* enclave_data = EnclaveData::getInstance();
        enclave_data->PerformEncryptionKeyRefresh();
        tcf::error::ThrowIf<tcf::error::ValueError>(
            inAllocatedPublicEnclaveDataSize < enclave_data->get_public_data_size(),
            "Public enclave data buffer size is too small");

        tcf::error::ThrowIf<tcf::error::ValueError>(
            inAllocatedSealedEnclaveDataSize < enclave_data->get_sealed_data_size(),
            "Sealed enclave data buffer size is too small");

        /*
           Seal up the signup data into the caller's buffer.
           NOTE - the attributes mask 0xfffffffffffffff3 seems rather
           arbitrary, but according to Intel SGX SDK documentation, this is
           what sgx_seal_data uses, so it is good enough for us.
        */
        sgx_attributes_t attribute_mask = {0xfffffffffffffff3, 0};
        sgx_status_t ret = sgx_seal_data_ex(SGX_KEYPOLICY_MRENCLAVE, attribute_mask,
            0,        // misc_mask
            0,        // additional mac text length
            nullptr,  // additional mac text
            enclave_data->get_private_data_size(),
            reinterpret_cast<const uint8_t*>(enclave_data->get_private_data().c_str()),
            static_cast<uint32_t>(enclave_data->get_sealed_data_size()),
            reinterpret_cast<sgx_sealed_data_t*>(outSealedEnclaveData));
        tcf::error::ThrowSgxError(ret, "Failed to seal signup data");

        // Give the caller a copy of the signing and encryption keys
        strncpy_s(outPublicEnclaveData, inAllocatedPublicEnclaveDataSize,
            enclave_data->get_public_data().c_str(),
            enclave_data->get_public_data_size());
    } catch (tcf::error::Error& e) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Error in enclave(ecall_RefreshWorkerEncryptionKey): %04X -- %s",
            e.error_code(), e.what());
        ocall_SetErrorMessage(e.what());
        result = e.error_code();
    } catch (...) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Unknown error in enclave(ecall_RefreshWorkerEncryptionKey)");
        result = TCF_ERR_UNKNOWN;
    }
    return result;
}  // ecall_RefreshWorkerEncryptionKey
