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

#include "sgx_urts.h"
#include "sgx_uae_service.h"

#include "error.h"
#include "tcf_error.h"
#include "types.h"

namespace tcf {

    namespace error {
        sgx_status_t ConvertErrorStatus(
            sgx_status_t ret,
            tcf_err_t tcfRet);
    }  // namespace error

    namespace enclave_api {

        class Enclave {
        public:
            Enclave();
            virtual ~Enclave();

            void Load(
                const std::string& inEnclaveFilePath);

            void Unload();

            size_t GetQuoteSize() const {
                return this->quoteSize;
            }  // GetQuoteSize

            size_t GetSealedSignupDataSize() const {
                return this->sealedSignupDataSize;
            }  // GetSealedSignupDataSize

            void GetEpidGroup(
                sgx_epid_group_id_t* outEpidGroup);

            void GetEnclaveCharacteristics(
                sgx_measurement_t* outEnclaveMeasurement,
                sgx_basename_t* outEnclaveBasename);

            void SetSpid(
                const HexEncodedString& inSpid);

            void SetSignatureRevocationList(
                const std::string& inSignatureRevocationList);

            void CreateQuoteFromReport(
                const sgx_report_t* inEnclaveReport,
                ByteArray& outEnclaveQuote);

            void ThrowTCFError(
                tcf_err_t err);

            sgx_status_t CallSgx(
                std::function<sgx_status_t(void)> sgxCall,
                int retries = 5,
                int retryDelayMs = 100);

            sgx_enclave_id_t GetEnclaveId() const {
                return this->enclaveId;
            }

            long GetThreadId() const {
                return this->threadId;
            }

        protected:
            void LoadEnclave();
            static void QuerySgxStatus();

            std::string enclaveFilePath;
            sgx_enclave_id_t enclaveId;
            long threadId;

            size_t quoteSize;
            size_t sealedSignupDataSize;

            std::string signatureRevocationList;
            sgx_spid_t spid;

            sgx_target_info_t reportTargetInfo;
            sgx_epid_group_id_t epidGroupId;

            std::string enclaveError;
        };  // class Enclave
    }  /* namespace enclave_api */
}  // namespace tcf


extern std::vector<tcf::enclave_api::Enclave> g_Enclave;
