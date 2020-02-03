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

#include <string.h>
#include <assert.h>
#include <openssl/err.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <openssl/x509v3.h>
#include <openssl/pem.h>
#include <algorithm>
#include <memory>
#include <vector>

#include "base64.h"  // Simple base64 enc/dec routines
#include "crypto_shared.h"
#include "crypto_utils.h"
#include "error.h"
#include "tcf_error.h"
#include "hex_string.h"
#include "c11_support.h"
#include "crypto.h"
#include "utils.h"
/*** Conditional compile untrusted/trusted ***/
#if _UNTRUSTED_
#include <openssl/crypto.h>
#include <stdio.h>

// memcpy_s definition is not present in std C library, hence mapping to memcpy
#define memcpy_s(dest, dest_size, src, count) memcpy(dest, src, count)
#else
#include "tSgxSSL_api.h"
#endif
/*** END Conditional compile untrusted/trusted ***/

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

int pcrypto::EVP_DecodeBlock_wrapper(unsigned char* out,
                                     int out_len,
                                     const unsigned char* in,
                                     int in_len) {
    /* Use a temporary output buffer. We do not want to disturb the
       original output buffer with extraneous \0 bytes. */
    unsigned char buf[in_len];

    int ret = EVP_DecodeBlock(buf, in, in_len);
    assert(ret != -1);
    if (in[in_len - 1] == '=' && in[in_len - 2] == '=')
    {
        ret -= 2;
    }
    else if (in[in_len - 1] == '=')
    {
        ret -= 1;
    }

    memcpy_s(out, out_len, buf, ret);
    return ret;
}

int pcrypto::decode_base64_block(unsigned char *decoded_data,
                                 const unsigned char *base64_data,
                                 int num_of_blocks) {
    return EVP_DecodeBlock(decoded_data, base64_data, num_of_blocks);
}

// Create symmetric encryption key and return hex encoded key string
std::string pcrypto::CreateHexEncodedEncryptionKey() {
    ByteArray enc_key = tcf::crypto::skenc::GenerateKey();
    return ByteArrayToHexEncodedString(enc_key);
}   // pcrypto::CreateHexEncodedEncryptionKey

// Decrypt cipher using given encryption key and return message
std::string pcrypto::DecryptData(std::string cipher, std::string key) {
    ByteArray ciphers_bytes = Base64EncodedStringToByteArray(cipher);
    ByteArray key_bytes = tcf::HexStringToBinary(key);
    ByteArray msg = tcf::crypto::skenc::DecryptMessage(key_bytes, ciphers_bytes);
    return ByteArrayToStr(msg);
}  // pcrypto::DecryptData

// Encrypt the message using given encryption key and return cipher
std::string pcrypto::EncryptData(std::string msg, std::string key) {
    ByteArray msg_bytes = StrToByteArray(msg);
    ByteArray key_bytes = tcf::HexStringToBinary(key);
    ByteArray cipher = tcf::crypto::skenc::EncryptMessage(key_bytes, msg_bytes);
    return ByteArrayToBase64EncodedString(cipher);
}  // pcrypto::EncryptData
