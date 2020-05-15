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

#include <stdlib.h>
#include <string>

#include "types.h"
#include "workload_processor.h"
#include "ext_work_order_info_kme.h"

#define KME_WO_COUNT_UNLIMITTED   0
#define KME_MAX_WO_COUNT          KME_WO_COUNT_UNLIMITTED


class KMEWorkloadProcessor: public WorkloadProcessor {

public:
    // contains registered WPE info
    struct WPEInfo {
        // number of preprocessed workorders for this WPE
        uint64_t workorder_count;
        // private signing key associated with this WPE
        ByteArray signing_key;

        WPEInfo(ByteArray& _sk) {
            workorder_count = 0;
            signing_key = _sk;
        }
    };

    KMEWorkloadProcessor(uint64_t max_wo_count = KME_MAX_WO_COUNT) {
       max_wo_count_ = max_wo_count;
    }

    virtual ~KMEWorkloadProcessor(void) {}

    IMPL_WORKLOAD_PROCESSOR_CLONE(KMEWorkloadProcessor);

    void GetUniqueId(
        const std::vector<tcf::WorkOrderData>& in_work_order_data,
        std::vector<tcf::WorkOrderData>& out_work_order_data,
        ExtWorkOrderInfoKME* ext_wo_info_kme);

    void Register(
        const std::vector<tcf::WorkOrderData>& in_work_order_data,
        std::vector<tcf::WorkOrderData>& out_work_order_data,
        ExtWorkOrderInfoKME* ext_wo_info_kme);

    void PreprocessWorkorder(
        const std::vector<tcf::WorkOrderData>& in_work_order_data,
        std::vector<tcf::WorkOrderData>& out_work_order_data,
        ExtWorkOrderInfoKME* ext_wo_info_kme);

    void ProcessWorkOrder(
        std::string workload_id,
        const ByteArray& requester_id,
        const ByteArray& worker_id,
        const ByteArray& work_order_id,
        const std::vector<tcf::WorkOrderData>& in_work_order_data,
        std::vector<tcf::WorkOrderData>& out_work_order_data);

private:
    static void AddOutput(int index, ByteArray& data,
        std::vector<tcf::WorkOrderData>& out_work_order_data);

    static void SetStatus(int result,
        std::vector<tcf::WorkOrderData>& out_work_order_data);

    std::map<ByteArray, ByteArray> sig_key_map;
    std::map<ByteArray, WPEInfo> wpe_enc_key_map;

    uint64_t max_wo_count_;
};  // KMEWorkloadProcessor

