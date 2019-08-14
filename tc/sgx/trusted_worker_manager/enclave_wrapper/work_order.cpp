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

#include "enclave_u.h"

#include "tcf_error.h"
#include "error.h"
#include "log.h"
#include "types.h"
#include "zero.h"

#include "crypto.h"
#include "enclave.h"
#include "base.h"
#include "work_order.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t tcf::enclave_api::workorder::HandleWorkOrderRequest(
    const Base64EncodedString& inSealedEnclaveData,
    const Base64EncodedString& inSerializedRequest,
    uint32_t& outResponseIdentifier,
    size_t& outSerializedResponseSize,
    int enclaveIndex) {
    tcf_err_t result = TCF_SUCCESS;

    try {
        size_t response_size = 0;
        ByteArray sealed_enclave_data = Base64EncodedStringToByteArray(inSealedEnclaveData);
        ByteArray serialized_request = Base64EncodedStringToByteArray(inSerializedRequest);

        // xxxxx call the enclave

        /// get the enclave id for passing into the ecall
        sgx_enclave_id_t enclaveid = g_Enclave[enclaveIndex].GetEnclaveId();

        tcf_err_t presult = TCF_SUCCESS;
        sgx_status_t sresult =
            g_Enclave[enclaveIndex].CallSgx(
                [
                    enclaveid,
                    &presult,
                    sealed_enclave_data,
                    serialized_request,
                    &response_size
                ]
                () {
                    sgx_status_t sresult_inner = ecall_HandleWorkOrderRequest(
                        enclaveid,
                        &presult,
                        sealed_enclave_data.data(),
                        sealed_enclave_data.size(),
                        serialized_request.data(),
                        serialized_request.size(),
                        &response_size);
                    return tcf::error::ConvertErrorStatus(sresult_inner, presult);
                });
        tcf::error::ThrowSgxError(sresult, "SGX enclave call failed (InitializeContract)");
        g_Enclave[enclaveIndex].ThrowTCFError(presult);

        outSerializedResponseSize = response_size;

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
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t tcf::enclave_api::workorder::GetSerializedResponse(
    const Base64EncodedString& inSealedEnclaveData,
    const uint32_t inResponseIdentifier,
    const size_t inSerializedResponseSize,
    Base64EncodedString& outSerializedResponse,
    int enclaveIndex) {
    tcf_err_t result = TCF_SUCCESS;

    try {
        ByteArray serialized_response(inSerializedResponseSize);
        ByteArray sealed_enclave_data = Base64EncodedStringToByteArray(inSealedEnclaveData);

        // xxxxx call the enclave

        /// get the enclave id for passing into the ecall
        sgx_enclave_id_t enclaveid = g_Enclave[enclaveIndex].GetEnclaveId();
        // tcf::logger::LogV(TCF_LOG_DEBUG, "GetSerializedResponse[%ld] %u ", (long)enclaveid, enclaveIndex);

        tcf_err_t presult = TCF_SUCCESS;
        sgx_status_t sresult =

            g_Enclave[enclaveIndex].CallSgx(
                [
                    enclaveid,
                    &presult,
                    sealed_enclave_data,
                    &serialized_response
                ]
                () {
                    sgx_status_t sresult_inner = ecall_GetSerializedResponse(
                        enclaveid,
                        &presult,
                        sealed_enclave_data.data(),
                        sealed_enclave_data.size(),
                        serialized_response.data(),
                        serialized_response.size());
                    return tcf::error::ConvertErrorStatus(sresult_inner, presult);
                });
        tcf::error::ThrowSgxError(sresult, "SGX enclave call failed (GetSerializedResponse)");
        g_Enclave[enclaveIndex].ThrowTCFError(presult);

        outSerializedResponse = ByteArrayToBase64EncodedString(serialized_response);
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
}
