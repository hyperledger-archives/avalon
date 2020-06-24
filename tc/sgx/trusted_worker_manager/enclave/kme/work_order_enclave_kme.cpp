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

#include "kme_enclave_t.h"

#include <string>

#include <sgx_trts.h>
#include<mbusafecrt.h>

#include "error.h"
#include "tcf_error.h"
#include "utils.h"

#include "enclave_utils.h"
#include "base_enclave.h"
#include "enclave_data.h"
#include "work_order_processor_kme.h"

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

        // Unseal the enclave persistent data
        EnclaveData* enclaveData = EnclaveData::getInstance(); 

        ByteArray request(inSerializedRequest,
            inSerializedRequest + inSerializedRequestSize);

        // Create KME work order processor
        tcf::WorkOrderProcessorKME wo_processor;

        // Persist Extended work order data in WorkOrderProcessor instance.
	    // extended work order data contains WPE's public encryption key
        if (inWorkOrderExtDataSize > 0) {
            wo_processor.ext_work_order_data = \
                std::string((const char*) inWorkOrderExtData);
        }

        std::string wo_string(request.begin(), request.end());
        last_serialized_response = wo_processor.Process(
            enclaveData, wo_string);

        // Save the response and return the size of the buffer required for it
        (*outSerializedResponseSize) = last_serialized_response.size();

        // clear Extended work order data if present after processing work order
        if (inWorkOrderExtDataSize > 0) {
            wo_processor.ext_work_order_data.clear();
        }
    } catch (tcf::error::Error& e) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Error in KME(ecall_HandleWorkOrderRequest): %04X -- %s",
            e.error_code(), e.what());
        ocall_SetErrorMessage(e.what());
        result = e.error_code();
    } catch (...) {
        SAFE_LOG(TCF_LOG_ERROR,
            "Unknown error KME(ecall_HandleWorkOrderRequest)");
        result = TCF_ERR_UNKNOWN;
    }

    return result;
}  // ecall_HandleWorkOrderRequest
