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

#include <algorithm>
#include <string>

#include "epid_attestation.h"
#include "sgx_utility.h"
#include "avalon_sgx_error.h"
#include "zero.h"
#include "hex_string.h"
#include "enclave_common_u.h"

namespace tcf {

    namespace attestation {

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
	EpidAttestation::EpidAttestation() {
            uint32_t size;
            sgx_status_t ret = sgx_calc_quote_size(nullptr, 0, &size);
            tcf::error::ThrowSgxError(ret,
                "Failed to get Intel SGX quote size.");
            this->quoteSize = size;
            
            // Initialize the targetinfo and epid variables
            ret = tcf::sgx_util::CallSgx([this] () {
                return sgx_init_quote(&this->reportTargetInfo, &this->epidGroupId);
            });
            tcf::error::ThrowSgxError(ret, "Failed to initialize quote in enclave constructor");
        } //EpidAttestation::EpidAttestation

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        EpidAttestation::~EpidAttestation() {

        }

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
	tcf_err_t EpidAttestation::GetEnclaveCharacteristics(const sgx_enclave_id_t& enclave_id,
			                                sgx_measurement_t* outEnclaveMeasurement,
                                                        sgx_basename_t* outEnclaveBasename) {
            tcf::error::ThrowIfNull(
                outEnclaveMeasurement,
                "Enclave measurement pointer is NULL");
            tcf::error::ThrowIfNull(
                outEnclaveBasename,
                "Enclave basename pointer is NULL");

            Zero(outEnclaveMeasurement, sizeof(*outEnclaveMeasurement));
            Zero(outEnclaveBasename, sizeof(*outEnclaveBasename));

            // We can get the enclave's measurement (i.e., mr_enclave) and
            // basename only by getting a quote. To do that, we need to first
            // generate a report.

            // Initialize a quote
            sgx_target_info_t targetInfo = { 0 };
            sgx_epid_group_id_t gid = { 0 };

            sgx_status_t ret = tcf::sgx_util::CallSgx([&targetInfo, &gid] () {
                    return sgx_init_quote(&targetInfo, &gid);
                });
            tcf::error::ThrowSgxError(ret, "Failed to initialize enclave quote");

            // Now retrieve a fake enclave report so that we can later
            // create a quote from it. We need to the quote so that we can
            // get some of the information (basename and mr_enclave,
            // specifically) being requested.
            sgx_report_t enclaveReport = { 0 };
            tcf_err_t tcfRet = TCF_SUCCESS;
            ret = tcf::sgx_util::CallSgx(
                    [&enclave_id,
                     &tcfRet,
                     &targetInfo,
                     &enclaveReport] () {
                        sgx_status_t ret =
                        ecall_CreateErsatzEnclaveReport(
                            enclave_id,
                            &tcfRet,
                            &targetInfo,
                            &enclaveReport);
                        return error::ConvertErrorStatus(ret, tcfRet);
                    });
            tcf::error::ThrowSgxError(
                ret,
                "Failed to retrieve ersatz enclave report");
            if (tcfRet != TCF_SUCCESS) {
		return tcfRet;
	    }

            // Properly size a buffer to receive an enclave quote and then
            // retrieve it. The enclave quote contains the basename.
            ByteArray enclaveQuoteBuffer(this->quoteSize);
            sgx_quote_t* enclaveQuote = reinterpret_cast<sgx_quote_t *>(&enclaveQuoteBuffer[0]);
            const uint8_t* pRevocationList = nullptr;
            if (this->signatureRevocationList.size()) {
                pRevocationList = reinterpret_cast<const uint8_t *>(
                        this->signatureRevocationList.c_str());
            }

            ret = tcf::sgx_util::CallSgx(
                    [this,
                     &enclaveReport,
                     pRevocationList,
                     &enclaveQuoteBuffer] () {
                        return
                        sgx_get_quote(
                            &enclaveReport,
                            SGX_LINKABLE_SIGNATURE,
                            &this->spid,
                            nullptr,
                            pRevocationList,
                            static_cast<uint32_t>(
                                this->signatureRevocationList.size()),
                            nullptr,
                            reinterpret_cast<sgx_quote_t *>(
                                &enclaveQuoteBuffer[0]),
                            static_cast<uint32_t>(enclaveQuoteBuffer.size()));
                    });
            tcf::error::ThrowSgxError(
                ret,
                "Failed to create linkable quote for enclave report");

            // Copy the mr_enclave and basename to the caller's buffers
            memcpy_s(
                outEnclaveMeasurement,
                sizeof(*outEnclaveMeasurement),
                &enclaveQuote->report_body.mr_enclave,
                sizeof(*outEnclaveMeasurement));
            memcpy_s(
                outEnclaveBasename,
                sizeof(*outEnclaveBasename),
                &enclaveQuote->basename,
                sizeof(*outEnclaveBasename));
            return TCF_SUCCESS;
        }  // EpidAttestation::GetEnclaveCharacteristics

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        size_t EpidAttestation::GetQuoteSize(void) {
            return this->quoteSize;
        } // GetQuoteSize

	// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        void EpidAttestation::CreateQuoteFromReport(const sgx_report_t* inEnclaveReport,
                                                    ByteArray& outEnclaveQuote) {
            tcf::error::ThrowIfNull(
                inEnclaveReport,
                "Enclave report pointer is NULL");
            const uint8_t* pRevocationList = nullptr;
            if (this->signatureRevocationList.size()) {
                pRevocationList = reinterpret_cast<const uint8_t *>(
                    this->signatureRevocationList.c_str());
            }

            // Properly size the enclave quote buffer for the caller and zero
            // it out so we have predictable contents.
            outEnclaveQuote.resize(this->quoteSize);

            sgx_status_t sresult = tcf::sgx_util::CallSgx(
                    [this,
                     &inEnclaveReport,
                     pRevocationList,
                     &outEnclaveQuote] () {
                        return
                        sgx_get_quote(
                            inEnclaveReport,
                            SGX_LINKABLE_SIGNATURE,
                            &this->spid,
                            nullptr,
                            pRevocationList,
                            static_cast<uint32_t>(
                                this->signatureRevocationList.size()),
                            nullptr,
                            reinterpret_cast<sgx_quote_t *>(&outEnclaveQuote[0]),
                            static_cast<uint32_t>(outEnclaveQuote.size()));
                    });
            tcf::error::ThrowSgxError(
                sresult,
                "Failed to create linkable quote for enclave report");
        }  // EpidAttestation::CreateQuoteFromReport

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
	void EpidAttestation::GetEpidGroup(HexEncodedString& outEpidGroup) {
            sgx_status_t ret;
	    // Get the EPID group from the enclave and convert it to big endian
            // Retrieve epid by calling init quote
            ret = tcf::sgx_util::CallSgx([this] () {
                      return sgx_init_quote(&this->reportTargetInfo, &this->epidGroupId);
                  });

            tcf::error::ThrowSgxError(ret, "Failed to get epid group id from init_quote");
	    std::reverse((uint8_t*)&this->epidGroupId,
	        (uint8_t*)&this->epidGroupId+ sizeof(this->epidGroupId));

	    outEpidGroup = tcf::BinaryToHexString((const uint8_t*)&this->epidGroupId,
	        sizeof(this->epidGroupId));
        } // EpidAttestation::GetEpidGroup

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
	void EpidAttestation::SetSpid(const HexEncodedString& inSpid) {
            tcf::error::ThrowIf<tcf::error::ValueError>(
                inSpid.length() != 32,
                "Invalid SPID length");

            HexStringToBinary(this->spid.id, sizeof(this->spid.id), inSpid);
        } // EpidAttestation::SetSpid

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
	void EpidAttestation::SetSignatureRevocationList (const std::string& inSignatureRevocationList) {
            // Copy the signature revocation list to our internal cached
            // version and then retrieve the, potentially, new quote size
            // and cache that value.
            this->signatureRevocationList = inSignatureRevocationList;

            const uint8_t* pRevocationList = nullptr;
            uint32_t revocationListSize = this->signatureRevocationList.size();
            if (revocationListSize) {
                pRevocationList = reinterpret_cast<const uint8_t *>(
                        this->signatureRevocationList.c_str());
            }

            uint32_t size;
	    tcf::error::ThrowSgxError(sgx_calc_quote_size(pRevocationList, revocationListSize, &size));
            this->quoteSize = size;
        } // EpidAttestation::SetSignatureRevocationList
        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    }  /* namespace enclave_api */
}  // namespace tcf

