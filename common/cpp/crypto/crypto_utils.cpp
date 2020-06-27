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
 * Avalon Crypto Utilities:
 * hashing, base 64 conversion, random number generation.
 * Implemented using OpenSSL.
 */

#include <openssl/err.h>
#include <openssl/rand.h>
#include <openssl/sha.h>

#include "crypto_shared.h"
#include "crypto_utils.h"
#include "error.h"
#include "tcf_error.h"

#ifndef CRYPTOLIB_OPENSSL
#error "CRYPTOLIB_OPENSSL must be defined to compile source with OpenSSL."
#endif

namespace pcrypto = tcf::crypto;
namespace constants = tcf::crypto::constants;

// Error handling
namespace Error = tcf::error;


/**
 * Generate a cryptographically strong random bit string.
 * Throws: RuntimeError.
 *
 * @param length Length of random bit string in bytes
 * @returns byte array with binary random bits
 */
ByteArray pcrypto::RandomBitString(size_t length) {
    char err[constants::ERR_BUF_LEN];
    ByteArray buf(length);
    int res = 0;

    if (length < 1) {
        std::string msg("Crypto Error (RandomBitString): "
            "length argument must be at least 1");
        throw Error::ValueError(msg);
    }

    res = RAND_bytes(buf.data(), length);

    if (res != 1) {
        std::string msg("Crypto Error (RandomBitString): ");
        ERR_load_crypto_strings();
        ERR_error_string(ERR_get_error(), err);
        msg += err;
        throw Error::RuntimeError(msg);
    }

    return buf;
}  // pcrypto::RandomBitString


/**
 * Compute SHA256 hash of message.data().
 * Returns ByteArray containing raw binary data.
 * Call base64_encode() to convert to a base64 string.
 *
 * @param message Data in a byte array to hash
 * @returns byte array containing binary hash of data
 */
ByteArray pcrypto::ComputeMessageHash(const ByteArray& message) {
    ByteArray hash(constants::DIGEST_LENGTH);

    SHA256((const unsigned char*)message.data(), message.size(), hash.data());
    return hash;
}  // pcrypto::ComputeMessageHash
