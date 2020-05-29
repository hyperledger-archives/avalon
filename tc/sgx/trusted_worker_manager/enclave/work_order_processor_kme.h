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

#pragma once

#include <string>
#include <vector>
#include "enclave_data.h"

#include "types.h"
#include "work_order_data_handler.h"
#include "work_order_processor.h"
#include "ext_work_order_info_kme.h"

namespace tcf {
    class WorkOrderProcessorKME : public WorkOrderProcessor {
    public:
        WorkOrderProcessorKME() {
            ext_work_order_data = "";
        }
        ~WorkOrderProcessorKME();

        std::string ext_work_order_data;
    private:
        void PopulateExtWorkOrderInfoData(std::string ext_wo_data,
            ExtWorkOrderInfoKME* ext_wo_info_kme);
        std::vector<tcf::WorkOrderData> ExecuteWorkOrder(
            EnclaveData* enclave_data) override;
    };  // WorkOrderProcessorKME
}  // namespace tcf

