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
#include "crypto_utils.h"
#include <openssl/err.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <algorithm>
#include <memory>
#include <vector>
#include "base64.h"  //simple base64 enc/dec routines
#include "crypto_shared.h"
#include "error.h"
#include "hex_string.h"
/***Conditional compile untrusted/trusted***/
#if _UNTRUSTED_
#include <openssl/crypto.h>
#include <stdio.h>
#else
#include "tSgxSSL_api.h"
#endif
/***END Conditional compile untrusted/trusted***/

namespace pcrypto = tcf::crypto;
namespace constants = tcf::crypto::constants;

// Error handling
namespace Error = tcf::error;

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Generate a cryptographically strong random bit string
// throws: RuntimeError
ByteArray pcrypto::RandomBitString(size_t length) {
    char err[constants::ERR_BUF_LEN];
    ByteArray buf(length);
    int res = 0;

    if (length < 1) {
        std::string msg("Crypto Error (RandomBitString): length argument must be at least 1");
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

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Compute SHA256 hash of message.data()
// returns ByteArray containing raw binary data
ByteArray pcrypto::ComputeMessageHash(const ByteArray& message) {
    ByteArray hash(SHA256_DIGEST_LENGTH);
    SHA256((const unsigned char*)message.data(), message.size(), hash.data());
    return hash;
}  // pcrypto::ComputeMessageHash
