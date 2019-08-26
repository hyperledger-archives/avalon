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
        class PublicKey;

        class PrivateKey {
            friend PublicKey;
            // throws RuntimeError
        public:
            // Default constructor
            PrivateKey(): private_key_(nullptr) {}
            // copy constructor
            // throws RuntimeError
            PrivateKey(const PrivateKey& privateKey);
            // move constructor
            // throws RuntimeError
            PrivateKey(PrivateKey&& privateKey);
            // deserializing constructor
            // throws RuntimeError, ValueError
            PrivateKey(const std::string& encoded);
            ~PrivateKey();
            // throws RuntimeError
            PrivateKey& operator=(const PrivateKey& privateKey);
            // throws RuntimeError, ValueError
            void Deserialize(const std::string& encoded);
            // generate PrivateKey
            // throws RuntimeError
            void Generate();
            // throws RuntimeError
            PublicKey GetPublicKey() const;
            // throws RuntimeError
            std::string Serialize() const;
            // Decrypt message.data() and return ByteArray containing raw binary plaintext
            // throws RuntimeError
            ByteArray DecryptMessage(const ByteArray& ct) const;

        private:
            RSA* private_key_;
        };
    }  // namespace pkenc
}  // namespace crypto
}  // namespace tcf
