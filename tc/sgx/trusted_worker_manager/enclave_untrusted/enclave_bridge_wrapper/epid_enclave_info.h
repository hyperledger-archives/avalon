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

#include "base_enclave_info.h"
#include "epid_attestation.h"

class EpidEnclaveInfo: public BaseEnclaveInfo {
public:
    EpidEnclaveInfo(const std::string& enclave_module_path,
        const std::string& spid, const std::string& persisted_sealed_data,
        const int num_of_enclaves);
    virtual ~EpidEnclaveInfo();
    std::string get_epid_group();
    void set_signature_revocation_list(
        const std::string& signature_revocation_list);
protected:
    EpidAttestation *epid_attestation;
};  // class EpidEnclaveInfo
