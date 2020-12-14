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
#include <functional>
#include <memory>
#include <string>
#include <vector>

#include "error.h"
#include "tcf_error.h"
#include "types.h"

#include "attestation.h"

namespace tcf {

    namespace enclave_api {

        class Enclave {
        public:
            Enclave(const Attestation *attestation);
            virtual ~Enclave();

            void Load(
                const std::string& inEnclaveFilePath,
                const Base64EncodedString& inSealedEnclaveData);

            void Unload();

            size_t GetQuoteSize() const {
                tcf::error::ThrowIf<tcf::error::ValueError>(
                    this->attestation == nullptr,
                    "Attestation object is not initialized"
                );
                return this->attestation->GetQuoteSize();
            }  // GetQuoteSize

            size_t GetSealedSignupDataSize() const {
                return this->sealedSignupDataSize;
            }  // GetSealedSignupDataSize

            void GetEnclaveCharacteristics(
                sgx_measurement_t* outEnclaveMeasurement,
                sgx_basename_t* outEnclaveBasename);

            void CreateQuoteFromReport(
                const sgx_report_t* inEnclaveReport,
                ByteArray& outEnclaveQuote);

            void ThrowTCFError(tcf_err_t err);

            sgx_enclave_id_t GetEnclaveId() const {
                return this->enclaveId;
            }

            long GetThreadId() const {
                return this->threadId;
            }

	    void LoadEnclave(
                const Base64EncodedString& persistedSealedEnclaveData = "");

            void InitQuote(sgx_target_info_t& target_info);
#ifdef BUILD_SINGLETON
            tcf_err_t VerifyEnclaveInfoSingleton(
		const std::string& enclave_info,
                const std::string& mr_enclave,
                const sgx_enclave_id_t& enclave_id);
#elif BUILD_KME
            tcf_err_t VerifyEnclaveInfoKME(
		const std::string& enclave_info,
                const std::string& mr_enclave,
                const std::string& ext_data,
                const sgx_enclave_id_t& enclave_id);
#elif BUILD_WPE
            tcf_err_t VerifyEnclaveInfoWPE(
                const std::string& enclave_info,
                const std::string& mr_enclave,
                const std::string& ext_data,
                const sgx_enclave_id_t& enclave_id);
#endif

        protected:
            static void QuerySgxStatus();

            std::string enclaveFilePath;
            sgx_enclave_id_t enclaveId;
            long threadId;

            size_t sealedSignupDataSize;

            std::string enclaveError;
	    Attestation *attestation;

        };  // class Enclave

    }  /* namespace enclave_api */

}  // namespace tcf


extern std::vector<tcf::enclave_api::Enclave> g_Enclave;
