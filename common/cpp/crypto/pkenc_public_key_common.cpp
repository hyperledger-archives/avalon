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
 * Avalon RSA public key serialization and encryption functions.
 * Serialization reads and writes keys in PEM format strings.
 *
 * No OpenSSL/Mbed TLS-dependent code is present.
 * See pkenc_public_key.cpp for OpenSSL/Mbed TLS-dependent code.
 */

#include "crypto_shared.h"
#include "error.h"
#include "hex_string.h"
#include "pkenc.h"
#include "pkenc_public_key.h"

namespace pcrypto = tcf::crypto;
namespace constants = tcf::crypto::constants;
namespace Error = tcf::error; // Error handling


/**
 * PublicKey constructor.
 */
pcrypto::pkenc::PublicKey::PublicKey() {
    public_key_ = nullptr;
}  // pcrypto::sig::PublicKey::PublicKey


/**
 * Constructor from a PEM encoded string.
 * That is, convert the key from a PEM format string
 * (begins with either "BEGIN RSA PUBLIC KEY" or "BEGIN PUBLIC KEY").
 *
 * Implemented with deserializeRSAPublicKey().
 * Throws RuntimeError, ValueError.
 *
 * @param PEM encoded serialized RSA public key
 */
pcrypto::pkenc::PublicKey::PublicKey(const std::string& encoded) {
    public_key_ = deserializeRSAPublicKey(encoded);
}  // pcrypto::pkenc::PublicKey::PublicKey


/**
 * Move constructor.
 * Throws RuntimeError.
 */
pcrypto::pkenc::PublicKey::PublicKey(pcrypto::pkenc::PublicKey&& publicKey) {
    public_key_ = publicKey.public_key_;
    publicKey.public_key_ = nullptr;
    if (public_key_ == nullptr) {
        std::string msg("Crypto Error (pkenc::PublicKey() move): "
            "Cannot move null public key");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::pkenc::PublicKey::PublicKey (move constructor)
