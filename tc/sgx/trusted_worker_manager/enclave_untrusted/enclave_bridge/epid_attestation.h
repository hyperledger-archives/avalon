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
#include "types.h"
#include "attestation.h"

namespace tcf {

    namespace attestation {

        class EpidAttestation: public Attestation {

            public:
                EpidAttestation();
                virtual ~EpidAttestation();
	        tcf_err_t GetEnclaveCharacteristics(const sgx_enclave_id_t& enclave_id,
	            sgx_measurement_t* outEnclaveMeasurement,
                    sgx_basename_t* outEnclaveBasename);
                size_t GetQuoteSize(void);
                void CreateQuoteFromReport(const sgx_report_t* inEnclaveReport,
                    ByteArray& outEnclaveQuote);
		void GetEpidGroup(HexEncodedString& outEpidGroup);
	        void SetSpid(const HexEncodedString& inSpid);
	        void SetSignatureRevocationList (const std::string& inSignatureRevocationList);

            protected:
	        std::string signatureRevocationList;
                sgx_spid_t spid;
	        sgx_epid_group_id_t epidGroupId;
        };  // class EpidAttestation

    }  /* namespace attestation */

}  // namespace tcf

