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
 * Defines base class WorkloadProcessor and other definitions to
 * create an Avalon workload processor.
 * To use, #include "workload_processor.h"
 */

#pragma once

#include <map>
#include <string>

#include "ext_work_order_info_kme.h"
#include "workload_processor.h"

/** Class to register, create, and process a kme workload. */
class WorkloadProcessorKME : public WorkloadProcessor {
public:
    WorkloadProcessorKME(void);
    virtual ~WorkloadProcessorKME(void);

    /**
     * Register a WorkloadProcessor.
     * Used by the workloads to register themselves
     *
     * @param workload_id Workload identifier
     * @returns           Pointer to WorkloadProcessorKME
     */
    static WorkloadProcessor* RegisterWorkloadProcessorKME(
        std::string workload_id, WorkloadProcessor* processor);

    /** Extended workorder info instance **/
    ExtWorkOrderInfoKME* ext_work_order_info_kme;

};

/**
 * This macro registers a kme workload processor.
 * It associates a string with a workload.
 * This is the same string that is passed in the work order request
 * JSON payload.
 * Example usage in a .cpp source file:
 * REGISTER_WORKLOAD_PROCESSOR_KME(workload_id_string, Workload)
 *
 * @param WORKLOADID_STR A string literal or variable identifying the workload
 *                       type
 * @param TYPE           Name of the Workload class
 */
#define REGISTER_WORKLOAD_PROCESSOR_KME(WORKLOADID_STR,TYPE) \
   WorkloadProcessor* TYPE##_myProcessor = \
      WorkloadProcessorKME::RegisterWorkloadProcessorKME(WORKLOADID_STR, new TYPE());
