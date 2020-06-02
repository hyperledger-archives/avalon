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

#pragma once

#include "signup_info.h"

class SignupInfoKME : public SignupInfo {
public:

    SignupInfoKME() {}

    std::map<std::string, std::string> CreateEnclaveData(
        const std::string& in_ext_data,
        const std::string& in_ext_data_signature);

    std::map<std::string, std::string> UnsealEnclaveData();

    size_t VerifyEnclaveInfo(
        const std::string& enclaveInfo,
        const std::string& mr_enclave,
        const std::string& ext_data);

    static SignupInfo* DeserializeSignupInfo(
        const std::string& serialized_signup_info);

    std::string sealed_signup_data;

private:
    /*
    Json serialization of the signup info Parameters, this serves as the
    canonical representation of the signup info.
    */
    std::string serialized_;
};  // SignupInfoKME

