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
#include <functional>
#include <memory>
#include <string>

#include "sgx_urts.h"
#include "sgx_uae_quote_ex.h"
#include "sgx_uae_epid.h"

#include "error.h"
#include "tcf_error.h"
#include "types.h"

class Attestation {

public:
    Attestation();
    virtual ~Attestation();
    virtual tcf_err_t GetEnclaveCharacteristics(
        const sgx_enclave_id_t& enclaveId,
        sgx_measurement_t* outEnclaveMeasurement,
        sgx_basename_t* outEnclaveBasename) = 0;
    virtual size_t GetQuoteSize(void) = 0;
    virtual void CreateQuoteFromReport(
        const sgx_report_t* inEnclaveReport,
        ByteArray& outEnclaveQuote) = 0;
    virtual void InitQuote(sgx_target_info_t &target_info) = 0;
#ifdef BUILD_SINGLETON
    virtual tcf_err_t VerifyEnclaveInfoSingleton(
        const std::string& enclaveInfo,
        const std::string& mr_enclave,
        const sgx_enclave_id_t& enclave_id) = 0;
#elif BUILD_KME
   virtual tcf_err_t VerifyEnclaveInfoKME(
        const std::string& enclaveInfo,
        const std::string& mr_enclave,
        const std::string& ext_data,
        const sgx_enclave_id_t& enclave_id) = 0;
#elif BUILD_WPE
    virtual tcf_err_t VerifyEnclaveInfoWPE(
        const std::string& enclaveInfo,
        const std::string& mr_enclave,
        const std::string& ext_data,
        const sgx_enclave_id_t& enclave_id) = 0;
#endif

protected:
    size_t quoteSize;
    sgx_target_info_t reportTargetInfo;

};  // class Attestation
