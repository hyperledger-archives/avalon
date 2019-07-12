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
#include <openssl/rsa.h>
#include <string>
#include <vector>
#include "types.h"

namespace tcf {
namespace crypto {
    // Public Key encryption functions
    namespace pkenc {
        class PrivateKey;
        class PublicKey {
            friend PrivateKey;

        public:
            // default constructor: UNINITIALIZED PublicKey!
            PublicKey();
            // copy constructor
            // throws RuntimeError
            PublicKey(const PublicKey& publicKey);
            // move constructor
            // throws RuntimeError
            PublicKey(PublicKey&& publicKey);
            // throws RuntimeError
            PublicKey(const PrivateKey& privateKey);
            // deserializing constructor
            // throws RuntimeError, ValueError
            PublicKey(const std::string& encoded);
            ~PublicKey();
            // throws RuntimeError
            PublicKey& operator=(const PublicKey& publicKey);
            // throws RuntimeError, ValueError
            void Deserialize(const std::string& encoded);
            // throws RuntimeError
            std::string Serialize() const;
            // Encrypt message.data() and return ByteArray containing raw binary ciphertext
            // throws RuntimeError
            ByteArray EncryptMessage(const ByteArray& message) const;

        private:
            RSA* public_key_;
        };
    }  // namespace pkenc
}  // namespace crypto
}  // namespace tcf
