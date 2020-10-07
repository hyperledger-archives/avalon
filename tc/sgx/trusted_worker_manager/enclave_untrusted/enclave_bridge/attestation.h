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

namespace tcf {

    namespace attestation {

        class Attestation {

        public:
            Attestation();
            virtual ~Attestation();
	    virtual tcf_err_t GetEnclaveCharacteristics(const sgx_enclave_id_t& enclaveId,
                sgx_measurement_t* outEnclaveMeasurement,
                sgx_basename_t* outEnclaveBasename) = 0;
            virtual size_t GetQuoteSize(void) = 0;
            virtual void CreateQuoteFromReport(const sgx_report_t* inEnclaveReport,
                                       ByteArray& outEnclaveQuote) = 0;

        protected:
            size_t quoteSize;
            sgx_target_info_t reportTargetInfo;

        };  // class Attestation

    }  /* namespace attestation */

}  // namespace tcf

