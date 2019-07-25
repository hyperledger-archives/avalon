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

#include "workload_processor.h"
#include "workload_dispatcher.cpp"
#include <iostream>
#include <string>

tc::WorkOrderProcessorInterface* LookUpWorkOrder(std::string work_order_code) {
    for (int i = 0; workOrderDispatchTable[i].project_name != NULL; i++) {
        if (work_order_code.compare(workOrderDispatchTable[i].project_name) == 0) {
            return workOrderDispatchTable[i].work_order_factory_ptr();
        }
    }
    tcf::error::RuntimeError("Work order not found in Work order lookup table\n");
    return NULL;
}

WorkloadProcessor::WorkloadProcessor() {}

WorkloadProcessor::~WorkloadProcessor() {}

void WorkloadProcessor::ProcessWorkOrder(
        std::string code_id,
        const ByteArray& participant_address,
        const ByteArray& enclave_id,
        const ByteArray& work_order_id,
        const std::vector<tcf::WorkOrderData>& in_work_order_data,
        std::vector<tcf::WorkOrderData>& out_work_order_data) {
    tcf::WorkOrderProcessorInterface* work_order = LookUpWorkOrder(code_id);
    if (work_order == nullptr) {
	tcf::error::RuntimeError("Work order not found in Work order lookup table\n");
	return;
    }
    work_order->ProcessWorkOrder(
                code_id,
                participant_address,
                enclave_id,
                work_order_id,
                in_work_order_data,
                out_work_order_data);
}
