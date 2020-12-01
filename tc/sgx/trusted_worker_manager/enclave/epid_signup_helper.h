
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

#include <string>

class EpidSignupHelper {
public:
       tcf_err_t verify_enclave_info(const char* enclave_info,
           const char* mr_enclave);
       std::string get_enclave_id();
       std::string get_enclave_encryption_key();
       sgx_report_data_t get_report_data();
protected:
          std::string enclave_id;
          std::string enclave_encryption_key;
          sgx_report_data_t report_data;
};
