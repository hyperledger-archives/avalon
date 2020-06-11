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

#include <algorithm>
#include <string>
#include <vector>
 
#include "error.h"
#include "tcf_error.h"
#include "types.h"

#include "crypto.h"
#include "skenc.h"
#include "jsonvalue.h"
#include "parson.h"
#include "hex_string.h"
#include "json_utils.h"
#include "utils.h"

#include "enclave_utils.h"
#include "enclave_data.h"

#include "work_order_processor.h"
#include "work_order_data_handler.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
namespace tcf {

    void WorkOrderDataHandler::GetDataEncryptionKey(
        ByteArray& data_encrypt_key, ByteArray& iv_bytes) {
        // encryptedDataEncryptionKey in inData or outData of the work order
        // request is in double encrypted format. At first, data encryption
        // is encrypted with Worker's public encryption key and then
        // requester's session key. To decrypt, first decrypt with session key
        // and then further decrypt with worker's private encryption key

        iv_bytes = HexStringToBinary(iv);
        ByteArray enc_data_key_bytes = HexStringToBinary(enc_data_key_str);
        ByteArray encrypted_key = tcf::crypto::skenc::DecryptMessage(
            session_key, enc_data_key_bytes);
        EnclaveData* enclave_data = EnclaveData::getInstance();
        data_encrypt_key = enclave_data->decrypt_message(encrypted_key);
    }

    void WorkOrderDataHandler::InitializeDataEncryptionKey() {
        if (enc_data_key_str.empty() || "null" == enc_data_key_str) {
            data_encryption_key = session_key;
            data_iv = session_key_iv;
        } else if ("-" == enc_data_key_str) {
            // If encrypted data encryption key is "-" in inData or outData
            // data is unencrypted plain text. Hence setting data_encryption_key
            // and data_iv set to empty values.
            data_encryption_key = {};
            data_iv = {};
        } else {
            ByteArray data_enc_key = {};
            ByteArray iv_bytes = {};
            GetDataEncryptionKey(data_encryption_key, data_iv);
            data_encryption_key = data_enc_key;
            data_iv = iv_bytes;
        }
    }

    void WorkOrderDataHandler::Unpack(const JSON_Object* object) {
        ByteArray encrypted_input_data;
        std::string input_data_hash;

        workorder_data.index = GetJsonNumber(object, "index");
        iv = GetJsonStr(object, "iv");
        enc_data_key_str = GetJsonStr(object, "encryptedDataEncryptionKey");

        InitializeDataEncryptionKey();

        std::string data_b64 = GetJsonStr(object, "data");
        if (!data_b64.empty()) {
            encrypted_input_data = Base64EncodedStringToByteArray(data_b64);
        } else {
            encrypted_input_data.clear();
        }

        input_data_hash = GetJsonStr(object, "dataHash");
        if (!encrypted_input_data.empty()) {
            DecryptData(encrypted_input_data);
            if (!input_data_hash.empty()) {
                tcf_err_t status = VerifyInputHash(workorder_data.decrypted_data,
                    HexStringToBinary(input_data_hash));
                tcf::error::ThrowIf<tcf::error::ValueError>(
                    status != TCF_SUCCESS, "input data hash verification failed");
            }
        } else {
            tcf::error::ThrowIf<tcf::error::ValueError>(!input_data_hash.empty(),
               "Invalid case: input data is empty but dataHash is non empty");
            workorder_data.decrypted_data = encrypted_input_data;
        }
        concat_string = input_data_hash + data_b64 + enc_data_key_str + iv;
        data_b64.clear();
    }  // WorkOrderDataHandler::Unpack

    void WorkOrderDataHandler::Pack(JSON_Array* json_array) {
        JSON_Status jret;

        JSON_Value* data_item_value = json_value_init_object();
        tcf::error::ThrowIfNull(data_item_value, "failed to create a data item");

        JSON_Object* data_item_object = json_value_get_object(data_item_value);
        tcf::error::ThrowIfNull(data_item_object, "failed to create a data item");

        JsonSetNumber(data_item_object,
                      "index",
                      workorder_data.index,
                      "failed to serialize index");

        Base64EncodedString output_hash_str = ByteArrayToHexEncodedString(hash);
        JsonSetStr(data_item_object,
                   "dataHash",
                   output_hash_str.c_str(),
                   "failed to serialize dataHash");

        std::string encrypted_output_str = base64_encode(encrypted_data);
        JsonSetStr(data_item_object,
                   "data",
                   encrypted_output_str.c_str(),
                   "failed to serialize encrypted output data");
        JsonSetStr(data_item_object,
                   "encryptedDataEncryptionKey",
                   enc_data_key_str.c_str(),
                   "failed to serialize encryptedDataEncryptionKey");

        JsonSetStr(data_item_object,
                   "iv",
                   iv.c_str(),
                   "failed to serialize data iv");

        jret = json_array_append_value(json_array, data_item_value);
        tcf::error::ThrowIf<tcf::error::RuntimeError>(
                jret != JSONSuccess, "failed to add item to the data array");
    }  // WorkOrderDataHandler::Pack

    void WorkOrderDataHandler::ComputeHashString() {
        std::string b64_encrypted_data = EncryptData();
        hash = tcf::crypto::ComputeMessageHash(workorder_data.decrypted_data);
        Base64EncodedString hash_str = ByteArrayToHexEncodedString(hash);
        concat_string = hash_str + b64_encrypted_data + enc_data_key_str + iv;
    }  // WorkOrderDataHandler::ComputeHashString

    tcf_err_t WorkOrderDataHandler::VerifyInputHash(
        ByteArray input_data, ByteArray input_hash) {
        tcf_err_t verify_status = TCF_SUCCESS;
        ByteArray hash = tcf::crypto::ComputeMessageHash(input_data);
        if (std::equal(hash.begin(), hash.end(), input_hash.begin())) {
            Log(TCF_LOG_INFO, "input data hash verification passed");
        } else {
            Log(TCF_LOG_ERROR, "input data hash verification failed");
            verify_status = TCF_ERR_CRYPTO;
        }

        return verify_status;
    }  // WorkOrderDataHandler::VerifyInputHash

    void WorkOrderDataHandler::DecryptData(ByteArray encrypted_input_data) {

        if (data_encryption_key.size() > 0) {
            workorder_data.decrypted_data = tcf::crypto::skenc::DecryptMessage(
		   data_encryption_key, data_iv, encrypted_input_data);
        } else {
            workorder_data.decrypted_data = encrypted_input_data;
        }
    }  // WorkOrderDataHandler::DecryptData

    std::string WorkOrderDataHandler::EncryptData() {
        std::string b64_encrypted_data;
        if (workorder_data.decrypted_data.empty()) {
            encrypted_data = workorder_data.decrypted_data;
            b64_encrypted_data.clear();
        } else if (data_encryption_key.size() > 0) {
            encrypted_data = tcf::crypto::skenc::EncryptMessage(
		   data_encryption_key, data_iv, workorder_data.decrypted_data);
            b64_encrypted_data = base64_encode(encrypted_data);
        } else {
            encrypted_data = workorder_data.decrypted_data;
            b64_encrypted_data.assign(workorder_data.decrypted_data.begin(),
			    workorder_data.decrypted_data.end());
        }
        return b64_encrypted_data;
    }  // WorkOrderDataHandler::EncryptData

}  // namespace tcf
