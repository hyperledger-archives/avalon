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
 * Avalon RSA constant definitions.
 */

#pragma once

namespace tcf {
namespace crypto {
    namespace constants {
         /**
          * RSA key size, in bits.
          * Use RSA-3072 for long-term security,
          * with OAEP padding and SHA-256 digest.
          * RSA is not quantum resistant.
          */
        const int RSA_KEY_SIZE = 3072;
        /** Padding required, in bits, for OAEP padding. */
        const int RSA_PADDING_SIZE = 41;
        /**
         * Maximum amount, in bytes, of plain text that can
         * be encrypted with RSA. For longer lengths
         * use symmetric encryption or a larger key size.
         */
        constexpr int RSA_PLAINTEXT_LEN =
            ((RSA_KEY_SIZE - RSA_PADDING_SIZE) >> 3);
    }  // namespace constants
}  // namespace crypto
}  // namespace tcf
