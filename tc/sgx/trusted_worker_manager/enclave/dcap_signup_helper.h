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

#pragma once

#include <string>

#include "tcf_error.h"
#include "signup_helper.h"

class DcapSignupHelper: public SignupHelper {
public:
       tcf_err_t verify_enclave_info(const char* enclave_info,
           const char* mr_enclave);
       VerificationStatus verify_attestation_report(const ByteArray& attestation_data,
           const ByteArray& hex_id,
           ByteArray& mr_enclave,
           ByteArray& mr_signer,
           ByteArray& encryption_public_key_hash,
           ByteArray& verification_key_hash);
};
