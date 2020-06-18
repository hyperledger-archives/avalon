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

/**
 * @file
 * Implements base class WorkloadProcessorKME to create an
 * Avalon KME workload processor.
 */

#include <string>
#include "enclave_utils.h"
#include "workload_processor_kme.h"

WorkloadProcessorKME::WorkloadProcessorKME() {
    this->ext_work_order_info_kme = nullptr;
}

WorkloadProcessorKME::~WorkloadProcessorKME() {}

WorkloadProcessor* WorkloadProcessorKME::RegisterWorkloadProcessorKME(
    std::string workload_id, WorkloadProcessor* processor) {

    // Call base class register workload processor method
    processor = RegisterWorkloadProcessor(workload_id, processor);
    WorkloadProcessorKME* kme_processor = \
        dynamic_cast<WorkloadProcessorKME*>(processor);
    if (kme_processor == nullptr) {
        Log(TCF_LOG_INFO, "Invalid KME workload processor");
        return nullptr;
    }

    // Initialize kme extended work order info class
    kme_processor->ext_work_order_info_kme = new ExtWorkOrderInfoKME();
    return processor;
}  // WorkloadProcessorKME::RegisterWorkloadProcessorKME
