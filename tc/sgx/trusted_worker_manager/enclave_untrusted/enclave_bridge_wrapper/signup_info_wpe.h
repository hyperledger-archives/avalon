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

#include <map>
#include <string>

std::map<std::string, std::string> CreateEnclaveDataWPE(
    const std::string& in_ext_data,
    const std::string& in_ext_data_signature,
    const std::string& in_kme_attestation);

size_t VerifyEnclaveInfoWPE(
    const std::string& enclaveInfo,
    const std::string& mr_enclave,
    const std::string& ext_data);
