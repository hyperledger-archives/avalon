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
 * Avalon ECDSA signature public key serialization and verification functions.
 * Used for Secp256k1 elliptical curves.
 *
 * No OpenSSL/Mbed TLS-dependent code is present.
 * See sig_public_key.cpp for OpenSSL/Mbed TLS-dependent code.
 */

#include "crypto_shared.h"
#include "error.h"
#include "hex_string.h"
#include "sig.h"
#include "sig_private_key.h"
#include "sig_public_key.h"

namespace pcrypto = tcf::crypto;
namespace constants = tcf::crypto::constants;
namespace Error = tcf::error; // Error handling


/**
 * PublicKey constructor.
 */
pcrypto::sig::PublicKey::PublicKey() {
    public_key_ = nullptr;
}  // pcrypto::sig::PublicKey::PublicKey


/**
 * Constructor from encoded string.
 * Throws RuntimeError, ValueError.
 *
 * @param encoded serialized public key
 */
pcrypto::sig::PublicKey::PublicKey(const std::string& encoded) {
    public_key_ = deserializeECDSAPublicKey(encoded);
}  // pcrypto::sig::PublicKey::PublicKey


/**
 * Move constructor.
 * Throws RuntimeError.
 *
 * @param publicKey Public key to move
 */
pcrypto::sig::PublicKey::PublicKey(pcrypto::sig::PublicKey&& publicKey) {
    public_key_ = publicKey.public_key_;
    publicKey.public_key_ = nullptr;
    if (public_key_ == nullptr) {
        std::string msg("Crypto Error (sig::PublicKey() move): "
            "Cannot move null public key");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::sig::PublicKey::PublicKey (move constructor)
