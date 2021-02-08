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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <sgx_key.h>
#include <sgx_tcrypto.h>
#include <sgx_trts.h>
#include "sgx_utils.h"
#include "sgx_report.h"
#include "sgx_error.h"
#include "sgx_quote_3.h"

#include "crypto.h"
#include "types.h"
#include "utils.h"
#include "error.h"
#include "avalon_sgx_error.h"
#include "jsonvalue.h"
#include "parson.h"

#include "auto_handle_sgx.h"

#include "signup_enclave_util.h"
#include "dcap_signup_helper.h"
#include "enclave_utils.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t DcapSignupHelper::verify_enclave_info(const char* enclave_info,
    const char* mr_enclave) {

    tcf_err_t result = TCF_SUCCESS;

    // Parse the enclave_info
    JsonValue enclave_info_parsed(json_parse_string(enclave_info));
    tcf::error::ThrowIfNull(enclave_info_parsed.value,
        "Failed to parse the enclave info, badly formed JSON");

    JSON_Object* enclave_info_object = \
        json_value_get_object(enclave_info_parsed);
    tcf::error::ThrowIfNull(enclave_info_object,
        "Invalid enclave_info, expecting object");

    const char* svalue = nullptr;
    svalue = json_object_dotget_string(enclave_info_object, "verifying_key");
    tcf::error::ThrowIfNull(svalue, "Invalid verifying_key");
    this->enclave_id = svalue;

    svalue = json_object_dotget_string(enclave_info_object, "encryption_key");
    tcf::error::ThrowIfNull(svalue, "Invalid encryption_key");
    this->enclave_encryption_key = svalue;

    // Parse proof data
    svalue = json_object_dotget_string(enclave_info_object, "proof_data");
    std::string proof_data(svalue);
    JsonValue proof_data_parsed(json_parse_string(proof_data.c_str()));
    tcf::error::ThrowIfNull(proof_data_parsed.value,
        "Failed to parse the proofData, badly formed JSON");
    JSON_Object* proof_object = json_value_get_object(proof_data_parsed);
    tcf::error::ThrowIfNull(proof_object, "Invalid proof, expecting object");

    svalue = json_object_dotget_string(proof_object, "report_signature");
    tcf::error::ThrowIfNull(svalue, "Invalid proof_signature");
    const std::string proof_signature(svalue);

    //Parse verification report
    svalue = json_object_dotget_string(proof_object, "verification_report");
    tcf::error::ThrowIfNull(svalue, "Invalid proof_verification_report");
    const std::string verification_report(svalue);

    // Extract ReportData and MR_ENCLAVE from isvEnclaveQuoteBody
    // present in Verification Report
    ByteArray mr_enclave_bytes = HexEncodedStringToByteArray(mr_enclave);
    sgx_quote3_t* p_quote = reinterpret_cast<sgx_quote3_t*>(
        Base64EncodedStringToByteArray(verification_report).data());
    sgx_report_body_t* report_body = &p_quote->report_body;
    this->report_data = *(&report_body->report_data);
    sgx_measurement_t mr_enclave_from_report = *(&report_body->mr_enclave);

    //CHECK MR_ENCLAVE
    tcf::error::ThrowIf<tcf::error::ValueError>(
        memcmp(mr_enclave_from_report.m, mr_enclave_bytes.data(),
            SGX_HASH_SIZE)  != 0, "Invalid MR_ENCLAVE");

    return result;
}  // verify_enclave_info

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

VerificationStatus DcapSignupHelper::verify_attestation_report(
    const ByteArray& attestation_data,
    const ByteArray& hex_id,
    ByteArray& mr_enclave,
    ByteArray& mr_signer,
    ByteArray& encryption_public_key_hash,
    ByteArray& verification_key_hash) {

    const char* svalue = nullptr;
    /// Verify attestation report
    VerificationStatus result = VERIFICATION_SUCCESS;
    std::string att_data_string = ByteArrayToString(attestation_data);
    /// Parse the attestation data
    JsonValue proof_data_parsed(json_parse_string(att_data_string.c_str()));
    tcf::error::ThrowIfNull(proof_data_parsed.value,
        "Failed to parse the proofData, badly formed JSON");
    JSON_Object* proof_object = json_value_get_object(proof_data_parsed);
    tcf::error::ThrowIfNull(proof_object, "Invalid proof, expecting object");

    svalue = json_object_dotget_string(proof_object, "report_signature");
    tcf::error::ThrowIfNull(svalue, "Invalid proof_signature");
    const std::string proof_signature(svalue);

    //Parse verification report
    svalue = json_object_dotget_string(proof_object, "verification_report");
    tcf::error::ThrowIfNull(svalue, "Invalid proof_verification_report");
    const std::string verification_report(svalue);
    //TODO: Do app quote verification and verify qve report and identity

    // Extract ReportData and MR_ENCLAVE from isvEnclaveQuoteBody
    // present in Verification Report
    sgx_quote3_t* p_quote = reinterpret_cast<sgx_quote3_t*>(
        Base64EncodedStringToByteArray(verification_report).data());
    sgx_report_body_t* report_body = &p_quote->report_body;
    sgx_report_data_t expected_report_data = *(&report_body->report_data);
    sgx_measurement_t mr_enclave_from_report = *(&report_body->mr_enclave);
    sgx_measurement_t mr_signer_from_report = *(&report_body->mr_signer);

    /// Convert uint8_t array to ByteArray(vector<uint8_t>)
    ByteArray mr_enclave_bytes(std::begin(mr_enclave_from_report.m),
        std::end(mr_enclave_from_report.m));
    ByteArray mr_signer_bytes(std::begin(mr_signer_from_report.m),
        std::end(mr_signer_from_report.m));
    mr_enclave = mr_enclave_bytes;
    mr_signer = mr_signer_bytes;


    encryption_public_key_hash = ByteArray(std::begin(expected_report_data.d),
                                     std::begin(expected_report_data.d)+SGX_HASH_SIZE);
    verification_key_hash = ByteArray(std::begin(expected_report_data.d)+SGX_HASH_SIZE,
                                     std::end(expected_report_data.d));
    return result;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
