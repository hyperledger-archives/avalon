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

#pragma once

#include <string>
#include <stdlib.h>

#include "tcf_error.h"
#include "types.h"

class WorkOrderHandler {
public:
    WorkOrderHandler() {}

    tcf_err_t HandleWorkOrderRequest(
        const Base64EncodedString& inSerializedRequest,
        const std::string inWorkOrderExtData,
        uint32_t& outResponseIdentifier,
        size_t& outSerializedResponseSize,
        int enclaveIndex);

    tcf_err_t GetSerializedResponse(
        const uint32_t inResponseIdentifier,
        const size_t inSerializedResponseSize,
        Base64EncodedString& outSerializedResponse,
        int enclaveIndex);
};
