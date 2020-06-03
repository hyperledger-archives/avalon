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

#include <sgx_utils.h>
#include <sgx_quote.h>

#include "ext_work_order_info_impl.h"
#include "enclave_data.h"
#include "error.h"
#include "parson.h"
#include "jsonvalue.h"
#include "utils.h"
#include "verify-report.h"
#include "enclave_utils.h"
#include "signup_enclave_util.h"

using namespace tcf::error;

ExtWorkOrderInfoImpl::ExtWorkOrderInfoImpl() {}

ExtWorkOrderInfoImpl::~ExtWorkOrderInfoImpl() {}

size_t ExtWorkOrderInfoImpl::GetWorkOrderExData(ByteArray& data) {
    // To be implemented
    return 0;
}  // ExtWorkOrderInfoImpl::GetWorkOrderExData

int ExtWorkOrderInfoImpl::VerifyAttestation(const ByteArray& attestation_data,
    ByteArray& mr_enclave, ByteArray& mr_signer,
    ByteArray& verification_key_hash, ByteArray& encryption_pub_key) {

    /// Verify attestation report
    VerificationStatus result = VERIFICATION_SUCCESS;
    std::string att_data_string = ByteArrayToString(attestation_data);
    Log(TCF_LOG_INFO,"\n\n\n VerifyAttestation attestion_data %s\n\n\n", att_data_string);
    /// Parse the att_string
    JsonValue att_data_string_parsed(json_parse_string(
        att_data_string.c_str()));
    if (att_data_string_parsed.value == nullptr) {
	ThrowIf<ValueError>(true, "Parsing attestion data failed");
        return VERIFICATION_FAILED;
    }
    JSON_Object* att_data_json_object = \
        json_value_get_object(att_data_string_parsed);
    if (att_data_json_object == nullptr) {
	ThrowIf<ValueError>(true, "Creating json object failed");
        return VERIFICATION_FAILED;
    }

    const char* s_value = nullptr;
    s_value = json_object_dotget_string(att_data_json_object, "verifying_key");
    if (s_value == nullptr) {
	ThrowIf<ValueError>(true,
			"Extracting verifying_key from report failed");
        return VERIFICATION_FAILED;
    }
    
    s_value = json_object_dotget_string(att_data_json_object, "encryption_key");
    if (s_value == nullptr) {
	ThrowIf<ValueError>(true,
			"Extracting encryption_key from report failed");
        return VERIFICATION_FAILED;
    }
    std::string e_key(s_value);
    encryption_pub_key = StrToByteArray(e_key);

    /// Parse proof data
    s_value = json_object_dotget_string(att_data_json_object, "proof_data");
    std::string proof_data(s_value);
    JsonValue proof_data_parsed(json_parse_string(proof_data.c_str()));
    if (proof_data_parsed == nullptr) {
	ThrowIf<ValueError>(true, "Extracting proof_data from report failed");
        return VERIFICATION_FAILED;
    }
    JSON_Object* proof_object = json_value_get_object(proof_data_parsed);
    if (proof_object == nullptr) {
	ThrowIf<ValueError>(true, "Parsing proof_data json failed");
        return VERIFICATION_FAILED;
    }

    s_value = json_object_dotget_string(proof_object, "ias_report_signature");
    if (s_value == nullptr) {
	ThrowIf<ValueError>(true,
			"Extracting ias_report_signature from proof_data failed");
        return VERIFICATION_FAILED;
    }
    const std::string proof_signature(s_value);

    /// Parse verification report
    s_value = json_object_dotget_string(proof_object, "verification_report");
    if (s_value == nullptr) {
	ThrowIf<ValueError>(true,
			"Extracting verification_report from proof_data failed");
        return VERIFICATION_FAILED;
    }
    const std::string verification_report(s_value);

    JsonValue verification_report_parsed(
        json_parse_string(verification_report.c_str()));
    if (verification_report_parsed.value == nullptr) {
	ThrowIf<ValueError>(true, "Parsing verification report failed");
        return VERIFICATION_FAILED;
    }

    JSON_Object* verification_report_object = \
        json_value_get_object(verification_report_parsed);
    if (verification_report_object == nullptr) {
	ThrowIf<ValueError>(true,
			"Creating verification report json object failed");
        return VERIFICATION_FAILED;
    }

    s_value = json_object_dotget_string(verification_report_object,
        "isvEnclaveQuoteBody");
    if (s_value == nullptr) {
	ThrowIf<ValueError>(true, "Extracting isvEnclaveQuoteBody failed");
        return VERIFICATION_FAILED;
    }
    const std::string enclave_quote_body(s_value);

    s_value = json_object_dotget_string(
        verification_report_object, "epidPseudonym");
    if (s_value == nullptr) {
	ThrowIf<ValueError>(true, "Extracting epidPseudonym failed");
        return VERIFICATION_FAILED;
    }
    const std::string epid_pseudonym(s_value);

    /* Verify verification report signature
       Verify good quote, but group-of-date is not considered ok */
    bool r = verify_enclave_quote_status(verification_report.c_str(),
        verification_report.length(), 1);
    if (r != true) {
	ThrowIf<ValueError>(true, "Verifying enclave quote failed");
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
	ThrowIf<ValueError>(true, "Verifying ias report signature failed");
        return VERIFICATION_FAILED;
    }

    /* Extract ReportData and MR_ENCLAVE from isvEnclaveQuoteBody
       present in Verification Report */
    sgx_quote_t* quote_body = reinterpret_cast<sgx_quote_t*>(
        Base64EncodedStringToByteArray(enclave_quote_body).data());
    sgx_report_body_t* report_body = &quote_body->report_body;
    sgx_report_data_t expected_report_data = *(&report_body->report_data);
    sgx_measurement_t mr_enclave_from_report = *(&report_body->mr_enclave);
    sgx_basename_t mr_basename_from_report = *(&quote_body->basename);
    sgx_measurement_t mr_signer_from_report = *(&report_body->mr_signer);

    /// Convert uint8_t array to ByteArray(vector<uint8_1>)
    ByteArray mr_enclave_bytes(std::begin(mr_enclave_from_report.m),
        std::end(mr_enclave_from_report.m));
    ByteArray mr_signer_bytes(std::begin(mr_signer_from_report.m),
        std::end(mr_signer_from_report.m));
    mr_enclave = mr_enclave_bytes;
    mr_signer = mr_signer_bytes;
    Log(TCF_LOG_INFO,"\n\n\n MRENCLAVE %s\n\n\n",
		    ByteArrayToStr(mr_enclave_bytes).c_str());

    uint8_t v_key_hash[SGX_HASH_SIZE] = {0};
    strncpy((char* )v_key_hash,
        (const char* )expected_report_data.d + SGX_HASH_SIZE,
        SGX_HASH_SIZE);
    verification_key_hash = StrToByteArray((char*)v_key_hash);

    return result;

}  // ExtWorkOrderInfoImpl::VerifyAttestation

