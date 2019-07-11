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
#include "echo_work_order/echo_workorder.h"
#include "heart_disease_eval/heart_disease_evaluation.h"

ByteArray ConvertStringToByteArray(std::string s) {
    ByteArray ba(s.begin(), s.end());
    return ba;
}

class EchoResult: public tcf::WorkOrderProcessorInterface {
public:
        void ProcessWorkOrder(
                std::string code_id,
                const ByteArray& participant_address,
                const ByteArray& enclave_id,
                const ByteArray& work_order_id,
                const std::vector<tcf::WorkOrderData>& in_work_order_data,
                std::vector<tcf::WorkOrderData>& out_work_order_data) {
        std::string result_str;
        int i = 0;
        int out_wo_data_size = out_work_order_data.size();

        for (auto wo_data : in_work_order_data) {
            // Skip first work order data index since it is
            // the identifier for the workload
            if (i == 0) {
                i++;
                continue;
            }

            // Execute the input data
            EchoResultImpl echo_result_impl;
            result_str = echo_result_impl.Process(ByteArrayToString(wo_data.decrypted_data));

            // If the out_work_order_data has entry to hold the data
            if (i < out_wo_data_size) {
                tcf::WorkOrderData& out_wo_data = out_work_order_data.at(i);
                out_wo_data.decrypted_data = ConvertStringToByteArray(result_str);
            } else {
                // Create a new entry
                out_work_order_data.emplace_back(wo_data.index, ConvertStringToByteArray(result_str));
            }

            i++;
        }
    };
} echo_result;


class HeartDiseaseEvalFactory: public tcf::WorkOrderProcessorInterface {
public:
        void ProcessWorkOrder(
                std::string code_id,
                const ByteArray& participant_address,
                const ByteArray& enclave_id,
                const ByteArray& work_order_id,
                const std::vector<tcf::WorkOrderData>& in_work_order_data,
                std::vector<tcf::WorkOrderData>& out_work_order_data) {
            std::string result_str;
            int out_wo_data_size = out_work_order_data.size();

            // Clear state - to reset totalRisk and count
            executeWorkOrder("");
            for (auto wo_data : in_work_order_data) {
                std::string inputData = ByteArrayToString(wo_data.decrypted_data);
                try {
                    result_str = executeWorkOrder(inputData);
                } catch(...) {
                    // Temp Implementation
                    result_str = "Failed to process workorder data";
                }
            }

            // If the out_work_order_data has entry to hold the data
            if (out_wo_data_size) {
                tcf::WorkOrderData& out_wo_data = out_work_order_data.at(0);
                out_wo_data.decrypted_data = ConvertStringToByteArray(result_str);
            } else {
                // Create a new entry
                out_work_order_data.emplace_back(0, ConvertStringToByteArray(result_str));
            }

      }
} heart_disease_eval_worker;

tcf::WorkOrderProcessorInterface* EchoResultFactory() {
        return &echo_result;
}

tcf::WorkOrderProcessorInterface* HeartDiseaseEvalFactory() {
        return &heart_disease_eval_worker;
}

WorkOrderDispatchTableEntry workOrderDispatchTable[] = {
    { "echo-result:", EchoResultFactory},
    { "heart-disease-eval:", HeartDiseaseEvalFactory },
    {NULL, NULL}
};
