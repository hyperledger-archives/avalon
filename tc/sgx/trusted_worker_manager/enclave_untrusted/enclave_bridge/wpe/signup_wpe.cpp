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

#include "enclave_u.h"

#include "error.h"
#include "avalon_sgx_error.h"
#include "log.h"
#include "tcf_error.h"
#include "types.h"
#include "utils.h"

#include "enclave.h"
#include "base.h"
#include "signup_wpe.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t SignupDataWPE::GenerateNonce(
    std::string& out_nonce, size_t in_nonce_size) {

    tcf_err_t result = TCF_SUCCESS;
    try {
        tcf_err_t presult = TCF_SUCCESS;
        sgx_status_t sresult;

        // Get the enclave id for passing into the ecall
        sgx_enclave_id_t enclaveid = g_Enclave[0].GetEnclaveId();

        ByteArray nonce = {};
        // +1 for null character for std::string
        nonce.resize(in_nonce_size + 1);

        // Create nonce and convert to hex
        sresult = g_Enclave[0].CallSgx(
            [enclaveid,
                &presult,
                &nonce] () {
                sgx_status_t ret = ecall_GenerateNonce(
                    enclaveid,
                    &presult,
                    (uint8_t*) nonce.data(),
                    nonce.size());
                return tcf::error::ConvertErrorStatus(ret, presult);
            });
        tcf::error::ThrowSgxError(sresult,
            "SGX enclave call failed (ecall_GenerateNonce)");
        g_Enclave[0].ThrowTCFError(presult);

        out_nonce = ByteArrayToStr(nonce);
    } catch (tcf::error::Error& e) {
        tcf::enclave_api::base::SetLastError(e.what());
        result = e.error_code();
    } catch (std::exception& e) {
        tcf::enclave_api::base::SetLastError(e.what());
        result = TCF_ERR_UNKNOWN;
    } catch (...) {
        tcf::enclave_api::base::SetLastError(
            "Unexpected exception in GenerateNonce");
        result = TCF_ERR_UNKNOWN;
    }
    return result;
}  // SignupDataWPE::GenerateNonce

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t SignupDataWPE::CreateEnclaveData(
    const std::string& inExtData,
    const std::string& inExtDataSignature,
    const std::string& inKmeAttestation,
    StringArray& outPublicEnclaveData,
    Base64EncodedString& outEnclaveQuote) {
    tcf_err_t result = TCF_SUCCESS;

    try {
        tcf_err_t presult = TCF_SUCCESS;
        sgx_status_t sresult;

        // Get the enclave id for passing into the ecall
        sgx_enclave_id_t enclaveid = g_Enclave[0].GetEnclaveId();

        // +1 for null character which is not included in std::string length()
        outPublicEnclaveData.resize(
            SignupData::CalculatePublicEnclaveDataSize() + 1);
    
        // We need target info in order to create signup data report
        sgx_target_info_t target_info = { 0 };
        sgx_epid_group_id_t epidGroupId = { 0 };
        sresult =
            g_Enclave[0].CallSgx(
                [&target_info,
                 &epidGroupId] () {
                    return sgx_init_quote(&target_info, &epidGroupId);
                });
        tcf::error::ThrowSgxError(sresult,
            "Intel SGX enclave call failed (sgx_init_quote);"
            " failed to initialize the quote");

        // Properly size the sealed signup data buffer for the caller
        // and call into the enclave to create the signup data
        sgx_report_t enclave_report = { 0 };

	ByteArray ext_data_bytes = StrToByteArray(inExtData);
	ByteArray ext_data_sig_bytes = StrToByteArray(inExtDataSignature);
        sresult = g_Enclave[0].CallSgx(
            [enclaveid,
             &presult,
             target_info,
             ext_data_bytes,
             ext_data_sig_bytes,
             inKmeAttestation,
             &outPublicEnclaveData,
             &enclave_report ] () {
                sgx_status_t ret = ecall_CreateSignupDataWPE(
                    enclaveid,
                    &presult,
                    &target_info,
                    ext_data_bytes.data(),
                    ext_data_bytes.size(),
                    ext_data_sig_bytes.data(),
                    ext_data_sig_bytes.size(),
                    (const uint8_t*)inKmeAttestation.c_str(),
                    inKmeAttestation.length(),
                    outPublicEnclaveData.data(),
                    outPublicEnclaveData.size(),
                    &enclave_report);
                return tcf::error::ConvertErrorStatus(ret, presult);
            });
        tcf::error::ThrowSgxError(sresult,
            "Intel SGX enclave call failed (CreateEnclaveDataWPE);"
            " failed to create signup data");
        g_Enclave[0].ThrowTCFError(presult);

        // Take the report generated and create a quote for it, encode it
        size_t quote_size = tcf::enclave_api::base::GetEnclaveQuoteSize();
        ByteArray enclave_quote_buffer(quote_size);
        g_Enclave[0].CreateQuoteFromReport(&enclave_report, enclave_quote_buffer);
        outEnclaveQuote = ByteArrayToBase64EncodedString(enclave_quote_buffer);
    } catch (tcf::error::Error& e) {
        tcf::enclave_api::base::SetLastError(e.what());
        result = e.error_code();
    } catch (std::exception& e) {
        tcf::enclave_api::base::SetLastError(e.what());
        result = TCF_ERR_UNKNOWN;
    } catch (...) {
        tcf::enclave_api::base::SetLastError(
            "Unexpected exception in (CreateEnclaveDataWPE)");
        result = TCF_ERR_UNKNOWN;
    }

    return result;
}  // SignupDataWPE::CreateEnclaveData

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t SignupDataWPE::VerifyEnclaveInfo(
    const std::string& enclaveInfo,
    const std::string& mr_enclave,
    const std::string& ext_data) {
    tcf_err_t result = TCF_SUCCESS;
    try {
        // xxxxx call the enclave
        sgx_enclave_id_t enclaveid = g_Enclave[0].GetEnclaveId();
        tcf_err_t presult = TCF_SUCCESS;

	//ByteArray ext_data_bytes = StrToByteArray(ext_data);
        sgx_status_t sresult = g_Enclave[0].CallSgx(
            [ enclaveid,
              &presult,
              enclaveInfo,
              mr_enclave,
              ext_data ] () {
              sgx_status_t sresult =
              ecall_VerifyEnclaveInfoWPE(
                             enclaveid,
                             &presult,
                             enclaveInfo.c_str(),
                             mr_enclave.c_str(),
                             ext_data.c_str());
          return tcf::error::ConvertErrorStatus(sresult, presult);
    });

        tcf::error::ThrowSgxError(sresult,
            "Intel SGX enclave call failed (ecall_VerifyEnclaveInfoWPE)");
        g_Enclave[0].ThrowTCFError(presult);

    } catch (tcf::error::Error& e) {
        tcf::enclave_api::base::SetLastError(e.what());
        result = e.error_code();
    } catch (std::exception& e) {
        tcf::enclave_api::base::SetLastError(e.what());
        result = TCF_ERR_UNKNOWN;
    } catch (...) {
        tcf::enclave_api::base::SetLastError("Unexpected exception");
        result = TCF_ERR_UNKNOWN;
    }
    return result;
}  // SignupDataWPE::VerifyEnclaveInfo
