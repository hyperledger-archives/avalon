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

/**
 * @file
 * Defines base class WorkloadProcessor and other definitions to
 * create an Avalon workload processor.
 * To use, #include "workload_processor.h"
 */

#pragma once

#include <map>
#include <string>
#include "work_order_data.h"

/** Class to register, create, and process a workload. */
class WorkloadProcessor {
public:
    WorkloadProcessor(void);
    virtual ~WorkloadProcessor(void);

    /** Clone a WorkloadProcessor */
    virtual WorkloadProcessor* Clone() const = 0;

    /**
     * Create a WorkloadProcessor
     *
     * @param workload_id Workload identifier
     * @returns           Pointer to WorkloadProcessor
     */
    static WorkloadProcessor* CreateWorkloadProcessor(std::string workload_id);

    /**
     * Register a WorkloadProcessor.
     * Used by the workloads to register themselves
     *
     * @param workload_id Workload identifier
     * @returns           Pointer to WorkloadProcessor
     */
    static WorkloadProcessor* RegisterWorkloadProcessor(std::string workload_id,
        WorkloadProcessor* processor);

    /** Mapping between workload id and WorkloadProcessor. */
    static std::map<std::string, WorkloadProcessor*> workload_processor_table;

    /**
     * Process the workload.
     *
     * @param workload_id         Workload identifier string
     * @param requester_id        Requester ID to identify who submitted
     *                            work order
     * @param worker_id           Worker ID, a unique string identifying
     *                            this type of work order processor
     * @param work_order_id       Unique work order ID for this type of
     *                            work order processor
     * @param in_work_order_data  Work order data input submitted to the
     *                            work order processor
     * @param out_work_order_data Work order data returned by the
     *                            work order processor
     */

    virtual void ProcessWorkOrder(
        std::string workload_id,
        const ByteArray& requester_id,
        const ByteArray& worker_id,
        const ByteArray& work_order_id,
        const std::vector<tcf::WorkOrderData>& in_work_order_data,
        std::vector<tcf::WorkOrderData>& out_work_order_data) = 0;
};

/**
 * This macro clones an instance of class WorkloadProcessor
 * for an Avalon worker.
 * Example usage in a .h header file:
 * IMPL_WORKLOAD_PROCESSOR_CLONE(Workload)
 *
 * @param TYPE           Name of the Workload class
 */
#define IMPL_WORKLOAD_PROCESSOR_CLONE(TYPE) \
   WorkloadProcessor* Clone() const { return new TYPE(*this); }

/**
 * This macro registers a workload processor for a specific application.
 * It associates a string with a workload.
 * This is the same string that is passed in the work order request
 * JSON payload.
 * Example usage in a .cpp source file:
 * REGISTER_WORKLOAD_PROCESSOR(workload_id_string, Workload)
 *
 * @param WORKLOADID_STR A string literal or variable identifying the workload
 *                       type
 * @param TYPE           Name of the Workload class
 */
#define REGISTER_WORKLOAD_PROCESSOR(WORKLOADID_STR,TYPE) \
   WorkloadProcessor* TYPE##_myProcessor = \
      WorkloadProcessor::RegisterWorkloadProcessor(WORKLOADID_STR, new TYPE());
