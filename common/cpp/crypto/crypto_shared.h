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

// Private header file with common constant definitions
// to implement crypto functions. Not for use by non-crypto consumers.
// Must be included by *.cpp files in this directory before other header files
// in this directory.

#pragma once

#if defined(CRYPTOLIB_OPENSSL) && defined(CRYPTOLIB_MBEDTLS)
#error "CRYPTOLIB_OPENSSL and CRYPTOLIB_MBEDTLS cannot both be defined at once"
#endif
#if !defined(CRYPTOLIB_OPENSSL) && !defined(CRYPTOLIB_MBEDTLS)
#define CRYPTOLIB_OPENSSL // default
#endif

#ifdef CRYPTOLIB_OPENSSL
#include <openssl/obj_mac.h> // NID_*
#include <openssl/rsa.h>
#endif

namespace tcf {
namespace crypto {
    namespace constants {
#ifdef CRYPTOLIB_OPENSSL
        // OpenSSL: Secp256k1 elliptical curve cryptography
        const int CURVE = NID_secp256k1;
        // OpenSSL: OAEP padding or better should always be used for RSA
        const int RSA_PADDING_SCHEME = RSA_PKCS1_OAEP_PADDING;
        // OpenSSL Error string buffer size
        const unsigned int ERR_BUF_LEN = 130;
#elif defined (CRYPTOLIB_MBEDTLS)
        // Longest expected cert is 4K. Double a few more times for safety.
        const unsigned int MAX_PEM_LEN = 16000;
#endif
    }  // namespace constants
}  // namespace crypto
}  // namespace tcf
