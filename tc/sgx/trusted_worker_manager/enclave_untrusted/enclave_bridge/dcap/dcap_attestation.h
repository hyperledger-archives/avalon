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

#include "error.h"
#include "tcf_error.h"
#include "sgx_error.h"
#include "types.h"
#include "attestation.h"

class DcapAttestation: public Attestation {

public:
    DcapAttestation();
    virtual ~DcapAttestation();
    tcf_err_t GetEnclaveCharacteristics(const sgx_enclave_id_t& enclave_id,
    sgx_measurement_t* outEnclaveMeasurement,
        sgx_basename_t* outEnclaveBasename);
    size_t GetQuoteSize(void);
    void CreateQuoteFromReport(const sgx_report_t* inEnclaveReport,
        ByteArray& outEnclaveQuote);
    void InitQuote(sgx_target_info_t& target_info);
#ifdef BUILD_SINGLETON
    tcf_err_t VerifyEnclaveInfoSingleton(const std::string& enclaveInfo,
        const std::string& mr_enclave,
        const sgx_enclave_id_t& enclave_id);
#elif BUILD_KME
    tcf_err_t VerifyEnclaveInfoKME(const std::string& enclaveInfo,
        const std::string& mr_enclave,
        const std::string& ext_data,
        const sgx_enclave_id_t& enclave_id);
#elif BUILD_WPE
    tcf_err_t VerifyEnclaveInfoWPE(const std::string& enclaveInfo,
        const std::string& mr_enclave,
        const std::string& ext_data,
        const sgx_enclave_id_t& enclave_id);
#endif

protected:
    tcf_err_t VerifyEnclaveInfo(const std::string& enclaveInfo,
        const sgx_enclave_id_t& enclave_id);

};  // class DcapAttestation
