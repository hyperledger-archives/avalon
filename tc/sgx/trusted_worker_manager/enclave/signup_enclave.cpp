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
#include "signup_enclave.h"
#include "verify-report.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// XX Declaration of static helper functions                         XX
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

static void CreateSignupReportData(const char* pOriginatorPublicKeyHash,
    const EnclaveData& enclaveData,
    sgx_report_data_t* pReportData);

void CreateReportData(const char* pOriginatorPublicKeyHash,
    std::string& enclaveId,
    std::string& enclaveEncryptKey,
    sgx_report_data_t* pReportData);

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t ecall_CalculateSealedEnclaveDataSize(size_t* pSealedEnclaveDataSize) {
    tcf_err_t result = TCF_SUCCESS;

    try {
        tcf::error::ThrowIfNull(pSealedEnclaveDataSize, "Sealed signup data size pointer is NULL");

        *pSealedEnclaveDataSize = EnclaveData::cMaxSealedDataSize;
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
        tcf::error::ThrowIfNull(pPublicEnclaveDataSize, "Publicp signup data size pointer is NULL");

        *pPublicEnclaveDataSize = EnclaveData::cMaxPublicDataSize;
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

        tcf::error::ThrowIfNull(outEnclaveReport,
            "Intel SGX report pointer is NULL");

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

        // Pass back the actual size of the enclave data
        (*outPublicEnclaveDataSize) = enclaveData.get_public_data_size();
        (*outSealedEnclaveDataSize) = enclaveData.get_sealed_data_size();

        // Create the report data we want embedded in the enclave report.
        sgx_report_data_t reportData = {0};
        CreateSignupReportData(inOriginatorPublicKeyHash, enclaveData, &reportData);

        sgx_status_t ret = sgx_create_report(inTargetInfo, &reportData, outEnclaveReport);
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
        SAFE_LOG(TCF_LOG_ERROR, "Error in Avalon enclave(ecall_CreateEnclaveData): %04X -- %s",
            e.error_code(), e.what());
        ocall_SetErrorMessage(e.what());
        result = e.error_code();
    } catch (...) {
        SAFE_LOG(TCF_LOG_ERROR, "Unknown error in Avalon enclave(ecall_CreateEnclaveData)");
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
        SAFE_LOG(TCF_LOG_ERROR, "Error in Avalon enclave(ecall_UnsealEnclaveData): %04X -- %s",
            e.error_code(), e.what());
        ocall_SetErrorMessage(e.what());
        result = e.error_code();
    } catch (...) {
        SAFE_LOG(TCF_LOG_ERROR, "Unknown error in Avalon enclave(ecall_UnsealEnclaveData)");
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

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t ecall_VerifyEnclaveInfo(const char* enclave_info,
                                  const char* mr_enclave,
                                  const char* originator_public_key_hash) {
    tcf_err_t result = TCF_SUCCESS;
    // Parse the enclave_info
    JsonValue enclave_info_parsed(json_parse_string(enclave_info));
    tcf::error::ThrowIfNull(enclave_info_parsed.value, "Failed to parse the enclave info, badly formed JSON");

    JSON_Object* enclave_info_object = json_value_get_object(enclave_info_parsed);
    tcf::error::ThrowIfNull(enclave_info_object, "Invalid enclave_info, expecting object");

    const char* svalue = nullptr;
    svalue = json_object_dotget_string(enclave_info_object, "verifying_key");
    tcf::error::ThrowIfNull(svalue, "Invalid verifying_key");
    std::string enclave_id(svalue);

    svalue = json_object_dotget_string(enclave_info_object, "encryption_key");
    tcf::error::ThrowIfNull(svalue, "Invalid encryption_key");
    std::string enclave_encrypt_key(svalue);

    // Parse proof data
    svalue = json_object_dotget_string(enclave_info_object, "proof_data");
    std::string proof_data(svalue);

    JsonValue proof_data_parsed(json_parse_string(proof_data.c_str()));
    tcf::error::ThrowIfNull(proof_data_parsed.value, "Failed to parse the proofData, badly formed JSON");
    JSON_Object* proof_object = json_value_get_object(proof_data_parsed);
    tcf::error::ThrowIfNull(proof_object, "Invalid proof, expecting object");

    svalue = json_object_dotget_string(proof_object, "ias_report_signature");
    tcf::error::ThrowIfNull(svalue, "Invalid proof_signature");
    const std::string proof_signature(svalue);

    //Parse verification report
    svalue = json_object_dotget_string(proof_object, "verification_report");
    tcf::error::ThrowIfNull(svalue, "Invalid proof_verification_report");
    const std::string verification_report(svalue);

    JsonValue verification_report_parsed(json_parse_string(verification_report.c_str()));
    tcf::error::ThrowIfNull(verification_report_parsed.value, "Failed to parse the verificationReport, badly formed JSON");

    JSON_Object* verification_report_object = json_value_get_object(verification_report_parsed);
    tcf::error::ThrowIfNull(verification_report_object, "Invalid verification_report, expecting object");

    svalue = json_object_dotget_string(verification_report_object, "isvEnclaveQuoteBody");
    tcf::error::ThrowIfNull(svalue, "Invalid enclave_quote_body");
    const std::string enclave_quote_body(svalue);

    svalue = json_object_dotget_string(verification_report_object, "epidPseudonym");
    tcf::error::ThrowIfNull(svalue, "Invalid epid_pseudonym");
    const std::string epid_pseudonym(svalue);

    // Verify verification report signature
    // Verify good quote, but group-of-date is not considered ok
    bool r = verify_enclave_quote_status(verification_report.c_str(), verification_report.length(), 1);
    tcf::error::ThrowIf<tcf::error::ValueError>(
        r!=true, "Invalid Enclave Quote:  group-of-date NOT OKAY");

    const char* ias_report_cert = json_object_dotget_string(proof_object, "ias_report_signing_certificate");

    std::vector<char> verification_report_vec(verification_report.begin(), verification_report.end());
    verification_report_vec.push_back('\0');
    char* verification_report_arr = &verification_report_vec[0];

    std::vector<char> proof_signature_vec(proof_signature.begin(), proof_signature.end());
    proof_signature_vec.push_back('\0');
    char* proof_signature_arr = &proof_signature_vec[0];

    //verify IAS signature
    r = verify_ias_report_signature(ias_report_cert,
                                    verification_report_arr,
                                    strlen(verification_report_arr),
                                    proof_signature_arr,
                                    strlen(proof_signature_arr));
    tcf::error::ThrowIf<tcf::error::ValueError>(
    r!=true, "Invalid verificationReport; Invalid Signature");

    //Extract ReportData and MR_ENCLAVE from isvEnclaveQuoteBody in Verification Report
    sgx_quote_t* quote_body = reinterpret_cast<sgx_quote_t*>(Base64EncodedStringToByteArray(enclave_quote_body).data());
    sgx_report_body_t* report_body = &quote_body->report_body;
    sgx_report_data_t expected_report_data = *(&report_body->report_data);
    sgx_measurement_t mr_enclave_from_report = *(&report_body->mr_enclave);
    sgx_basename_t mr_basename_from_report = *(&quote_body->basename);

    ByteArray mr_enclave_bytes = HexEncodedStringToByteArray(mr_enclave);
    //CHECK MR_ENCLAVE
    tcf::error::ThrowIf<tcf::error::ValueError>(
        memcmp(mr_enclave_from_report.m, mr_enclave_bytes.data(), SGX_HASH_SIZE)  != 0,
        "Invalid MR_ENCLAVE");

    //Verify Report Data by comparing hash of report data in Verification Report with computed report data
    sgx_report_data_t computed_report_data = {0};
    CreateReportData(originator_public_key_hash, enclave_id, enclave_encrypt_key, &computed_report_data);

    //Compare computedReportData with expectedReportData
    tcf::error::ThrowIf<tcf::error::ValueError>(
        memcmp(computed_report_data.d, expected_report_data.d, SGX_REPORT_DATA_SIZE)  != 0,
        "Invalid Report data: computedReportData does not match expectedReportData");

    return result;
}  // ecall_VerifyEnclaveInfo

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void CreateReportData(const char* originator_public_key_hash,
    std::string& enclave_id,
    std::string& enclave_encrypt_key,
    sgx_report_data_t* report_data)
{
    // We will put the following in the report data SHA256(PPK|PEK|OPK_HASH)

    // WARNING - WARNING - WARNING - WARNING - WARNING - WARNING - WARNING
    //
    // If anything in this code changes the way in which the actual enclave
    // report data is represented, the corresponding code that creates
    // the report data has to be change accordingly.
    //
    // WARNING - WARNING - WARNING - WARNING - WARNING - WARNING - WARNING
    std::string hash_string;

    tcf::crypto::sig::PublicKey signing_key(enclave_id);
    tcf::crypto::pkenc::PublicKey enclave_key(enclave_encrypt_key);

    hash_string.append(signing_key.Serialize());
    hash_string.append(enclave_key.Serialize());

    // Canonicalize the originator public key hash string to ensure a consistent
    // format.
    std::transform(originator_public_key_hash,
        originator_public_key_hash + strlen(originator_public_key_hash), std::back_inserter(hash_string),
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
    Zero(report_data, sizeof(*report_data));
    sgx_status_t ret = sgx_sha256_msg(reinterpret_cast<const uint8_t*>(hash_string.c_str()),
        static_cast<uint32_t>(hash_string.size()),
        reinterpret_cast<sgx_sha256_hash_t*>(report_data));
    tcf::error::ThrowSgxError(ret, "Failed to retrieve SHA256 hash of report data");
}  // CreateReportData

