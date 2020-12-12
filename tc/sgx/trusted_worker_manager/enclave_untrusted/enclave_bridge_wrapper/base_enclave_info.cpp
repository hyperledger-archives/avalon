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

#include <string.h>
#include "log.h"
#include "error.h"
#include "tcf_error.h"
#include "swig_utils.h"
#include "types.h"

#include "base.h"
#include "base_enclave_info.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
bool is_sgx_simulator() {
    return 0 != tcf::enclave_api::base::IsSgxSimulator();
}  // is_sgx_simulator

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void BaseEnclaveInfo::init_enclave_info(
    const std::string& enclave_module_path,
    const Attestation* attestation,
    const std::string& persisted_sealed_enclave_data,
    const int num_of_enclaves,
    const std::string& kss_config_id) {
    tcf::Log(TCF_LOG_INFO, "Initializing Avalon Intel SGX Enclave\n");

    const char* config = kss_config_id.c_str();
    size_t length = strlen(config) + 1;

    for (int i =0; i<length; ++i){ kss_config[i] = (uint8_t)(config[i]);}

    tcf_err_t ret = tcf::enclave_api::base::Initialize(
        enclave_module_path, attestation,
        persisted_sealed_enclave_data, num_of_enclaves, kss_config);
    ThrowTCFError(ret);
    tcf::Log(TCF_LOG_INFO, "Avalon Intel SGX Enclave initialized.\n");

    HexEncodedString mrEnclaveBuffer;
    HexEncodedString basenameBuffer;

    ThrowTCFError(
        tcf::enclave_api::base::GetEnclaveCharacteristics(
            mrEnclaveBuffer, basenameBuffer));

    this->mr_enclave = mrEnclaveBuffer;
    this->basename = basenameBuffer;

}  // BaseEnclaveInfo::init_enclave_info

void BaseEnclaveInfo::init_enclave_info(
    const std::string& enclave_module_path,
    const Attestation* attestation,
    const std::string& persisted_sealed_enclave_data,
    const int num_of_enclaves) {
    tcf::Log(TCF_LOG_INFO, "Initializing Avalon Intel SGX Enclave\n");

    tcf_err_t ret = tcf::enclave_api::base::Initialize(
        enclave_module_path, attestation,
        persisted_sealed_enclave_data, num_of_enclaves, kss_config);

    ThrowTCFError(ret);
    tcf::Log(TCF_LOG_INFO, "Avalon Intel SGX Enclave initialized.\n");

    HexEncodedString mrEnclaveBuffer;
    HexEncodedString basenameBuffer;

    ThrowTCFError(
        tcf::enclave_api::base::GetEnclaveCharacteristics(
            mrEnclaveBuffer, basenameBuffer));

    this->mr_enclave = mrEnclaveBuffer;
    this->basename = basenameBuffer;

}  // BaseEnclaveInfo::init_enclave_info

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
BaseEnclaveInfo::~BaseEnclaveInfo() {
    try {
        tcf::enclave_api::base::Terminate();
        TerminateInternal();
    } catch (...) {}

}  // BaseEnclaveInfo::~BaseEnclaveInfo
