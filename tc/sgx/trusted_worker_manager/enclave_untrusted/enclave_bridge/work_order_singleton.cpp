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

#include "avalon_sgx_error.h"
#include "log.h"
#include "types.h"

#include "enclave.h"
#include "base.h"
#include "work_order_singleton.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t WorkOrderHandlerSingleton::HandleWorkOrderRequest(
    const Base64EncodedString& inSerializedRequest,
    uint32_t& outResponseIdentifier,
    size_t& outSerializedResponseSize,
    int enclaveIndex) {
    tcf_err_t result = TCF_SUCCESS;

    try {
        size_t response_size = 0;
        ByteArray serialized_request = \
            Base64EncodedStringToByteArray(inSerializedRequest);

        // xxxxx Call the enclave

        // Get the enclave id for passing into the ecall
        sgx_enclave_id_t enclaveid = g_Enclave[enclaveIndex].GetEnclaveId();

        tcf_err_t presult = TCF_SUCCESS;
        sgx_status_t sresult =
            g_Enclave[enclaveIndex].CallSgx(
                [
                    enclaveid,
                    &presult,
                    serialized_request,
                    &response_size
                ]
                () {
                    sgx_status_t sresult_inner = ecall_HandleWorkOrderRequest(
                        enclaveid,
                        &presult,
                        serialized_request.data(),
                        serialized_request.size(),
                        &response_size);
                    return tcf::error::ConvertErrorStatus(sresult_inner, presult);
                });
        tcf::error::ThrowSgxError(sresult,
            "Intel SGX enclave call failed (ecall_HandleWorkOrderRequest)");
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
}  // 
