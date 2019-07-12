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
#include "work_order_data.h"


namespace tcf {
        class WorkOrderDataHandler {
        public:
            WorkOrderDataHandler() {}

            explicit WorkOrderDataHandler(const WorkOrderData& wo_data, std::string encrypted_session_key) {
                workorder_data = wo_data;
                data_encryption_key = HexEncodedStringToByteArray(encrypted_session_key);
            }

            void Unpack(EnclaveData& enclaveData, const JSON_Object* object, std::string encryptedSessionKey);
            void Pack(JSON_Array* json_array);

            void ComputeHashString(std::string session_key_iv);
            tcf::WorkOrderData workorder_data;
            std::string concat_string;

        private:
            std::string iv;
            std::string enc_data_key_str;
            ByteArray encrypted_data = {};
            ByteArray hash = {};

            void ComputeOutputHash();
            void VerifyInputHash(ByteArray input_data, ByteArray input_hash);
            void DecryptInputData(ByteArray encrypted_input_data, ByteArray iv);
            std::string EncryptOutputData(ByteArray iv);
            ByteArray data_encryption_key = {};
        };
}  // namespace tcf
