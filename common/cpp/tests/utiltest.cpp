/*
 * Copyright 2020 Intel Corporation
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

/*
 * Test crypto utilities in crypto_utils.cpp.
 *
 * Test case from /tc/sgx/trusted_worker_manager/tests/testCrypto.cpp
 * and from upstream common/tests/testCrypto.cpp in
 * https://github.com/hyperledger-labs/private-data-objects
 *
 * SHA-256 digest computed with:
 * echo -n Hyperledger Avalon | openssl dgst -binary -sha256 | openssl base64
 */

#include <stdexcept>
#include <stdio.h>

#include "crypto_utils.h"
#include "error.h"       // tcf::error
#include "crypto.h"
#include "base64.h"      // base64_*code()
#include "utils.h"       // ByteArrayToHexEncodedString()


int
main(void)
{
    static const size_t rand_length = 32;
    bool is_ok;
    int  count = 0;
    // A short ByteArray for testing ValueError detection
    ByteArray rand;
    typedef struct {
        const char *plain;
        const char *encoded;
    } hash_test_type;
    static hash_test_type hash_test_cases[] = {
        {"Hyperledger Avalon", "22hKjT4z7yvB8D3Ros2/QykiYzXwkJIfJO89Df5xOtQ="},
        {"", "47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU="},
        {nullptr, nullptr}
    };

    printf("Random number test: RandomBitString()\n");
    try {
        rand = tcf::crypto::RandomBitString(rand_length);
        std::string rand_s = ByteArrayToHexEncodedString(rand);
        printf("RandomBitString generation PASSED:\n%s\n", rand_s.c_str());
    } catch (const std::exception& e) {
        printf("RandomBitString generation FAILED:\n%s\n", e.what());
        ++count;
    }

    // RandomBitString negative test
    try {
        rand = tcf::crypto::RandomBitString(0);
        printf("RandomBitString FAILED: invalid length undetected.\n");
        ++count;
    } catch (const tcf::error::ValueError& e) { // expected error here
        printf("RandomBitString PASSED: invalid length detected.\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf("RandomBitString FAILED: internal error:\n%s\n", e.what());
        ++count;
    }

    for (hash_test_type *tp = hash_test_cases; tp->encoded != nullptr; ++tp) {
        printf("Hash SHA-256 test: ComputeMessageHash()\n");
        std::string msgStr(tp->plain);
        ByteArray msg;
        msg.insert(msg.end(), msgStr.data(), msgStr.data() + msgStr.size());
        std::string msg_SHA256_B64(tp->encoded);
        ByteArray hash = tcf::crypto::ComputeMessageHash(msg);
        std::string hashStr_B64 = base64_encode(hash);
        if (hashStr_B64.compare(msg_SHA256_B64) != 0) {
            printf("FAILED: ComputeMessageHash(\"%s\"): "
                "SHA256 digest mismatch.\n", tp->plain);
            ++count;
        } else {
            printf("PASSED: ComputeMessageHash(\"%s\"): \n", tp->plain);
        }
    }


    // Key generation test: CreateHexEncodedEncryptionKey()
    // examples/apps/simple_wallet/workload/simple_wallet_execute_io.cpp
    printf("Test key generation: CreateHexEncodedEncryptionKey()\n");
    std::string enc_key = tcf::crypto::CreateHexEncodedEncryptionKey();
    printf("Key is: %s\n", enc_key.c_str());
    if (!enc_key.empty()) {
        printf("PASSED: CreateHexEncodedEncryptionKey()\n");
    } else {
        printf("FAILED: CreateHexEncodedEncryptionKey()\n");
        ++count;
    }

    printf("Test encryption: EncryptData()/DecryptData()\n");
    std::string test_data = "Hyperledger Avalon";
    std::string encrypted_data = tcf::crypto::EncryptData(test_data, enc_key);
    std::string decrypted_data = tcf::crypto::DecryptData(encrypted_data,
        enc_key);
    if (decrypted_data == test_data) {
        printf("PASSED: EncryptData()/DecryptData()\n");
    } else {
        printf("FAILED: EncryptData()/DecryptData()\n");
        ++count;
    }

    // Summarize
    if (count == 0) {
        printf("Crypto utility tests PASSED.\n");
    } else {
        printf("Crypto utility tests FAILED %d tests.\n", count);
    }

    return count;
}
