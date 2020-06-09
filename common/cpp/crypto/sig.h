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
 * Constants used for Avalon ECDSA signature public key signing and
 * verification functions with ECC curve Secp256k1.
 */

#pragma once

namespace tcf {
namespace crypto {
    namespace constants {
        /**
          * ECDSA Secp256k1 signature size, in bytes:
          * 64 bytes (512b) + 8 byte DER prefix
          */
        const int MAX_SIG_SIZE = 72;
    }  // namespace constants
}  // namespace crypto
}  // namespace tcf
