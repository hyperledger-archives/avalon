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

#include <iostream>
#include <vector>

#include "log.h"
#include "error.h"
#include "tcf_error.h"
#include "swig_utils.h"
#include "types.h"

#include "base.h"
#include "enclave_info.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
bool is_sgx_simulator() {
    return 0 != tcf::enclave_api::base::IsSgxSimulator();
}  // _is_sgx_simulator

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_enclave_info::tcf_enclave_info(
    const std::string& enclaveModulePath,
    const std::string& spid,
    const int num_of_enclaves
    ) {
    // tcf::logger::SetLogFunction(PyLog);
    // tcf::SetLogFunction(PyLog);

    // Todo: PyLogV logs are removed, as its crashing the process, needs investigation
    tcf::Log(TCF_LOG_INFO, "Initializing SGX TCF enclave\n");
    tcf::Log(TCF_LOG_DEBUG, "Enclave path: %s\n", enclaveModulePath.c_str());
    tcf::Log(TCF_LOG_DEBUG, "SPID: %s\n", spid.c_str());

    tcf_err_t ret = tcf::enclave_api::base::Initialize(enclaveModulePath, spid, num_of_enclaves);
    ThrowTCFError(ret);
    tcf::Log(TCF_LOG_INFO, "SGX TCF enclave initialized.\n");

    HexEncodedString mrEnclaveBuffer;
    HexEncodedString basenameBuffer;

    ThrowTCFError(
        tcf::enclave_api::base::GetEnclaveCharacteristics(
            mrEnclaveBuffer,
            basenameBuffer));

    this->mr_enclave = mrEnclaveBuffer;
    this->basename = basenameBuffer;

}  // tcf_enclave_info::tcf_enclave_info

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_enclave_info::~tcf_enclave_info() {
    try {
        tcf::enclave_api::base::Terminate();
        TerminateInternal();
    } catch (...) {}

}  // tcf_enclave_info::~tcf_enclave_info

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
std::string tcf_enclave_info::get_epid_group() {
    HexEncodedString epidGroupBuffer;
    ThrowTCFError(
        tcf::enclave_api::base::GetEpidGroup(epidGroupBuffer));

    return epidGroupBuffer;
}  // tcf_enclave_info::get_epid_group

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void tcf_enclave_info::set_signature_revocation_list(
    const std::string& signature_revocation_list) {
    ThrowTCFError(
        tcf::enclave_api::base::SetSignatureRevocationList(signature_revocation_list));

}  // tcf_enclave_info::set_signature_revocation_lists
