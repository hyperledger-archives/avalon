/* Copyright 2021 Intel Corporation
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

#include "sgx_report.h"
#include "tcf_error.h"
#include "types.h"

enum VerificationStatus {
    VERIFICATION_SUCCESS = 0, /// WPE registration success status
    VERIFICATION_FAILED = 1, /// WPE registration failure status
};

/* Interface for signup helper and it is
 * going to be implemented for EPID
 * and DCAP
 * */
class SignupHelper {
public:
    virtual tcf_err_t verify_enclave_info(const char* enclave_info,
       const char* mr_enclave)=0;
    std::string get_enclave_id();
    std::string get_enclave_encryption_key();
    sgx_report_data_t get_report_data();
    virtual VerificationStatus verify_attestation_report(const ByteArray& attestation_data,
       const ByteArray& hex_id,
       ByteArray& mr_enclave,
       ByteArray& mr_signer,
       ByteArray& encryption_public_key_hash,
       ByteArray& verification_key_hash)=0;
protected:
    std::string enclave_id;
    std::string enclave_encryption_key;
    sgx_report_data_t report_data;
};
