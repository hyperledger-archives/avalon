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

#include <map>
#include <string>
#include <vector>

#include "error.h"
#include "tcf_error.h"

class SignupInfo {
public:
    friend SignupInfo* deserialize_signup_info(const std::string& s);

    std::string serialize() const {
        return serialized_;
    }

    // Signup info properties
    std::string verifying_key;
    std::string encryption_key;
    std::string sealed_signup_data;
    std::string proof_data;
    std::string enclave_persistent_id;

protected:
    tcf_err_t DeserializeSignupInfo(
        const std::string& serialized_signup_info);

    SignupInfo(
        const std::string& serializedSignupInfo);

private:
    /*
    Json serialization of the signup info Parameters, this serves as the
    canonical representation of the signup info.
    */
    std::string serialized_;
};  // class SignupInfo

SignupInfo* deserialize_signup_info(
    const std::string& serialized_signup_info);

std::map<std::string, std::string> CreateEnclaveData(
    const std::string& originator_public_key_hash);

std::map<std::string, std::string> UnsealEnclaveData(
    const std::string& sealed_enclave_data);

size_t VerifyEnclaveInfo(const std::string& enclaveInfo,
    const std::string& mr_enclave,
    const std::string& originator_public_key_hash);
