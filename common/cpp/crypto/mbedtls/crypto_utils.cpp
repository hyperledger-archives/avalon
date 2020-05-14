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
 * Avalon Crypto Utilities:
 * hashing, base 64 conversion, random number generation.
 * Implemented using Mbed TLS.
 */

#include <mbedtls/entropy.h>
#include <mbedtls/ctr_drbg.h>
#include <mbedtls/sha256.h>

#include "crypto_shared.h"
#include "crypto_utils.h"
#include "error.h"
#include "tcf_error.h"

#ifndef CRYPTOLIB_MBEDTLS
#error "CRYPTOLIB_MBEDTLS must be defined to compile source with Mbed TLS."
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
    static mbedtls_ctr_drbg_context ctr_drbg;
    ByteArray buf(length);
    int res = 0;

    if (length < 1) {
        std::string msg("Crypto Error (RandomBitString): "
            "length argument must be at least 1");
        throw Error::ValueError(msg);
    }

    // One-time initialization
    static bool init = false;
    if (!init) {
        static const unsigned char *custom =
            (const unsigned char *)"Hyperledger Avalon";
        mbedtls_entropy_context  entropy;

        mbedtls_entropy_init(&entropy);
        mbedtls_ctr_drbg_init(&ctr_drbg);

        res = mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func,
            &entropy, custom, sizeof (custom));
        if (res != 0) {
            std::string msg("Crypto Error (RandomBitString): "
                "mbedtls_ctr_drbg_seed() failed");
            throw Error::RuntimeError(msg);
        }
        init = true;
    }

    // Generate randomness
    res = mbedtls_ctr_drbg_random(&ctr_drbg, buf.data(), length);
    if (res != 0) {
        std::string msg("Crypto Error (RandomBitString): "
            "mbedtls_ctr_drbg_random() failed");
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

    mbedtls_sha256_ret((const unsigned char*)message.data(), message.size(),
        hash.data(), 0);
    return hash;
}  // pcrypto::ComputeMessageHash
