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

#include "epid_enclave_info.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
epid_enclave_info::epid_enclave_info(
    const std::string& enclaveModulePath,
    const std::string& spid,
    const std::string& persistedSealedEnclaveData,
    const int num_of_enclaves) {
    this->epid_attestation = new tcf::attestation::EpidAttestation();
    this->epid_attestation->SetSpid(spid);

    this->init_enclave_info(enclaveModulePath, this->epid_attestation,
        persistedSealedEnclaveData,
        num_of_enclaves);
}  // epid_enclave_info::epid_enclave_info

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
epid_enclave_info::~epid_enclave_info() {

}  // epid_enclave_info::~epid_enclave_info

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
std::string epid_enclave_info::get_epid_group() {
    HexEncodedString epidGroupBuffer;
    this->epid_attestation->GetEpidGroup(epidGroupBuffer);

    return epidGroupBuffer;
}  // epid_enclave_info::get_epid_group

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void epid_enclave_info::set_signature_revocation_list(
    const std::string& signature_revocation_list) {
    this->epid_attestation->SetSignatureRevocationList(signature_revocation_list);

}  // epid_enclave_info::set_signature_revocation_lists
