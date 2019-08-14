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

/***************************************************************************************************
FILENAME:      workorder_enclave.h
DESCRIPTION:   Function declarations for the workorder enclave
*******************************************************************************************************/

#pragma once

#include "error.h"
#include "sgx_thread.h"
#include "enclave_utils.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
extern tcf_err_t ecall_HandleWorkOrderRequest(const uint8_t* inSealedSignupData,
    size_t inSealedSignupDataSize,
    const uint8_t* inSerializedRequest,
    size_t inSerializedRequestSize,
    size_t* outSerializedResponseSize);

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
extern tcf_err_t ecall_GetSerializedResponse(const uint8_t* inSealedSignupData,
    size_t inSealedSignupDataSize,
    char* outSerializedResponse,
    size_t inSerializedResponseSize);
