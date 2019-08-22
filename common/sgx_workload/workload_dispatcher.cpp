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
#include "work_order_data.h"
#include "workload_processor.h"
#include "echo/workload/echo.h"
#include "heart_disease_eval/workload/heart_disease_evaluation.h"

template<typename T> tcf::WorkOrderProcessorInterface* createInstance() {
    return new T;
}

WorkOrderDispatchTableEntry workOrderDispatchTable[] = {
    {"echo-result", &createInstance<EchoResult>},
    {"heart-disease-eval", &createInstance<HeartDiseaseEval>},
    {NULL, NULL}
};
