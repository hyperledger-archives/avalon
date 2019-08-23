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

#include <string>
#include "workload_processor.h"
#include "enclave_utils.h"

std::map<std::string, WorkloadProcessor*> \
    WorkloadProcessor::workload_processor_table;

WorkloadProcessor::WorkloadProcessor() {}

WorkloadProcessor::~WorkloadProcessor() {}

WorkloadProcessor* WorkloadProcessor::RegisterWorkloadProcessor(
    std::string workload_id,
    WorkloadProcessor* processor)
{
   Log(TCF_LOG_INFO, "Register Workload Processor - %s",
    workload_id.c_str());
   workload_processor_table[workload_id] = processor;
   return processor;
}

WorkloadProcessor* WorkloadProcessor::CreateWorkloadProcessor(
    std::string workload_id)
{
   WorkloadProcessor* processor;

   // Search the workload processor type in the table
   auto itr = workload_processor_table.find(workload_id);
   if (itr == workload_processor_table.end()) {
       Log(TCF_LOG_ERROR, "Workload Processor not found in table");
       return nullptr;
   } else {
       processor = (*itr).second;
   }

   // Clone the workload processor and return it.
   if( processor == nullptr) {
       Log(TCF_LOG_ERROR,"Workload Processor found, but it's class is nullptr");
       return nullptr;
   } else {
       return processor->Clone();
   }
}

