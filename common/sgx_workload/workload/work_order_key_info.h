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

#pragma once

#include <string>

#include "types.h"
#include "work_order_data.h"

class WorkOrderKeyInfo {
public:
    WorkOrderKeyInfo() {
        sym_key = {};
        encrypted_sym_key = {};
        encrypted_wo_key = {};
        encrypted_signing_key = {};
        verification_key = "";
        verification_key_signature = {};
        signature = {};
        in_data_keys = {};
        out_data_keys = {};
    }

    std::string GetEncryptedSymmetricKey() {
        return ByteArrayToBase64EncodedString(encrypted_sym_key);
    }

    std::string GetEncryptedWorkOrderKey() {
        return ByteArrayToBase64EncodedString(encrypted_wo_key);
    }

    std::string GetEncryptedSigningKey() {
        return ByteArrayToBase64EncodedString(encrypted_signing_key);
    }

    std::string GetVerificationKey() {
        return this->verification_key;
    }

    std::string GetVerificationKeySignature() {
        return ByteArrayToBase64EncodedString(verification_key_signature);
    }

    std::string GetSignature() {
        return ByteArrayToBase64EncodedString(signature);
    }

    ByteArray sym_key;
    ByteArray encrypted_sym_key;
    ByteArray encrypted_wo_key;
    ByteArray encrypted_signing_key;
    Base64EncodedString verification_key;
    ByteArray verification_key_signature;
    ByteArray signature;
    std::vector<tcf::WorkOrderData> in_data_keys;
    std::vector<tcf::WorkOrderData> out_data_keys;
};
