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
#include "work_order_data.h"

// Class to register, create and process the workload
class WorkloadProcessor {
public:
    WorkloadProcessor(void);
    virtual ~WorkloadProcessor(void);

    // Clone WorkloadProcessor
    virtual WorkloadProcessor* Clone() const = 0;

    /* Create WorkloadProcessor
    * Input parameters:
    *  - workload_id: workload identifier
    * Returns - Pointer to WorkloadProcessor
    */
    static WorkloadProcessor* CreateWorkloadProcessor(std::string workload_id);

    /* Register WorkloadProcessor. Used by the workloads to register themselves
    * Input parameters:
    *  - workload_id: workload identifier
    * Returns - Pointer to WorkloadProcessor
    */
    static WorkloadProcessor* RegisterWorkloadProcessor(std::string workload_id,
        WorkloadProcessor* processor);

    // Mapping between workload id and WorkloadProcessor
    static std::map<std::string, WorkloadProcessor*> workload_processor_table;

    // Process the workload
    virtual void ProcessWorkOrder(
                std::string workload_id,
                const ByteArray& requester_id,
                const ByteArray& worker_id,
                const ByteArray& work_order_id,
                const std::vector<tcf::WorkOrderData>& in_work_order_data,
                std::vector<tcf::WorkOrderData>& out_work_order_data) = 0;
};

#define IMPL_WORKLOAD_PROCESSOR_CLONE(TYPE) \
   WorkloadProcessor* Clone() const { return new TYPE(*this); }

#define REGISTER_WORKLOAD_PROCESSOR(WORKLOADID_STR,TYPE) \
   WorkloadProcessor* TYPE##_myProcessor = \
      WorkloadProcessor::RegisterWorkloadProcessor(WORKLOADID_STR, new TYPE());
