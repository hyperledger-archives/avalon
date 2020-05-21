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
 * Test base64 functions:
 * - OpenSSL EVP_DecodeBlock() used in signature verification
 * - Avalon base64_encode()
 * - Avalon base64_decode()
 * See https://tools.ietf.org/html/rfc4648
 */

#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include "crypto_shared.h" // Sets default CRYPTOLIB_* value
#ifdef CRYPTOLIB_OPENSSL
#include <openssl/evp.h> // EVP_DecodeBlock()
#endif
#include "types.h"       // ByteArray
#include "utils.h"       // ByteArrayToStr()
#include "base64.h"      // base64_*code()

static const char rsa_2048_signature[] =
    "TuHse3QCPZtyZP436ltUAc6cVlIDzwKyjguOBDMmoou/NlGylzY0EtOEbHvVZ28H"
    "T8U1CiCVVmZso2ut2HY3zFDfpUg5/FV7FUSw/UhDOu3xkDwicrOvd/P1C3BKWJ6v"
    "JWghv3QLpgDItQPapFH/3OfciWs10kC3KV4UY+Irkrrck9+h3+FaltM/52AL1m1Q"
    "WZIutMk1gDs5nz5N87gGvbc9VJKXx/RDDmvX1rLfqnPpH3owkprVLhU8iLcmPPN+"
    "irjfH4f4GGrnbWYCYK5wfB1BBbFl8ppqxm4Gr8ekePCPLMjYYLpKYWEipvTgaYl6"
    "3zg+C9r8g+sIA3I9Jr3Exg==";

static const char rsa_2048_signature_decoded[256] = {
    '\x4e', '\xe1', '\xec', '\x7b', '\x74', '\x02', '\x3d', '\x9b',
    '\x72', '\x64', '\xfe', '\x37', '\xea', '\x5b', '\x54', '\x01',
    '\xce', '\x9c', '\x56', '\x52', '\x03', '\xcf', '\x02', '\xb2',
    '\x8e', '\x0b', '\x8e', '\x04', '\x33', '\x26', '\xa2', '\x8b',
    '\xbf', '\x36', '\x51', '\xb2', '\x97', '\x36', '\x34', '\x12',
    '\xd3', '\x84', '\x6c', '\x7b', '\xd5', '\x67', '\x6f', '\x07',
    '\x4f', '\xc5', '\x35', '\x0a', '\x20', '\x95', '\x56', '\x66',
    '\x6c', '\xa3', '\x6b', '\xad', '\xd8', '\x76', '\x37', '\xcc',
    '\x50', '\xdf', '\xa5', '\x48', '\x39', '\xfc', '\x55', '\x7b',
    '\x15', '\x44', '\xb0', '\xfd', '\x48', '\x43', '\x3a', '\xed',
    '\xf1', '\x90', '\x3c', '\x22', '\x72', '\xb3', '\xaf', '\x77',
    '\xf3', '\xf5', '\x0b', '\x70', '\x4a', '\x58', '\x9e', '\xaf',
    '\x25', '\x68', '\x21', '\xbf', '\x74', '\x0b', '\xa6', '\x00',
    '\xc8', '\xb5', '\x03', '\xda', '\xa4', '\x51', '\xff', '\xdc',
    '\xe7', '\xdc', '\x89', '\x6b', '\x35', '\xd2', '\x40', '\xb7',
    '\x29', '\x5e', '\x14', '\x63', '\xe2', '\x2b', '\x92', '\xba',
    '\xdc', '\x93', '\xdf', '\xa1', '\xdf', '\xe1', '\x5a', '\x96',
    '\xd3', '\x3f', '\xe7', '\x60', '\x0b', '\xd6', '\x6d', '\x50',
    '\x59', '\x92', '\x2e', '\xb4', '\xc9', '\x35', '\x80', '\x3b',
    '\x39', '\x9f', '\x3e', '\x4d', '\xf3', '\xb8', '\x06', '\xbd',
    '\xb7', '\x3d', '\x54', '\x92', '\x97', '\xc7', '\xf4', '\x43',
    '\x0e', '\x6b', '\xd7', '\xd6', '\xb2', '\xdf', '\xaa', '\x73',
    '\xe9', '\x1f', '\x7a', '\x30', '\x92', '\x9a', '\xd5', '\x2e',
    '\x15', '\x3c', '\x88', '\xb7', '\x26', '\x3c', '\xf3', '\x7e',
    '\x8a', '\xb8', '\xdf', '\x1f', '\x87', '\xf8', '\x18', '\x6a',
    '\xe7', '\x6d', '\x66', '\x02', '\x60', '\xae', '\x70', '\x7c',
    '\x1d', '\x41', '\x05', '\xb1', '\x65', '\xf2', '\x9a', '\x6a',
    '\xc6', '\x6e', '\x06', '\xaf', '\xc7', '\xa4', '\x78', '\xf0',
    '\x8f', '\x2c', '\xc8', '\xd8', '\x60', '\xba', '\x4a', '\x61',
    '\x61', '\x22', '\xa6', '\xf4', '\xe0', '\x69', '\x89', '\x7a',
    '\xdf', '\x38', '\x3e', '\x0b', '\xda', '\xfc', '\x83', '\xeb',
    '\x08', '\x03', '\x72', '\x3d', '\x26', '\xbd', '\xc4', '\xc6'};


int
main(void)
{
    typedef struct {
        const char *plain;
        const char *encoded;
        unsigned int plain_len;
    } b64_test_type;
    static b64_test_type b64_test_cases[] = {
        {"Hyperledger Avalon", "SHlwZXJsZWRnZXIgQXZhbG9u", 18},
        {"Hyperledger", "SHlwZXJsZWRnZXI=", 11},
        {"Hype", "SHlwZQ==", 4},
        {"H", "SA==", 1},
        {"", "", 0},
        {rsa_2048_signature_decoded, rsa_2048_signature, 256},
        {nullptr, nullptr}
    };
    static b64_test_type negative_test_cases[] = {
        {nullptr, "`~!@#$%^&*()-_|':;?>,,.\\", 0},
        {nullptr, "===", 0},
        {nullptr, "==", 0},
        {nullptr, "=", 0},
        {nullptr, nullptr, 0}
    };
    char buffer[256 + 3];
    int  rc, count = 0;
    ByteArray v;
    std::string out_str;

    for (b64_test_type *tp = b64_test_cases; tp->encoded != nullptr; ++tp) {
#ifdef CRYPTOLIB_OPENSSL
        // Test OpenSSL decode
        memset(buffer, 0, sizeof (buffer));
        rc = EVP_DecodeBlock((unsigned char *)buffer,
            (unsigned char *)tp->encoded, strlen(tp->encoded));
        if (rc < 0 || strcmp(buffer, tp->plain) != 0) {
            printf("\nEVP_DecodeBlock FAILED\n");
            printf("    rc %d, expected strlen plain %ld\n",
                rc, strlen(tp->plain));
            printf("    encoded %s, expected plain %s\n",
                tp->encoded, tp->plain);
            printf("    actual result %s\n", buffer);
            ++count;
        } else {
            if (rc > 0 && rc < 32) { // only print short strings
                printf("EVP_DecodeBlock PASSED: %s --> %s\n",
                    tp->encoded, buffer);
            } else {
                printf("EVP_DecodeBlock PASSED: length %lu --> rc %d\n",
                    strlen(tp->encoded), rc);
            }
        }
#endif

        // Test Avalon C++ decode
        v = base64_decode(std::string(tp->encoded));
        std::string s = ByteArrayToStr(v);
        unsigned char *out_cstr = (unsigned char *)s.c_str();
        unsigned int out_len = s.size();
        if (out_len != tp->plain_len ||
                (out_len > 0 &&
                 strncmp((char *)out_cstr, tp->plain, tp->plain_len) != 0)) {
            printf("\nbase64_decode FAILED\n");
            printf("    encoded %s, expected plain %s\n",
                tp->encoded, tp->plain);
            printf("    actual result %s\n", out_cstr);
            ++count;
        } else {
            printf("base64_decode   PASSED: %s, length %lu --> len %d\n",
                tp->encoded, strlen(tp->encoded), out_len);
        }

        // Test Avalon C++ encode
        ByteArray in_vec(&tp->plain[0], &tp->plain[tp->plain_len]);
        out_str = base64_encode(in_vec);
        if (out_str.size() != strlen(tp->encoded) ||
                (out_str.size() > 0 &&
                 strncmp((char *)out_str.c_str(), tp->encoded,
                     strlen(tp->encoded)) != 0)) {
            printf("\nbase64_encode FAILED\n");
            printf("    plain %s, expected encoded %s\n",
                tp->plain, tp->encoded);
            printf("    actual result %s\n", out_str.c_str());
            ++count;
        } else {
            printf("base64_encode   PASSED: length %u --> len %lu\n",
                tp->plain_len, out_str.size());
        }

    }

    // Negative tests
    for (b64_test_type *ntp = negative_test_cases; ntp->encoded != nullptr;
            ++ntp) {
#ifdef CRYPTOLIB_OPENSSL
        // Test OpenSSL decode
        rc = EVP_DecodeBlock((unsigned char *)buffer,
            (unsigned char *)ntp->encoded, strlen(ntp->encoded));
        if (rc < 0) {
            printf("Negative test EVP_DecodeBlock(%s) PASSED\n", ntp->encoded);
        } else {
            printf("Negative test EVP_DecodeBlock(%s) FAILED\n", ntp->encoded);
            ++count;
        }
#endif

        // Test Avalon C++ decode
        v = base64_decode(std::string(ntp->encoded));
        if (v.empty()) {
            printf("Negative test b64_decode(%s) PASSED\n", ntp->encoded);
        } else {
            printf("Negative test b64_decode(%s) FAILED\n", ntp->encoded);
            ++count;
        }

    }

    // Summarize
    if (count == 0) {
        printf("Base64 Decode tests PASSED.\n");
    } else {
        printf("Base64 Decode FAILED %d tests.\n", count);
    }
    return count;
}
