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

#include <string>
#include "work_order_data.h"
#include "work_order_processor_interface.h"

class EchoResult: public tcf::WorkOrderProcessorInterface {
private:
    std::string Process(std::string str_in);

public:
    EchoResult(void);
    virtual ~EchoResult(void);

    void ProcessWorkOrder(
                std::string workload_id,
                const ByteArray& participant_address,
                const ByteArray& enclave_id,
                const ByteArray& work_order_id,
                const std::vector<tcf::WorkOrderData>& in_work_order_data,
                std::vector<tcf::WorkOrderData>& out_work_order_data);
};

