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

#include "hex_string.h"
#include "work_order_data_handler_wpe.h"

namespace tcf {
    // This is a overriden function because in case of WPE,
    // data encryption key of the work order request is decrypted by KME
    // during preprocess stage since it holds worker's private key.
    // Hence return data encryption key present from the preprocessed output.
    void WorkOrderDataHandlerWPE::GetDataEncryptionKey(
        ByteArray& data_encrypt_key, ByteArray& iv_bytes) {

        iv_bytes = HexStringToBinary(iv);
        data_encrypt_key = this->data_encryption_key_from_preprocess;
    }  // WorkOrderDataHandlerWPE::GetDataEncryptionKey
} // namespace tcf

