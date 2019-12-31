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

#pragma once

#include <vector>
#include "types.h"

namespace tcf {
namespace crypto {
    // SHA256 hashing
    ByteArray ComputeMessageHash(const ByteArray& message);

    // Generate a cryptographically strong random bitstring.
    // throws RuntimeError
    ByteArray RandomBitString(size_t length);

    // Wrapper function for EVP_DecodeBlock.
    // EVP_DecodeBlock pads its output with \0 if the output length
    // is not a multiple of 3. Check if the base64 string is padded at the end
    // and adjust the output length
    int EVP_DecodeBlock_wrapper(unsigned char* out, int out_len,
        const unsigned char* in, int in_len);

    // Decodes specified number of blocks of base64 encoded data
    int decode_base64_block(unsigned char *decoded_data,
        const unsigned char *base64_data, int num_of_blocks);

    // Create symmetric encryption key and return hex encoded key string
    std::string CreateHexEncodedEncryptionKey();

    // Decrypt cipher using given encryption key and return message
    std::string DecryptData(std::string cipher, std::string key);

    // Encrypt the message using given encryption key and return cipher
    std::string EncryptData(std::string msg, std::string key);
}  // namespace crypto
}  // namespace tcf
