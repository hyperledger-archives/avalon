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
#include <sgx_quote.h>

#include "crypto.h"
#include "error.h"
#include "avalon_sgx_error.h"
#include "tcf_error.h"
#include "jsonvalue.h"
#include "parson.h"

#include "auto_handle_sgx.h"

#include "verify-ias-report.h"
#include "signup_enclave_util.h"
#include "epid_signup_helper.h"


// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t EpidSignupHelper::verify_enclave_info(const char* enclave_info,
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

    svalue = json_object_dotget_string(proof_object, "ias_report_signature");
    tcf::error::ThrowIfNull(svalue, "Invalid proof_signature");
    const std::string proof_signature(svalue);

    //Parse verification report
    svalue = json_object_dotget_string(proof_object, "verification_report");
    tcf::error::ThrowIfNull(svalue, "Invalid proof_verification_report");
    const std::string verification_report(svalue);

    JsonValue verification_report_parsed(
        json_parse_string(verification_report.c_str()));
    tcf::error::ThrowIfNull(verification_report_parsed.value,
        "Failed to parse the verificationReport, badly formed JSON");

    JSON_Object* verification_report_object = \
        json_value_get_object(verification_report_parsed);
    tcf::error::ThrowIfNull(verification_report_object,
        "Invalid verification_report, expecting object");

    svalue = json_object_dotget_string(verification_report_object,
        "isvEnclaveQuoteBody");
    tcf::error::ThrowIfNull(svalue, "Invalid enclave_quote_body");
    const std::string enclave_quote_body(svalue);

    svalue = json_object_dotget_string(
        verification_report_object, "epidPseudonym");
    tcf::error::ThrowIfNull(svalue, "Invalid epid_pseudonym");
    const std::string epid_pseudonym(svalue);

    // Verify verification report signature
    // Verify good quote, but group-of-date is not considered ok
    bool r = verify_enclave_quote_status(verification_report.c_str(),
        verification_report.length(), 1);
    tcf::error::ThrowIf<tcf::error::ValueError>(
        r!=true, "Invalid Enclave Quote:  group-of-date NOT OKAY");

    const char* ias_report_cert = json_object_dotget_string(
        proof_object, "ias_report_signing_certificate");

    std::vector<char> verification_report_vec(
        verification_report.begin(), verification_report.end());
    verification_report_vec.push_back('\0');
    char* verification_report_arr = &verification_report_vec[0];

    std::vector<char> proof_signature_vec(proof_signature.begin(),
        proof_signature.end());
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

    // Extract ReportData and MR_ENCLAVE from isvEnclaveQuoteBody
    // present in Verification Report
    sgx_quote_t* quote_body = reinterpret_cast<sgx_quote_t*>(
        Base64EncodedStringToByteArray(enclave_quote_body).data());
    sgx_report_body_t* report_body = &quote_body->report_body;
    this->report_data = *(&report_body->report_data);
    sgx_measurement_t mr_enclave_from_report = *(&report_body->mr_enclave);
    sgx_basename_t mr_basename_from_report = *(&quote_body->basename);

    ByteArray mr_enclave_bytes = HexEncodedStringToByteArray(mr_enclave);
    //CHECK MR_ENCLAVE
    tcf::error::ThrowIf<tcf::error::ValueError>(
        memcmp(mr_enclave_from_report.m, mr_enclave_bytes.data(),
            SGX_HASH_SIZE)  != 0, "Invalid MR_ENCLAVE");

    return result;
}  // Epid_VerifyEnclaveInfo

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
VerificationStatus EpidSignupHelper::verify_attestation_report(
    const ByteArray& attestation_data,
    const ByteArray& hex_id,
    ByteArray& mr_enclave, ByteArray& mr_signer,
    ByteArray& encryption_public_key_hash,
    ByteArray& verification_key_hash) {

    /// Verify attestation report
    VerificationStatus result = VERIFICATION_SUCCESS;
    std::string att_data_string = ByteArrayToString(attestation_data);
    /// Parse the attestation data
    JsonValue att_data_string_parsed(json_parse_string(
        att_data_string.c_str()));
    if (att_data_string_parsed.value == nullptr) {
	tcf::error::ThrowIf<tcf::error::ValueError>(true, "Parsing attestation data failed");
        return VERIFICATION_FAILED;
    }
    JSON_Object* proof_object = \
        json_value_get_object(att_data_string_parsed);
    if (proof_object == nullptr) {
        tcf::error::ThrowIf<tcf::error::ValueError>(true, "Get proof data json object failed");
        return VERIFICATION_FAILED;
    }

    const char* s_value = nullptr;

    s_value = json_object_dotget_string(proof_object, "ias_report_signature");
    if (s_value == nullptr) {
	tcf::error::ThrowIf<tcf::error::ValueError>(true,
			"Extracting ias_report_signature from proof_data failed");
        return VERIFICATION_FAILED;
    }
    const std::string proof_signature(s_value);

    /// Parse verification report
    s_value = json_object_dotget_string(proof_object, "verification_report");
    if (s_value == nullptr) {
	tcf::error::ThrowIf<tcf::error::ValueError>(true,
			"Extracting verification_report from proof_data failed");
        return VERIFICATION_FAILED;
    }
    const std::string verification_report(s_value);

    JsonValue verification_report_parsed(
        json_parse_string(verification_report.c_str()));
    if (verification_report_parsed.value == nullptr) {
	tcf::error::ThrowIf<tcf::error::ValueError>(true, "Parsing verification report failed");
        return VERIFICATION_FAILED;
    }

    JSON_Object* verification_report_object = \
        json_value_get_object(verification_report_parsed);
    if (verification_report_object == nullptr) {
	tcf::error::ThrowIf<tcf::error::ValueError>(true,
	    "Get verification report json object failed");
        return VERIFICATION_FAILED;
    }

    s_value = json_object_dotget_string(verification_report_object,
        "isvEnclaveQuoteBody");
    if (s_value == nullptr) {
	tcf::error::ThrowIf<tcf::error::ValueError>(true, "Extracting isvEnclaveQuoteBody failed");
        return VERIFICATION_FAILED;
    }
    const std::string enclave_quote_body(s_value);

    s_value = json_object_dotget_string(
        verification_report_object, "epidPseudonym");
    if (s_value == nullptr) {
        tcf::error::ThrowIf<tcf::error::ValueError>(true, "Extracting epidPseudonym failed");
        return VERIFICATION_FAILED;
    }
    const std::string epid_pseudonym(s_value);

    /* Verify verification report signature
       Verify good quote, but group-of-date is not considered ok */
    bool r = verify_enclave_quote_status(verification_report.c_str(),
        verification_report.length(), 1);
    if (r != true) {
	tcf::error::ThrowIf<tcf::error::ValueError>(true, "Verifying enclave quote failed");
        return VERIFICATION_FAILED;
    }
    const char* ias_report_cert = json_object_dotget_string(
        proof_object, "ias_report_signing_certificate");

    std::vector<char> verification_report_vec(
        verification_report.begin(), verification_report.end());
    verification_report_vec.push_back('\0');
    char* verification_report_arr = &verification_report_vec[0];

    std::vector<char> proof_signature_vec(proof_signature.begin(),
        proof_signature.end());
    proof_signature_vec.push_back('\0');
    char* proof_signature_arr = &proof_signature_vec[0];

    /// verify IAS signature
    r = verify_ias_report_signature(ias_report_cert,
                                    verification_report_arr,
                                    strlen(verification_report_arr),
                                    proof_signature_arr,
                                    strlen(proof_signature_arr));
    if (r != true) {
        tcf::error::ThrowIf<tcf::error::ValueError>(true, "Verifying ias report signature failed");
        return VERIFICATION_FAILED;
    }

    /* Extract ReportData and MR_ENCLAVE from isvEnclaveQuoteBody
       present in Verification Report */
    sgx_quote_t* quote_body = reinterpret_cast<sgx_quote_t*>(
        Base64EncodedStringToByteArray(enclave_quote_body).data());
    sgx_report_body_t* report_body = &quote_body->report_body;
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
