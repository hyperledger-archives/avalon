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

#include "dcap_enclave_info.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
dcap_enclave_info::dcap_enclave_info(
    const std::string& enclaveModulePath,
    const std::string& persistedSealedEnclaveData,
    const int num_of_enclaves) {
    this->dcap_attestation = new tcf::attestation::DcapAttestation();

    this->init_enclave_info(enclaveModulePath, this->dcap_attestation,
        persistedSealedEnclaveData,
        num_of_enclaves);
}  // dcap_enclave_info::dcap_enclave_info

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
dcap_enclave_info::~dcap_enclave_info() {

}  // dcap_enclave_info::~dcap_enclave_info
