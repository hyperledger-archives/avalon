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

#include <string>

#include "io_helper.h"
#include "file_io_wrapper.h"
#include "crypto_utils.h"

#define SUCCESS 0
#define FAILED -1

namespace crypto = tcf::crypto;

IoHelper::IoHelper(std::string file_name) {
    this->file_name = file_name;
}

std::string IoHelper::GenerateKey() {
    return crypto::CreateHexEncodedEncryptionKey();
}

void IoHelper::SetKey(std::string hex_key) {
    this->hex_key = hex_key;
}

uint32_t IoHelper::ReadFile(std::string& read_data) {
    std::string encrypted_data = Read(this->file_name);
    if ( encrypted_data.empty() ) {
        return FAILED;
    }
    read_data = crypto::DecryptData(encrypted_data, this->hex_key);
    return SUCCESS;
}

uint32_t IoHelper::WriteFile(std::string data) {
    std::string encrypted_data = crypto::EncryptData(data, this->hex_key);
    uint32_t status = Write(this->file_name, encrypted_data);
    return status;
}

uint32_t IoHelper::DeleteFile() {
    uint32_t status = Delete(this->file_name);
    return status;
}
