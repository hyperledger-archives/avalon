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
 * Avalon RSA public key serialization and encryption functions.
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
        class PrivateKey;

        class PublicKey {
            friend PrivateKey;

        public:
            // Default constructor for UNINITIALIZED PublicKey.
            PublicKey();
            // Copy constructor.
            // throws RuntimeError
            PublicKey(const PublicKey& publicKey);
            // Move constructor.
            // throws RuntimeError
            PublicKey(PublicKey&& publicKey);
            // throws RuntimeError
            PublicKey(const PrivateKey& privateKey);
            // Deserializing constructor.
            // Reads RSA public key PEM format string.
            // (with "BEGIN RSA PUBLIC KEY" or "BEGIN PUBLIC KEY").
            // Throws RuntimeError, ValueError.
            PublicKey(const std::string& encoded);
            ~PublicKey();
            // throws RuntimeError
            PublicKey& operator=(const PublicKey& publicKey);
            // Reads RSA public key PEM format string
            // Throws RuntimeError, ValueError.
            void Deserialize(const std::string& encoded);
            // Creates RSA public key PEM format string
            // (with "BEGIN PUBLIC KEY").
            // Throws RuntimeError.
            std::string Serialize() const;
            // Encrypt message.data() and return ciphertext.
            // throws RuntimeError
            ByteArray EncryptMessage(const ByteArray& message) const;

        private:
            // void * is an opaque pointer to implementation-dependent context
            void *public_key_;
            void *deserializeRSAPublicKey(const std::string& encoded);
        };
    }  // namespace pkenc
}  // namespace crypto
}  // namespace tcf
