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
#include "enclave_data.h"
#include <string>

#include "crypto.h"
#include "utils.h"
#include "types.h"
#include "error.h"

#include "verify-report.h"
#include "signup_enclave_util.h"
#include "parson.h"
#include "jsonvalue.h"
#include "json_utils.h"
#include "enclave_data.h"

#include "enclave_utils.h"
#include "ext_work_order_info_kme.h"

using namespace tcf::error;

ExtWorkOrderInfoKME::ExtWorkOrderInfoKME(void) {}

ExtWorkOrderInfoKME::~ExtWorkOrderInfoKME(void) {}

int ExtWorkOrderInfoKME::GenerateSigningKey(
    KeyType type, const ByteArray& nonce_hex,
    ByteArray& signing_key, ByteArray& verification_key_hex,
    ByteArray& verification_key_signature_hex) {

    tcf_err_t result = TCF_SUCCESS;

    if (type != KeyType_SECP256K1) {
        Log(TCF_LOG_ERROR,
            "Unsupported KeyType passed to generate signig key pair");
        result = TCF_ERR_CRYPTO;
        return result;
    }

    tcf::crypto::sig::PrivateKey private_sig_key;
    tcf::crypto::sig::PublicKey public_sig_key;

    try {
        // Generate Signing key pair
        private_sig_key.Generate();
        public_sig_key = private_sig_key.GetPublicKey();

        signing_key = StrToByteArray(private_sig_key.Serialize());

        ByteArray v_key_bytes = StrToByteArray(public_sig_key.Serialize());
        std::string v_key_hex_str = ByteArrayToHexEncodedString(v_key_bytes);
        verification_key_hex = StrToByteArray(v_key_hex_str);

        // Generate signature on hash of concatenation of
        // base64 encoded verification key and hex encoded nonce string.
        // nonce_hex bytearray is converted to c_str to remove
        // string termination '\0' char
        std::string msg = ByteArrayToStr(v_key_bytes) +
            ByteArrayToStr(nonce_hex).c_str();
        ByteArray msg_hash = tcf::crypto::ComputeMessageHash(
            StrToByteArray(msg));
        ByteArray signature = private_sig_key.SignMessage(msg_hash);

        std::string signature_hex = ByteArrayToHexEncodedString(signature);
        verification_key_signature_hex = StrToByteArray(signature_hex);
    } catch (tcf::error::CryptoError& e) {
        Log(TCF_LOG_ERROR,
            "Caught Exception while generating Signing key pair: %s, %s",
            e.error_code(), e.what());
        result = TCF_ERR_CRYPTO;
    }

    return result;
}  // ExtWorkOrderInfoKME::GenerateSigningKey

int ExtWorkOrderInfoKME::VerifyAttestationWpe(
    const ByteArray& attestation_data, const ByteArray& hex_id,
    ByteArray& mr_enclave, ByteArray& mr_signer,
    ByteArray& encryption_public_key_hash, ByteArray& verification_key_hash) {
    /// Verify attestation report
    VerificationStatus result = VERIFICATION_SUCCESS;
    std::string att_data_string = ByteArrayToString(attestation_data);
    /// Parse the attestation data
    JsonValue att_data_string_parsed(json_parse_string(
        att_data_string.c_str()));
    if (att_data_string_parsed.value == nullptr) {
	ThrowIf<ValueError>(true, "Parsing attestation data failed");
        return VERIFICATION_FAILED;
    }
    JSON_Object* proof_object = \
        json_value_get_object(att_data_string_parsed);
    if (proof_object == nullptr) {
	ThrowIf<ValueError>(true, "Get proof data json object failed");
        return VERIFICATION_FAILED;
    }

    const char* s_value = nullptr;

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
	    "Get verification report json object failed");
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

}  // ExtWorkOrderInfoKME::VerifyAttestationWpe

int ExtWorkOrderInfoKME::CreateWorkOrderKeyInfo(
    const ByteArray& wpe_encryption_key,
    const ByteArray& kme_signing_key,
    ByteArray& work_order_key_data) {

    tcf_err_t result = TCF_SUCCESS;

    tcf::crypto::sig::PrivateKey private_sig_key;
    tcf::crypto::sig::PublicKey public_sig_key;
    try {
        WorkOrderKeyInfo wo_key_info;
        wo_key_info.in_data_keys = this->in_work_order_keys;
        wo_key_info.out_data_keys =  this->out_work_order_keys;

        // generate symmetric key
        wo_key_info.sym_key = tcf::crypto::skenc::GenerateKey();

        // encrypted_wo_key is the encrypted version of session key
        // generated client using symmetric key generated above
        wo_key_info.encrypted_wo_key = tcf::crypto::skenc::EncryptMessage(
            wo_key_info.sym_key, this->work_order_sym_key);

        // Generate work order signing key pair to sign work order response
        // and encrypt the signing key using symmetric key generated above
        private_sig_key.Generate();
        public_sig_key = private_sig_key.GetPublicKey();

        ByteArray signing_key = StrToByteArray(private_sig_key.Serialize());
        // verification_key is PEM encoded public key string
        wo_key_info.verification_key = public_sig_key.Serialize();

        // Generate signature on verification key and nonce
        std::string concat_str = \
            public_sig_key.Serialize() + this->wo_requester_nonce;

        // Sign hash of concatenated verification key signature and
        // requester nonce using worker's private key.
        // Verification key signature is verified at client
        // by using worker's public verification key
        EnclaveData* enclave_data = EnclaveData::getInstance();
        ByteArray verify_key_sig_hash = \
            tcf::crypto::ComputeMessageHash(StrToByteArray(concat_str));
        wo_key_info.verification_key_signature = \
            enclave_data->sign_message(verify_key_sig_hash);

        // encrypt the signing key using symmetric key
        wo_key_info.encrypted_signing_key = \
            tcf::crypto::skenc::EncryptMessage(
                wo_key_info.sym_key, signing_key);

        // encrypt the symmetric key using WPE asymmetric public encryption key
        tcf::crypto::pkenc::PublicKey public_enc_key(
            ByteArrayToStr(wpe_encryption_key));
        wo_key_info.encrypted_sym_key = \
            public_enc_key.EncryptMessage(wo_key_info.sym_key);

        // Encrypt plain keys in in_data and out_data using symmetric key
        int count = this->in_work_order_keys.size();
        wo_key_info.in_data_keys.resize(count);
        for (int i=0; i<count; i++) {
            std::string in_data_enc_key = \
                ByteArrayToStr(wo_key_info.in_data_keys[i].decrypted_data);
            // skip encrypting input data encryption key if
            // its value is equivalent to empty or null or "-"
            // these checks are performed again while decrypting data
            // during work order processing at WPE
            if (in_data_enc_key.empty() || "null" == in_data_enc_key ||
                "-" == in_data_enc_key ) {
                continue;
            }
            wo_key_info.in_data_keys[i].decrypted_data = \
                tcf::crypto::skenc::EncryptMessage(wo_key_info.sym_key,
                    wo_key_info.in_data_keys[i].decrypted_data);
        }

        count = this->out_work_order_keys.size();
        wo_key_info.out_data_keys.resize(count);
        for (int i=0; i<count; i++) {
            std::string out_data_enc_key = \
                ByteArrayToStr(wo_key_info.out_data_keys[i].decrypted_data);
            // skip encrypting output data encryption key if
            // its value is equivalent to empty or null or "-"
            // these checks are performed again while decrypting data
            // during work order processing at WPE
            if (out_data_enc_key.empty() || "null" == out_data_enc_key ||
                "-" == out_data_enc_key) {
                continue;
            }
            wo_key_info.out_data_keys[i].decrypted_data = \
                tcf::crypto::skenc::EncryptMessage(wo_key_info.sym_key,
                    wo_key_info.out_data_keys[i].decrypted_data);
        }

        // Calculate signature of hash of all the encrypted values in this
        // work order key info JSON using KME's signing key
        ByteArray wo_key_info_hash = {};
        CalculateWorkOrderKeyInfoHash(wo_key_info, wo_key_info_hash);

        tcf::crypto::sig::PrivateKey kme_priv_key(
            ByteArrayToStr(kme_signing_key));
        wo_key_info.signature = kme_priv_key.SignMessage(wo_key_info_hash);

        // Generate WorkOrderKeyInfo JSON doc
        work_order_key_data = CreateJsonWorkOrderKeys(wo_key_info);
    } catch (tcf::error::CryptoError& e) {
        Log(TCF_LOG_ERROR,
            "Caught Exception while creating work order key info: %s, %s",
            e.error_code(), e.what());
        result = TCF_ERR_CRYPTO;
    }

    return result;
}  // ExtWorkOrderInfoKME::CreateWorkOrderKeyInfo

bool ExtWorkOrderInfoKME::CheckAttestationSelf(
    const ByteArray& attestation_data, ByteArray& mrenclave,
    ByteArray& mrsigner, ByteArray& verification_key,
    ByteArray& encryption_public_key) {

    // To be implemented
    return 0;
}  // ExtWorkOrderInfoKME::CheckAttestationSelf

void ExtWorkOrderInfoKME::CalculateWorkOrderKeyInfoHash(
    WorkOrderKeyInfo wo_key_info, ByteArray& wo_key_info_hash) {

    std::string concat_str = \
        ByteArrayToBase64EncodedString(wo_key_info.encrypted_sym_key) +
        ByteArrayToBase64EncodedString(wo_key_info.encrypted_wo_key) +
        ByteArrayToBase64EncodedString(wo_key_info.encrypted_signing_key);

    std::string hash1_str = ByteArrayToBase64EncodedString(
        tcf::crypto::ComputeMessageHash(StrToByteArray(concat_str)));

    // sort input-data-keys and output-data-keys based on indices
    std::sort(wo_key_info.in_data_keys.begin(), wo_key_info.in_data_keys.end(),
        [](tcf::WorkOrderData x, tcf::WorkOrderData y) {
            return x.index < y.index;});

    std::sort(wo_key_info.out_data_keys.begin(), wo_key_info.out_data_keys.end(),
        [](tcf::WorkOrderData x, tcf::WorkOrderData y) {
            return x.index < y.index;});

    std::string in_data_hash_str;
    for (auto d: wo_key_info.in_data_keys) {
        in_data_hash_str += ByteArrayToBase64EncodedString(
            tcf::crypto::ComputeMessageHash(d.decrypted_data));
    }

    std::string out_data_hash_str;
    for (auto d: wo_key_info.out_data_keys) {
        out_data_hash_str += ByteArrayToBase64EncodedString(
            tcf::crypto::ComputeMessageHash(d.decrypted_data));
    }
    std::string final_hash_str = \
        hash1_str + in_data_hash_str + out_data_hash_str;
    wo_key_info_hash = tcf::crypto::ComputeMessageHash(
        StrToByteArray(final_hash_str));
}  // ExtWorkOrderInfoKME::CalculateWorkOrderKeyInfoHash

ByteArray ExtWorkOrderInfoKME::CreateJsonWorkOrderKeys(
    WorkOrderKeyInfo wo_key_info) {

    JSON_Status jret;
    // Create the response structure
    JsonValue wo_key_info_val(json_value_init_object());
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        !wo_key_info_val.value, "Failed to create the work order key info object");

    JSON_Object* wo_key_info_obj = json_value_get_object(wo_key_info_val);
    tcf::error::ThrowIfNull(wo_key_info_obj,
        "Failed to retrieve of work order info object");

    JsonSetStr(wo_key_info_obj, "signature",
        wo_key_info.GetSignature().c_str(),
        "failed to serialize signature");
    JsonSetStr(wo_key_info_obj, "encrypted-sym-key",
        wo_key_info.GetEncryptedSymmetricKey().c_str(),
        "failed to serialize encrypted symmetric key");
    JsonSetStr(wo_key_info_obj, "encrypted-wo-key",
        wo_key_info.GetEncryptedWorkOrderKey().c_str(),
        "failed to serialize encrypted work order key");
    JsonSetStr(wo_key_info_obj, "encrypted-wo-signing-key",
        wo_key_info.GetEncryptedSigningKey().c_str(),
        "failed to serialize encrypted work order signing key");
    JsonSetStr(wo_key_info_obj, "wo-verification-key",
        wo_key_info.GetVerificationKey().c_str(),
        "failed to serialize work order verification key");
    JsonSetStr(wo_key_info_obj, "wo-verification-key-sig",
        wo_key_info.GetVerificationKeySignature().c_str(),
        "failed to serialize work order verification key signature");

    // construct input-data-keys and output-data-keys
    jret = json_object_set_value(wo_key_info_obj,
        "input-data-keys", json_value_init_array());
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        jret != JSONSuccess, "failed to set input-data-keys array");
    JSON_Array* in_data_keys_arr = json_object_get_array(
        wo_key_info_obj, "input-data-keys");
    tcf::error::ThrowIfNull(in_data_keys_arr,
        "failed to get input-data-keys array");

   JSON_Value* key_item_value;
   JSON_Object* key_item_object;
    for (auto wo_key: wo_key_info.in_data_keys) {
        key_item_value = json_value_init_object();
        tcf::error::ThrowIfNull(key_item_value,
            "failed to create a key item value");

        key_item_object = json_value_get_object(key_item_value);
        tcf::error::ThrowIfNull(key_item_object,
            "failed to create a key item object");

        JsonSetNumber(key_item_object, "index", wo_key.index,
            "failed to serialize index of input-work-order-key");
        JsonSetStr(key_item_object, "encrypted-data-key",
            ByteArrayToBase64EncodedString(wo_key.decrypted_data).c_str(),
            "failed to serialize key of input-work-order-key");
        jret = json_array_append_value(in_data_keys_arr, key_item_value);
        tcf::error::ThrowIf<tcf::error::RuntimeError>(jret != JSONSuccess,
            "failed to add key item to the in-data-keys array");
    }

    jret = json_object_set_value(wo_key_info_obj,
        "output-data-keys", json_value_init_array());
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        jret != JSONSuccess, "failed to set output-data-keys array");
    JSON_Array* out_data_keys_arr = json_object_get_array(
        wo_key_info_obj, "output-data-keys");
    tcf::error::ThrowIfNull(out_data_keys_arr,
        "failed to get output-data-keys array");

    for (auto wo_key: wo_key_info.out_data_keys) {
        key_item_value = json_value_init_object();
        tcf::error::ThrowIfNull(key_item_value,
            "failed to create a key item value");

        key_item_object = json_value_get_object(key_item_value);
        tcf::error::ThrowIfNull(key_item_object,
            "failed to create a key item object");
        JsonSetNumber(key_item_object, "index", wo_key.index,
            "failed to serialize index of output-work-order-key");
        JsonSetStr(key_item_object, "encrypted-data-key",
            ByteArrayToBase64EncodedString(wo_key.decrypted_data).c_str(),
            "failed to serialize key of output-work-order-key");
        jret = json_array_append_value(out_data_keys_arr, key_item_value);
        tcf::error::ThrowIf<tcf::error::RuntimeError>(jret != JSONSuccess,
            "failed to add key item to the output-data-keys array");
    }

    // Serialize the resulting json
    size_t serialized_size = json_serialization_size(wo_key_info_val);
    ByteArray serialized_wo_key_info;
    serialized_wo_key_info.resize(serialized_size);

    jret = json_serialize_to_buffer(wo_key_info_val,
        reinterpret_cast<char*>(&serialized_wo_key_info[0]),
        serialized_wo_key_info.size());
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        jret != JSONSuccess, "work order key info serialization failed");

    return serialized_wo_key_info;
}  // ExtWorkOrderInfoKME::CreateJsonWorkOrderKeys

