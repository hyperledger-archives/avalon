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

#include "singleton_enclave_t.h"

#include <string>

#include <sgx_trts.h>
#include<mbusafecrt.h>

#include "error.h"
#include "tcf_error.h"

#include "enclave_utils.h"
#include "base_enclave.h"
#include "enclave_data.h"
#include "work_order_processor.h"

ByteArray last_serialized_response;

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t ecall_HandleWorkOrderRequest(const uint8_t* inSerializedRequest,
    size_t inSerializedRequestSize,
    const uint8_t* inWorkOrderExtData,
    size_t inWorkOrderExtDataSize,
    size_t* outSerializedResponseSize) {
    tcf_err_t result = TCF_SUCCESS;

    try {
        tcf::error::ThrowIfNull(inSerializedRequest,
            "Serialized request pointer is NULL");
        tcf::error::ThrowIfNull(outSerializedResponseSize,
            "Response size pointer is NULL");
        tcf::error::ThrowIf<tcf::error::ValueError>(
            inWorkOrderExtData != nullptr,
            "Work order extended data should be NULL for singleton worker");
        tcf::error::ThrowIf<tcf::error::ValueError>(inWorkOrderExtDataSize != 0,
            "Work order extended data size should be 0 for singleton worker");

        // Unseal the enclave persistent data
        EnclaveData* enclaveData = EnclaveData::getInstance(); 

        ByteArray request(inSerializedRequest,
            inSerializedRequest + inSerializedRequestSize);

        tcf::WorkOrderProcessor wo_processor;

        // work order extended data will not be used in singleton worker,
        // hence store empty value
        wo_processor.ext_work_order_data = "";

        std::string wo_string(request.begin(), request.end());
        last_serialized_response = wo_processor.Process(enclaveData, wo_string);

        // Save the response and return the size of the buffer required for it
        (*outSerializedResponseSize) = last_serialized_response.size();
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
