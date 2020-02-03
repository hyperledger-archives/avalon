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
#include <openssl/rsa.h>
namespace tcf {
namespace crypto {
    namespace constants {
        //***RSA is not quantum resistant ***//
        //*** USE 3072 for long term security ***//
        const int RSA_KEY_SIZE = 2048;
        const int RSA_PADDING_SIZE = 41;

        //*** OAEP or better should always be used for RSA encryption ***//
        const int RSA_PADDING_SCHEME = RSA_PKCS1_OAEP_PADDING;
        constexpr int RSA_PLAINTEXT_LEN = ((RSA_KEY_SIZE - RSA_PADDING_SIZE) >> 3);
    }  // namespace constants
}  // namespace crypto
}  // namespace tcf
