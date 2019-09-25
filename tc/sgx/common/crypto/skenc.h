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
#include "types.h"

namespace tcf {
namespace crypto {
    namespace constants {
        //***AES-GCM 256 for authenticated encryption
        const int IV_LEN = 12;       // AES-GCM IV length
        const int SYM_KEY_LEN = 32;  // AES-GCM Key length.
        const int TAG_LEN = 16;      // AES-GCM TAG length.
    }  // namespace constants

    // Authenticated encryption
    namespace skenc {
        // ByteArray here is used to encapsulate raw binary data and does not apply/assume any
        // encoding
        // throws RuntimeError
        ByteArray GenerateKey();
        // throws RuntimeError
        ByteArray GenerateIV(const std::string& IVstring = std::string(""));
        // throws RuntimeError, ValueError
        ByteArray EncryptMessage(
            const ByteArray& key, const ByteArray& iv, const ByteArray& message);
        // Uses random IV prepended the returned ciphertext
        // throws RuntimeError, ValueError
        ByteArray EncryptMessage(const ByteArray& key, const ByteArray& message);
        // throws RuntimeError, ValueError, CryptoError (message authentication failure)
        ByteArray DecryptMessage(
            const ByteArray& key, const ByteArray& iv, const ByteArray& message);
        // throws RuntimeError, ValueError, CryptoError (message authentication failure)
        // expects IV prepended to message ciphertext
        ByteArray DecryptMessage(const ByteArray& key, const ByteArray& message);
    }  // namespace skenc
}  // namespace crypto
}  // namespace tcf
