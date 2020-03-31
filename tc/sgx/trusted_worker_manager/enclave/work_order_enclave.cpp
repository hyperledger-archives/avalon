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

#include "enclave_t.h"

#include <string>
#include <vector>

#include <sgx_trts.h>
#include <sgx_tseal.h>
#include <sgx_utils.h>
#include "sgx_thread.h"
#include<mbusafecrt.h>

#include "error.h"
#include "packages/base64/base64.h"
#include "tcf_error.h"
#include "timer.h"
#include "types.h"
#include "zero.h"

#include "enclave_utils.h"

#include "base_enclave.h"
#include "work_order_enclave.h"
#include "enclave_data.h"
#include "signup_enclave.h"

#include "work_order_processor.h"

ByteArray last_result;

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t ecall_HandleWorkOrderRequest(const uint8_t* inSerializedRequest,
    size_t inSerializedRequestSize,
    size_t* outSerializedResponseSize) {
    tcf_err_t result = TCF_SUCCESS;

    try {
        tcf::error::ThrowIfNull(inSerializedRequest,
            "Serialized request pointer is NULL");
        tcf::error::ThrowIfNull(outSerializedResponseSize,
            "Response size pointer is NULL");

        // Unseal the enclave persistent data
        EnclaveData* enclaveData = EnclaveData::getInstance(); 

        ByteArray request(inSerializedRequest,
            inSerializedRequest + inSerializedRequestSize);

        tcf::WorkOrderProcessor wo_processor;
        std::string wo_string(request.begin(), request.end());
        last_result = wo_processor.Process(enclaveData, wo_string);

        // Save the response and return the size of the buffer required for it
        (*outSerializedResponseSize) = last_result.size();
    } catch (tcf::error::Error& e) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Error in worker enclave (ecall_HandleWorkOrderRequest): %04X -- %s",
            e.error_code(), e.what());
        ocall_SetErrorMessage(e.what());
        result = e.error_code();
    } catch (...) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Unknown error in worker enclave (ecall_HandleWorkOrderRequest)");
        result = TCF_ERR_UNKNOWN;
    }

    return result;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t ecall_GetSerializedResponse(uint8_t* outSerializedResponse,
    size_t inSerializedResponseSize) {
    tcf_err_t result = TCF_SUCCESS;

    try {
        tcf::error::ThrowIfNull(outSerializedResponse,
            "Serialized response pointer is NULL");
        tcf::error::ThrowIf<tcf::error::ValueError>(
            inSerializedResponseSize < last_result.size(),
            "Not enough space for the response");

        // Unseal the enclave persistent data
        EnclaveData* enclaveData = EnclaveData::getInstance();

        memcpy_s(outSerializedResponse, inSerializedResponseSize,
            last_result.data(), last_result.size());
    } catch (tcf::error::Error& e) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Error in worker enclave(ecall_GetSerializedResponse): %04X -- %s",
            e.error_code(), e.what());
        ocall_SetErrorMessage(e.what());
        result = e.error_code();
    } catch (...) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Unknown error in worker enclave (ecall_GetSerializedResponse)");
        result = TCF_ERR_UNKNOWN;
    }

    return result;
}

