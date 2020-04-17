/* Copyright 2020 Intel Corporation
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


#include <sgx_tcrypto.h>

#include "avalon_sgx_error.h"
#include "tcf_error.h"
#include "signup_enclave_util.h"

void ComputeSHA256Hash(const std::string& src, uint8_t* data) {
    sgx_status_t ret = sgx_sha256_msg(
        reinterpret_cast<const uint8_t*>(src.c_str()),
        static_cast<uint32_t>(src.size()),
        reinterpret_cast<sgx_sha256_hash_t*>(data));
    tcf::error::ThrowSgxError(ret, "Failed to retrieve SHA256 hash of data");
}  // ComputeSHA256Hash
