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

#include <stdio.h>
#include <string.h>
#include "tcf_error.h"

tcf_err_t CreateEnclaveData(uint8_t* persistedSealedEnclaveData=nullptr);

tcf_err_t ecall_CalculateSealedEnclaveDataSize(size_t* pSealedEnclaveDataSize);

tcf_err_t ecall_CalculatePublicEnclaveDataSize(size_t* pPublicEnclaveDataSize);

tcf_err_t ecall_UnsealEnclaveData(char* outPublicEnclaveData,
    size_t inAllocatedPublicEnclaveDataSize);
