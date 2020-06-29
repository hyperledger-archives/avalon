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

#pragma once

#include <string>
#include <vector>

#include "enclave_data.h"

#include "base64.h"
#include "parson.h"
#include "types.h"
#include "tcf_error.h"
#include "work_order_data.h"

namespace tcf {
        class WorkOrderDataHandler {
        public:
            WorkOrderDataHandler() {}

            explicit WorkOrderDataHandler(ByteArray session_key,
                                          ByteArray session_key_iv) {
                this->session_key = session_key;
                this->session_key_iv = session_key_iv;
                this->data_encryption_key = {};
                this->data_iv = {};
            }

            // Used when input request doesn't have OutData
            explicit WorkOrderDataHandler(const WorkOrderData& wo_data,
                                          ByteArray data_encryption_key,
                                          ByteArray data_iv,
                                          std::string enc_data_key_str,
                                          std::string iv) {
                workorder_data = wo_data;
                this->data_encryption_key = data_encryption_key;
                this->data_iv = data_iv;

                this->enc_data_key_str = enc_data_key_str;
                this->iv = iv;
            }

            void Unpack(const JSON_Object* object);

            void InitializeDataEncryptionKey();

            virtual void GetDataEncryptionKey(
                ByteArray& data_encrypt_key, ByteArray& iv_bytes);

            void Pack(JSON_Array* json_array);

            ByteArray GetEncryptionKey() {
                return this->data_encryption_key;
            }

            std::string GetIv() {
                return this->iv;
            }

            std::string GetEncryptedDataEncryptionKey() {
                return this->enc_data_key_str;
            }

            ByteArray GetDataIv() {
                return this->data_iv;
            }

            void ComputeHashString();
            tcf::WorkOrderData workorder_data;
            std::string concat_string;

            ByteArray GetDataEncryptionKey() {
                return this->data_encryption_key;
            }

        protected:
            // iv is used for calculating hash during signature verification
            // and signature computation
            std::string iv;
            // enc_data_key_str is encryptedDataEncryptionKey
            // used to decrypt input data
            std::string enc_data_key_str;
            ByteArray encrypted_data = {};
            ByteArray hash = {};

            // data_encryption_key is a symmetric key used for
            // both encryption and decryption of data
            ByteArray data_encryption_key = {};
            // data_iv is used for encryption and decryption of data
            ByteArray data_iv = {};

            ByteArray session_key = {};
            ByteArray session_key_iv = {};
            void ComputeOutputHash();
            tcf_err_t VerifyInputHash(ByteArray input_data,
                                      ByteArray input_hash);
            void DecryptData(ByteArray encrypted_input_data);
            std::string EncryptData();
        };
}  // namespace tcf
