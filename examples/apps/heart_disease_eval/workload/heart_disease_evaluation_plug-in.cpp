/* Copyright 2019 Intel Corporation
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

// This demo application predicts the probability of heart disease.

#include <string>
#include <memory>

#include "heart_disease_evaluation_plug-in.h"
#include "heart_disease_evaluation_logic.h"

REGISTER_WORKLOAD_PROCESSOR("heart-disease-eval",HeartDiseaseEval)

HeartDiseaseEval::HeartDiseaseEval() {}

HeartDiseaseEval::~HeartDiseaseEval() {}

void HeartDiseaseEval::ProcessWorkOrder(
        std::string workload_id,
        const ByteArray& requester_id,
        const ByteArray& worker_id,
        const ByteArray& work_order_id,
        const std::vector<tcf::WorkOrderData>& in_work_order_data,
        std::vector<tcf::WorkOrderData>& out_work_order_data) {
    std::string result_str;
    int out_wo_data_size = out_work_order_data.size();

    std::unique_ptr<HeartDiseaseEvalLogic> heart_disease_eval_logic(
            new HeartDiseaseEvalLogic());
    // Clear state - to reset totalRisk and count
    heart_disease_eval_logic->executeWorkOrder("");
    for (auto wo_data : in_work_order_data) {
        std::string inputData =
              ByteArrayToString(wo_data.decrypted_data);
        try {
            result_str = heart_disease_eval_logic->executeWorkOrder(inputData);
        } catch(...) {
            result_str = "Failed to process workorder data";
        }
    }

    // If the out_work_order_data has entry to hold the data
    if (out_wo_data_size) {
        tcf::WorkOrderData& out_wo_data = out_work_order_data.at(0);
        out_wo_data.decrypted_data =
                    ByteArray(result_str.begin(), result_str.end());
    } else {
        // Create a new entry
        out_work_order_data.emplace_back(
                    0, ByteArray(result_str.begin(), result_str.end()));
    }

}
