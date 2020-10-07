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

#include "sgx_uae_epid.h"

#include "singleton_enclave_u.h"

#include "error.h"
#include "avalon_sgx_error.h"
#include "log.h"
#include "tcf_error.h"

#include "enclave.h"
#include "base.h"
#include "signup_singleton.h"
#include "sgx_utility.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t SignupDataSingleton::CreateEnclaveData(
    StringArray& outPublicEnclaveData,
    Base64EncodedString& outSealedEnclaveData,
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
        ByteArray sealed_enclave_data_buffer(
            SignupData::CalculateSealedEnclaveDataSize());

        // We need target info in order to create signup data report
        sgx_target_info_t target_info = { 0 };
        sgx_epid_group_id_t epidGroupId = { 0 };
        sresult = tcf::sgx_util::CallSgx(
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

        sresult = tcf::sgx_util::CallSgx(
            [enclaveid,
             &presult,
             target_info,
             &outPublicEnclaveData,
             &sealed_enclave_data_buffer,
             &enclave_report ] () {
                sgx_status_t ret = ecall_CreateSignupData(
                    enclaveid,
                    &presult,
                    &target_info,
                    outPublicEnclaveData.data(),
                    outPublicEnclaveData.size(),
                    sealed_enclave_data_buffer.data(),
                    sealed_enclave_data_buffer.size(),
                    &enclave_report);
                return tcf::error::ConvertErrorStatus(ret, presult);
            });
        tcf::error::ThrowSgxError(sresult,
            "Intel SGX enclave call failed (ecall_CreateSignupData);"
            " failed to create signup data");
        g_Enclave[0].ThrowTCFError(presult);
        outSealedEnclaveData = \
            ByteArrayToBase64EncodedString(sealed_enclave_data_buffer);

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
            "Unexpected exception in (CreateEnclaveData)");
        result = TCF_ERR_UNKNOWN;
    }

    return result;
}  // SignupDataSingleton::CreateEnclaveData

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t SignupDataSingleton::UnsealEnclaveData(
    StringArray& outPublicEnclaveData) {
    tcf_err_t result = TCF_SUCCESS;

    try {
        SignupDataSingleton signup_data;
        outPublicEnclaveData.resize(
            signup_data.CalculatePublicEnclaveDataSize());

        // xxxxx call the enclave
        sgx_enclave_id_t enclaveid = g_Enclave[0].GetEnclaveId();

        tcf_err_t presult = TCF_SUCCESS;
        sgx_status_t sresult = tcf::sgx_util::CallSgx(
            [ enclaveid,
              &presult,
              &outPublicEnclaveData] () {
                sgx_status_t sresult =
                ecall_UnsealEnclaveData(
                    enclaveid,
                    &presult,
                    outPublicEnclaveData.data(),
                    outPublicEnclaveData.size());
                return tcf::error::ConvertErrorStatus(sresult, presult);
            });

        tcf::error::ThrowSgxError(sresult,
            "Intel SGX enclave call failed (ecall_UnsealSignupData)");
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
}  // SignupDataSingleton::UnsealSignupData

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t SignupDataSingleton::VerifyEnclaveInfo(
    const std::string& enclaveInfo,
    const std::string& mr_enclave) {
    tcf_err_t result = TCF_SUCCESS;
    try {
        // xxxxx call the enclave
        sgx_enclave_id_t enclaveid = g_Enclave[0].GetEnclaveId();
        tcf_err_t presult = TCF_SUCCESS;

        sgx_status_t sresult = tcf::sgx_util::CallSgx(
            [ enclaveid,
              &presult,
              enclaveInfo,
              mr_enclave ] () {
              sgx_status_t sresult =
              ecall_VerifyEnclaveInfo(
                             enclaveid,
                             &presult,
                             enclaveInfo.c_str(),
                             mr_enclave.c_str());
          return tcf::error::ConvertErrorStatus(sresult, presult);
    });

        tcf::error::ThrowSgxError(sresult,
            "Intel SGX enclave call failed (ecall_VerifyEnclaveInfo)");
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
}  // SignupDataSingleton::VerifyEnclaveInfo
