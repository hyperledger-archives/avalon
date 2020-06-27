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

#include "crypto.h"
#include "tcf_error.h"
#include "error.h"
#include "jsonvalue.h"
#include "parson.h"
#include "json_utils.h"
#include "enclave_utils.h"
#include "work_order_preprocessed_keys_wpe.h"

/*
 * Unpack Work order key info JSON object to extract index
 * and encrypted-data-key from input-data-keys or output-data-keys
 * 
 * @param keys_object - JSON object which has index and encrypted_in_data
 * @param data_keys [out] - WorkOrder data object placeholder to store
 *               index and encrypted-data-key from JSON object
 * @param encrypted_data_key [out] - Placeholder to store encrypted version
 *               of encrypted-data-key which will be used for hash calculation
*/
void WorkOrderPreProcessedKeys::Unpack(const JSON_Object* keys_object,
    tcf::WorkOrderData& data_keys, std::string& encrypted_data_key) {

    data_keys.index = GetJsonNumber(keys_object, "index");
    encrypted_data_key = GetJsonStr(keys_object, "encrypted-data-key");

    // skip decrypting data encryption key if its value is
    // equivalent to empty or null or "-"
    if (encrypted_data_key.empty() ||  "null" == encrypted_data_key ||
        "-" == encrypted_data_key) {
        return;
    }

    // Decrypt base64 encoded data key using symmetric key(after decryption)
    // from work_order_key_info json
    data_keys.decrypted_data = DecryptKey(this->sym_key,
        Base64EncodedStringToByteArray(encrypted_data_key));
}  // WorkOrderPreProcessedKeys::Unpack

/*
 * Decrypt the encrypted key using decryption key supplied.
 * 
 * @param decryption_key - Decryption key using which plain key is encrypted.
 * @param key_to_decrypt - encrypted key which is to be decrypted.
*/
ByteArray WorkOrderPreProcessedKeys::DecryptKey(
    const ByteArray& decryption_key, const ByteArray& key_to_decrypt) {

    return tcf::crypto::skenc::DecryptMessage(decryption_key, key_to_decrypt);
}  // WorkOrderPreProcessedKeys::DecryptKey

/*
 * Parse preprocessed work order key info json
 * 
 * @param work_order_keys_data_json - Serialized work order key json
 *                    obtained after preprocessing.
 * @param enclave_data - Instance of EnclaveData
*/
tcf_err_t WorkOrderPreProcessedKeys::ParsePreProcessingJson(
    std::string work_order_keys_data_json, EnclaveData* enclave_data) {

    JSON_Status jret;
    // Parse the preprocessed work order keys json
    JsonValue parsed(json_parse_string(work_order_keys_data_json.c_str()));
    tcf::error::ThrowIfNull(parsed.value,
        "Failed to parse the preprocessed work order keys data");

    JSON_Object* wo_keys_obj = json_value_get_object(parsed);
    tcf::error::ThrowIfNull(wo_keys_obj,
        "Missing JSON object in preprocessed work order keys data");
    this->encrypted_sym_key = GetJsonStr(wo_keys_obj,
        "encrypted-sym-key",
        "failed to retrieve encrypted symmetric key from preprocessed keys");
    // Decrypt base64 encoded symmetric key using WPE private encryption key
    this->sym_key = enclave_data->decrypt_message(
        Base64EncodedStringToByteArray(this->encrypted_sym_key));
    this->encrypted_work_order_session_key = GetJsonStr(wo_keys_obj,
        "encrypted-wo-key",
        "failed to retrieve encrypted work order session key "
        "from preprocessed keys");
    // Decrypt base64 encoded work order session key using
    // symmetric key decrypted above
    this->work_order_session_key = DecryptKey(this->sym_key,
        Base64EncodedStringToByteArray(this->encrypted_work_order_session_key));

    this->encrypted_signing_key = GetJsonStr(wo_keys_obj,
        "encrypted-wo-signing-key",
        "failed to retrieve encrypted work order session key "
        "from preprocessed keys");
    // Decrypt base64 encoded work order signing key using
    // symmetric key decrypted above
    this->signing_key = DecryptKey(this->sym_key,
        Base64EncodedStringToByteArray(encrypted_signing_key));

    this->verification_key = GetJsonStr(wo_keys_obj,
        "wo-verification-key",
        "failed to retrieve work order verification key "
        "from preprocessed keys");

    std::string wo_verification_key_sig = GetJsonStr(wo_keys_obj,
        "wo-verification-key-sig",
        "failed to retrieve work order verification key signature "
        "from preprocessed keys");
    this->verification_key_signature = \
        Base64EncodedStringToByteArray(wo_verification_key_sig);

    std::string signature_str = GetJsonStr(wo_keys_obj,
        "signature",
        "failed to retrieve signature from preprocessed keys");
    this->signature = Base64EncodedStringToByteArray(signature_str);

    JSON_Array* in_data_keys_arr = json_object_get_array(
        wo_keys_obj, "input-data-keys");
    size_t count = json_array_get_count(in_data_keys_arr);

    if (count > 0) {
        in_data_keys.resize(count);
        encrypted_in_data_keys.resize(count);
        for (int i=0; i<count; i++) {
            JSON_Object* keys_object = json_array_get_object(
                in_data_keys_arr, i);
            Unpack(keys_object, in_data_keys[i], encrypted_in_data_keys[i]);
        }
    }

    JSON_Array* out_data_keys_arr = json_object_get_array(
        wo_keys_obj, "output-data-keys");
    count = json_array_get_count(out_data_keys_arr);

    if (count > 0) {
        out_data_keys.resize(count);
        encrypted_out_data_keys.resize(count);
        for (int i=0; i<count; i++) {
            JSON_Object* keys_object = json_array_get_object(
                out_data_keys_arr, i);
            Unpack(keys_object, out_data_keys[i], encrypted_out_data_keys[i]);
        }
    }
}  // WorkOrderPreProcessedKeys::ParsePreProcessingJson

/*
 * Calculates hash of work order key info fields
*/
ByteArray WorkOrderPreProcessedKeys::CalculateWorkOrderKeyInfoHash() {
    std::string concat_str = this->encrypted_sym_key +
        this->encrypted_work_order_session_key +
        this->encrypted_signing_key;
    std::string hash1_str = ByteArrayToBase64EncodedString(
        tcf::crypto::ComputeMessageHash(StrToByteArray(concat_str)));

    // Compute hash on encrypted_in_data_keys
    std::string enc_in_data_hash_str;
    for (auto d: encrypted_in_data_keys) {
        enc_in_data_hash_str += ByteArrayToBase64EncodedString(
            tcf::crypto::ComputeMessageHash(
                Base64EncodedStringToByteArray(d)));
    }

    // Compute hash on encrypted_out_data_keys
    std::string enc_out_data_hash_str;
    for (auto d: encrypted_out_data_keys) {
        enc_out_data_hash_str += ByteArrayToBase64EncodedString(
            tcf::crypto::ComputeMessageHash(
                Base64EncodedStringToByteArray(d)));
    }

    std::string final_hash_str = \
        hash1_str + enc_in_data_hash_str + enc_out_data_hash_str;
    return tcf::crypto::ComputeMessageHash(StrToByteArray(final_hash_str));
}

/*
 * Verifies signature of work order key json by comparing hash values.
 * 
 * @param enclave_data - Instance of EnclaveData
 * 
 * @returns status of signature verification.
 * passed = 1
 * failed = other values
*/
tcf_err_t WorkOrderPreProcessedKeys::VerifySignatureOfWorkOrderKeys(
    EnclaveData* enclave_data) {

    ByteArray hash = CalculateWorkOrderKeyInfoHash();
    ByteArray verify_key_hex_bytes = HexEncodedStringToByteArray(
        ByteArrayToStr(enclave_data->get_extended_data()));
    tcf::crypto::sig::PublicKey public_key(
        ByteArrayToStr(verify_key_hex_bytes));
    size_t result = public_key.VerifySignature(hash, this->signature);
    tcf::error::ThrowIf<tcf::error::ValueError>(result != 1,
        "Failed to verify signature of work order key info");
}  // WorkOrderPreProcessedKeys::VerifySignatureOfPreProcessedJson


/*
 * Process work order key info json obtainer after preprocessing
 * 
 * @param work_order_keys_data_json - Serialized work order key json
 *                    obtained after preprocessing.
 * @param enclave_data - Instance of EnclaveData
*/
tcf_err_t WorkOrderPreProcessedKeys::ProcessPreProcessedWorkOrderKeys(
    std::string work_order_keys_data_json, EnclaveData* enclave_data) {

    try {
        ParsePreProcessingJson(work_order_keys_data_json, enclave_data);
        Log(TCF_LOG_INFO, "parsed preprocessed work order keys.....");
        VerifySignatureOfWorkOrderKeys(enclave_data);
        Log(TCF_LOG_INFO, "verified signature of preprocessed work order keys.....");
    } catch (tcf::error::ValueError& e) {
        Log(TCF_LOG_ERROR, "Failed to process pre-processed "
            "work order key info json - %s", e.what());
        return TCF_ERR_VALUE;
    } catch (...) {
        Log(TCF_LOG_ERROR, "Unknown error while processing preprocessed "
            "work order key info json");
        return TCF_ERR_UNKNOWN;
    }
}  // WorkOrderPreProcessedKeys::ProcessPreProcessedWorkOrderKeys
