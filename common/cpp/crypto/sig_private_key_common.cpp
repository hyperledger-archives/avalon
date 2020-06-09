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
 * Avalon ECDSA private key functions: generation, serialization, and signing.
 * Used for Secp256k1.
 *
 * No OpenSSL/Mbed TLS-dependent code is present.
 * See sig_private_key.cpp for OpenSSL/Mbed TLS-dependent code.
 */

#include "crypto_shared.h"
#include "error.h"
#include "hex_string.h"
#include "sig.h"
#include "sig_public_key.h"
#include "sig_private_key.h"

namespace pcrypto = tcf::crypto;
namespace constants = tcf::crypto::constants;
namespace Error = tcf::error; // Error handling


/**
 * Constructor from encoded string.
 * Throws RuntimeError, ValueError.
 *
 * @param encoded ECDSA private key string created by Generate()
 */
pcrypto::sig::PrivateKey::PrivateKey(const std::string& encoded) {
    private_key_ = deserializeECDSAPrivateKey(encoded);
}  // pcrypto::sig::PrivateKey::PrivateKey


/**
 * Move constructor.
 * Throws RuntimeError.
 *
 * @param privateKey ECDSA private key to move. Created by Generate()
 */
pcrypto::sig::PrivateKey::PrivateKey(pcrypto::sig::PrivateKey&& privateKey) {
    private_key_ = privateKey.private_key_;
    privateKey.private_key_ = nullptr;
    if (private_key_ = nullptr) {
        std::string msg("Crypto Error (sig::PrivateKey() move): "
            "Cannot move null private key");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::sig::PrivateKey::PrivateKey (move constructor)


/**
 * Derive ECDSA public key from private key.
 * Throws RuntimeError.
 */
pcrypto::sig::PublicKey pcrypto::sig::PrivateKey::GetPublicKey() const {
    PublicKey publicKey(*this);
    return publicKey;
}  // pcrypto::sig::GetPublicKey()
