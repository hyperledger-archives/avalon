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

#include <map>
#include <string>
#include <vector>

#include "error.h"
#include "tcf_error.h"

class SignupInfo {
public:
    SignupInfo() {}

    std::string serialize() const {
        return serialized_;
    }

    tcf_err_t DeserializePublicEnclaveData(
        const std::string& public_enclave_data,
        std::string& verifying_key,
        std::string& encryption_key,
        std::string& encryption_key_signature);

    tcf_err_t DeserializeSignupInfo(const std::string& serialized_signup_info);

    // Signup info properties
    std::string verifying_key;
    std::string encryption_key;
    std::string encryption_key_signature;
    std::string proof_data;
    std::string enclave_persistent_id;

private:
    /*
    Json serialization of the signup info Parameters, this serves as the
    canonical representation of the signup info.
    */
    std::string serialized_;
};  // class SignupInfo
