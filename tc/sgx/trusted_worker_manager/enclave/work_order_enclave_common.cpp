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

#include "enclave_common_t.h"

#include <sgx_trts.h>
#include<mbusafecrt.h>

#include "error.h"
#include "tcf_error.h"
#include "types.h"
#include "enclave_utils.h"

// global variable to store last serialized response. Initialized when
// work order is successfully processed in ecall_HandleWorkOrderRequest
extern ByteArray last_serialized_response;

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t ecall_GetSerializedResponse(uint8_t* outSerializedResponse,
    size_t inSerializedResponseSize) {

    tcf_err_t result = TCF_SUCCESS;
    try {
        tcf::error::ThrowIfNull(outSerializedResponse,
            "Serialized response pointer is NULL");
        tcf::error::ThrowIf<tcf::error::ValueError>(
            inSerializedResponseSize < last_serialized_response.size(),
            "Not enough space for the response");

        memcpy_s(outSerializedResponse, inSerializedResponseSize,
            last_serialized_response.data(),
            last_serialized_response.size());
    } catch (tcf::error::Error& e) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Error in enclave(ecall_GetSerializedResponse): %04X -- %s",
            e.error_code(), e.what());
        ocall_SetErrorMessage(e.what());
        result = e.error_code();
    } catch (...) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Unknown error in enclave(ecall_GetSerializedResponse)");
        result = TCF_ERR_UNKNOWN;
    }

    return result;
}  // ecall_GetSerializedResponse
