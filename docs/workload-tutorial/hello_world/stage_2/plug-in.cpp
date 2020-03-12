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

#include <string>
#include "plug-in.h"
#include "logic.h"


REGISTER_WORKLOAD_PROCESSOR(workload_id, Workload)

void Workload::ProcessWorkOrder(
        std::string workload_id,
        const ByteArray& requester_id,
        const ByteArray& worker_id,
        const ByteArray& work_order_id,
        const std::vector<tcf::WorkOrderData>& in_work_order_data,
        std::vector<tcf::WorkOrderData>& out_work_order_data) {

    // For each work order, process the input data
    for (auto wo_data : in_work_order_data) {
        std::string result_str =
            ProcessHelloWorld(ByteArrayToString(wo_data.decrypted_data));

        ByteArray ba(result_str.begin(), result_str.end());
        AddOutput(wo_data.index, out_work_order_data, ba);
    }
}
