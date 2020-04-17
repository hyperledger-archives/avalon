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

#include "types.h"
#include "swig_utils.h"

#include "signup_info.h"
#include "signup_kme.h"
#include "signup_info_kme.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
std::map<std::string, std::string> CreateEnclaveDataKME(
    const std::string& in_ext_data,
    const std::string& in_ext_data_signature) {

    tcf_err_t presult;
    // Create some buffers for receiving the output parameters
    // CreateEnclaveData will resize appropriately
    StringArray public_enclave_data(0);
    Base64EncodedString sealed_enclave_data;
    Base64EncodedString enclave_quote;

    // Create the signup data
    
    presult = tcf::enclave_api::enclave_data_kme::CreateEnclaveDataKME(
        in_ext_data, in_ext_data_signature, public_enclave_data,
        sealed_enclave_data, enclave_quote);
    ThrowTCFError(presult);

    // Parse the json and save the verifying and encryption keys
    std::string verifying_key;
    std::string encryption_key;
    std::string encryption_key_signature;

    presult = DeserializePublicEnclaveData(
        public_enclave_data.str(),
        verifying_key,
        encryption_key,
        encryption_key_signature);
    ThrowTCFError(presult);

    // Save the information
    std::map<std::string, std::string> result;
    result["verifying_key"] = verifying_key;
    result["encryption_key"] = encryption_key;
    result["encryption_key_signature"] = encryption_key_signature;
    result["sealed_enclave_data"] = sealed_enclave_data;
    result["enclave_quote"] = enclave_quote;

    return result;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
size_t VerifyEnclaveInfoKME(
    const std::string& enclave_info,
    const std::string& mr_enclave,
    const std::string& ext_data) {

    tcf_err_t result = tcf::enclave_api::enclave_data_kme::VerifyEnclaveInfoKME(
        enclave_info, mr_enclave, ext_data);
    size_t verify_status = result;
    return verify_status;
}  // VerifyEnclaveInfoKME
