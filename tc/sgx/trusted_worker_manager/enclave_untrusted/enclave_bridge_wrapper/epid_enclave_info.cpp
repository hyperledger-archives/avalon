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

#include "epid_enclave_info.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
EpidEnclaveInfo::EpidEnclaveInfo(
    const std::string& enclave_module_path,
    const std::string& spid,
    const std::string& persisted_sealed_enclave_data,
    const int num_of_enclaves) {

    this->epid_attestation = new EpidAttestation();
    this->epid_attestation->SetSpid(spid);

    this->init_enclave_info(enclave_module_path, this->epid_attestation,
        persisted_sealed_enclave_data, num_of_enclaves);
}  // EpidEnclaveInfo::EpidEnclaveInfo

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
EpidEnclaveInfo::~EpidEnclaveInfo() {

}  // EpidEnclaveInfo::~EpidEnclaveInfo

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
std::string EpidEnclaveInfo::get_epid_group() {
    HexEncodedString epidGroupBuffer;
    this->epid_attestation->GetEpidGroup(epidGroupBuffer);

    return epidGroupBuffer;
}  // EpidEnclaveInfo::get_epid_group

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void EpidEnclaveInfo::set_signature_revocation_list(
    const std::string& signature_revocation_list) {
    this->epid_attestation->SetSignatureRevocationList(signature_revocation_list);

}  // EpidEnclaveInfo::set_signature_revocation_lists
