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

/**
 * @file
 * Avalon RSA private key generation, serialization, and decryption functions.
 * Serialization reads and writes keys in PEM format strings.
 */

#pragma once
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
            // Default constructor.
            PrivateKey(): private_key_(nullptr) {}
            // Copy constructor.
            // throws RuntimeError
            PrivateKey(const PrivateKey& privateKey);
            // Move constructor.
            // throws RuntimeError
            PrivateKey(PrivateKey&& privateKey);
            // Deserializing constructor.
            // Reads PEM format string (with "BEGIN RSA PRIVATE KEY").
            // Throws RuntimeError, ValueError
            PrivateKey(const std::string& encoded);
            ~PrivateKey();
            // throws RuntimeError
            PrivateKey& operator=(const PrivateKey& privateKey);
            // Reads PEM format string (with "BEGIN RSA PRIVATE KEY").
            // Throws RuntimeError, ValueError.
            void Deserialize(const std::string& encoded);
            // Generate PrivateKey.
            // throws RuntimeError
            void Generate();
            // throws RuntimeError
            PublicKey GetPublicKey() const;
            // Creates PEM format string (with "BEGIN RSA PRIVATE KEY").
            // Throws RuntimeError.
            std::string Serialize() const;
            // Decrypt message.data() and return plaintext.
            // throws RuntimeError
            ByteArray DecryptMessage(const ByteArray& ct) const;

        private:
            // void * is an opaque pointer to implementation-dependent context
            void *private_key_;
            void *deserializeRSAPrivateKey(const std::string& encoded);
        };
    }  // namespace pkenc
}  // namespace crypto
}  // namespace tcf
