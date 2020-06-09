/* Copyright 2018-2020 Intel Corporation
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
 *
 * No OpenSSL/Mbed TLS-dependent code is present.
 * See pkenc_private_key.cpp for OpenSSL/Mbed TLS-dependent code.
 */

#include "crypto_shared.h"
#include "error.h"
#include "hex_string.h"
#include "pkenc.h"
#include "pkenc_public_key.h"
#include "pkenc_private_key.h"

namespace pcrypto = tcf::crypto;
namespace constants = tcf::crypto::constants;
namespace Error = tcf::error; // Error handling.


/**
 * Constructor from PEM encoded string.
 * That is, convert the key from a PEM format string
 * (begins with "BEGIN RSA PRIVATE KEY").
 *
 * Implemented with deserializeRSAPrivateKey().
 * Throws RuntimeError, ValueError.
 * @param PEM encoded serialized RSA private key
 */
pcrypto::pkenc::PrivateKey::PrivateKey(const std::string& encoded) {
    private_key_ = deserializeRSAPrivateKey(encoded);
}  // pcrypto::pkenc::PrivateKey::PrivateKey


/**
 * Move constructor.
 * Throws RuntimeError.
 */
pcrypto::pkenc::PrivateKey::PrivateKey(pcrypto::pkenc::PrivateKey&& privateKey) {
    private_key_ = privateKey.private_key_;
    privateKey.private_key_ = nullptr;
    if (private_key_ == nullptr) {
        std::string msg("Crypto Error (pkenc::PrivateKey() move): "
            "Cannot move null private key");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::pkenc::PrivateKey::PrivateKey (move constructor)


/**
 * Get Public encryption from PrivateKey.
 * Throws RuntimeError.
 */
pcrypto::pkenc::PublicKey pcrypto::pkenc::PrivateKey::GetPublicKey() const {
    PublicKey publicKey(*this);
    return publicKey;
}  // pcrypto::pkenc::PrivateKey::GetPublicKey
