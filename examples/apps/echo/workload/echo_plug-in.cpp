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

#include "echo_plug-in.h"
#include "echo_logic.h"

REGISTER_WORKLOAD_PROCESSOR("echo-result",EchoResult)

EchoResult::EchoResult() {}

EchoResult::~EchoResult() {}

void EchoResult::ProcessWorkOrder(
        std::string workload_id,
        const ByteArray& requester_id,
        const ByteArray& worker_id,
        const ByteArray& work_order_id,
        const std::vector<tcf::WorkOrderData>& in_work_order_data,
        std::vector<tcf::WorkOrderData>& out_work_order_data) {
    std::string result_str;
    int i = 0;
    int out_wo_data_size = out_work_order_data.size();

    for (auto wo_data : in_work_order_data) {
        // Process the input data
        result_str = Process(
            ByteArrayToString(wo_data.decrypted_data));

        // If the out_work_order_data has entry to hold the data
        if (i < out_wo_data_size) {
            tcf::WorkOrderData& out_wo_data = out_work_order_data.at(i);
            out_wo_data.decrypted_data =
                ByteArray(result_str.begin(), result_str.end());
        } else {
            // Create a new entry
            out_work_order_data.emplace_back(
                wo_data.index, ByteArray(result_str.begin(), result_str.end()));
            }

        i++;
    }
}

