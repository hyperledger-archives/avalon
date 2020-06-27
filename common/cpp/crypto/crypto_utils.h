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
 * hashing, base 64 conversion, random number generation, key generation,
 * encrypt, and decrypt.
 */

#pragma once

#include <vector>
#include "types.h"

namespace tcf {
namespace crypto {
    /** SHA256 hashing. */
    namespace constants {
        /** SHA-256 digest length in bytes (256 bits) */
        const int DIGEST_LENGTH = 32;
    }  // namespace constants

    ByteArray ComputeMessageHash(const ByteArray& message);

    /** Generate a cryptographically strong random bitstring. */
    // throws RuntimeError
    ByteArray RandomBitString(size_t length);

    /** Create symmetric encryption key and return hex encoded key string. */
    std::string CreateHexEncodedEncryptionKey();

    /** Decrypt cipher using given encryption key and return message. */
    std::string DecryptData(std::string cipher, std::string key);

    /** Encrypt the message using given encryption key and return cipher. */
    std::string EncryptData(std::string msg, std::string key);
}  // namespace crypto
}  // namespace tcf
