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

#include <Python.h>
#include <string>

#include "epid_attestation.h"

bool is_sgx_simulator();

class tcf_enclave_info {
public:
    tcf_enclave_info(const std::string& enclaveModulePath,
                     const std::string& spid,
                     const std::string& persisted_sealed_data,
                     const int num_of_enclaves);
    virtual ~tcf_enclave_info();
    std::string get_epid_group();
    void set_signature_revocation_list(
        const std::string& signature_revocation_list);

    std::string mr_enclave;         // hex encoding of the enclave measurement
    std::string basename;           // hex encoding of the basename
protected:
    tcf::attestation::EpidAttestation *epid_attestation;
};  // class tcf_enclave_info
