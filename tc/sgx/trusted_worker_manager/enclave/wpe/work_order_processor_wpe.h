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

#pragma once

#include <string>
#include <vector>
#include "enclave_data.h"

#include "parson.h"
#include "types.h"
#include "work_order_data_handler_wpe.h"
#include "work_order_processor.h"
#include "work_order_preprocessed_keys_wpe.h"

namespace tcf {
    class WorkOrderProcessorWPE : public WorkOrderProcessor{
    public:
        WorkOrderProcessorWPE() {
            ext_work_order_data = "";
        }
        ~WorkOrderProcessorWPE();
        std::string ext_work_order_data;
    private:
        WorkOrderPreProcessedKeys wo_pre_proc_keys;

        void DecryptWorkOrderKeys(EnclaveData* enclave_data,
            const JsonValue& wo_req_json_val) override;
        JsonValue CreateJsonOutput() override;
        void ComputeSignature(ByteArray& message_hash) override;
    };  // WorkOrderProcessorWPE
}  // namespace tcf

