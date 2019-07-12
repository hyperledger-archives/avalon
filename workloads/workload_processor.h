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

#include <map>
#include <string>
#include "work_order_processor_interface.h"

namespace tc = tcf;

typedef tc::WorkOrderProcessorInterface* (*work_order_factory)();

struct WorkOrderDispatchTableEntry {
    const char* project_name;
    work_order_factory work_order_factory_ptr;
};

class WorkloadProcessor : public tc::WorkOrderProcessorInterface {
private:
    // Convention: we use the key "IntrinsicState" key to store the value
    const std::string intrinsic_state_key_ = "IntrinsicState";
public:
    WorkloadProcessor(void);
    virtual ~WorkloadProcessor(void);

    virtual void ProcessWorkOrder(
                std::string code_id,
                const ByteArray& participant_address,
                const ByteArray& enclave_id,
                const ByteArray& work_order_id,
                const std::vector<tcf::WorkOrderData>& in_work_order_data,
                std::vector<tcf::WorkOrderData>& out_work_order_data);
};

