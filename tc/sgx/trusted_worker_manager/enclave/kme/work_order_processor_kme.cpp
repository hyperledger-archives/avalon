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

#include <algorithm>
#include <vector>
#include <string>

#include "error.h"
#include "tcf_error.h"
#include "types.h"

#include "hex_string.h"
#include "utils.h"
#include "enclave_utils.h"

#include "work_order_processor_kme.h"
#include "workload_processor_kme.h"

namespace tcf {
    WorkOrderProcessorKME::~WorkOrderProcessorKME() {
        // Sanitize class members storing secrets
        worker_encryption_key.clear();
        session_key.clear();
    }

    /*
     * Populates keys from work order requests into ExtWorkOrderInfoKME
     * class members
     *
     * @param ext_wo_data - extended work order data which contains WPE's
     *                      public encryption key
     * @param ext_wo_info_kme - Instance of ExtWorkOrderInfoKME class
     */
    void WorkOrderProcessorKME::PopulateExtWorkOrderInfoData(
        std::string ext_wo_data, ExtWorkOrderInfoKME* ext_wo_info_kme) {

        // Create work order data vector having index and
        // decrypted work order keys
        std::vector<tcf::WorkOrderData> in_wo_keys;
        std::vector<tcf::WorkOrderData> out_wo_keys;
        for (auto d : this->data_items_in) {
            in_wo_keys.emplace_back(
                d.workorder_data.index, d.GetDataEncryptionKey());
        }

        for (auto d : this->data_items_out) {
            out_wo_keys.emplace_back(
                d.workorder_data.index, d.GetDataEncryptionKey());
        }

        // Initializing ExtWorkOrderInfo member variables
        // whose values to be used in pre-processing
        ext_wo_info_kme->SetExtWorkOrderData(ext_wo_data);
        ext_wo_info_kme->SetWorkOrderRequesterNonce(this->requester_nonce);
        ext_wo_info_kme->SetWorkOrderSymmetricKey(this->session_key);
        ext_wo_info_kme->SetWorkOrderInDataKeys(in_wo_keys);
        ext_wo_info_kme->SetWorkOrderOutDataKeys(out_wo_keys);
    }  // WorkOrderProcessorKME::PopulateExtWorkOrderInfoData

    /*
     * Execute KME specific work order requests
     *
     * @param enclave_data - Instance of EnclaveData
     */
    std::vector<tcf::WorkOrderData> WorkOrderProcessorKME::ExecuteWorkOrder(
        EnclaveData* enclave_data) {

        std::vector<tcf::WorkOrderData> in_wo_data;
        std::vector<tcf::WorkOrderData> out_wo_data;
        if (data_items_in.size() > 0) {
            for (auto d : data_items_in) {
                in_wo_data.emplace_back(d.workorder_data.index,
                                        d.workorder_data.decrypted_data);
            }

            for (auto d : data_items_out) {
                out_wo_data.emplace_back(d.workorder_data.index,
                                            d.workorder_data.decrypted_data);
            }

            // Convert workload_id from hex string to string
            ByteArray workload_bytes = HexStringToBinary(workload_id);
            std::string workload_type(workload_bytes.begin(), workload_bytes.end());
            WorkloadProcessorKME *processor;
            // Creating workload processor for "kme" workload type. The type of
            // workload is checked in kme_workload_plugin in case of KME and
            // processed accordingly.
            processor = dynamic_cast <WorkloadProcessorKME*>(
                WorkloadProcessor::CreateWorkloadProcessor("kme"));
            tcf::error::ThrowIf<tcf::error::WorkloadError>(
                (processor==nullptr) ||
                (processor->ext_work_order_info_kme==nullptr),
                "Failed to initialize KME workload");
            if (workload_type == "kme-preprocess") {
                // KME preprocess request will embed client's work order
                // request at index 0 and ext_work_order_data at index 1
                // of in-data. We need to parse client request
                // to fetch client specific keys which will be wrapped
                // during preprocess.
                std::string orig_wo_req = ByteArrayToStr(
                        data_items_in[0].workorder_data.decrypted_data);
                // ext_data at index 1 contains WPE encryption key
                std::string ext_data = ByteArrayToStr(
                    data_items_in[1].workorder_data.decrypted_data);
                WorkOrderProcessorKME kme_wo_proc;
                JsonValue wo_req_json_val = \
                    kme_wo_proc.ParseJsonInput(orig_wo_req);
                kme_wo_proc.DecryptWorkOrderKeys(enclave_data, wo_req_json_val);
                kme_wo_proc.PopulateExtWorkOrderInfoData(ext_data,
                    processor->ext_work_order_info_kme);
            }

            processor->ProcessWorkOrder(
                    workload_type,
                    StrToByteArray(requester_id),
                    StrToByteArray(worker_id),
                    StrToByteArray(work_order_id),
                    in_wo_data,
                    out_wo_data);
            return out_wo_data;
        }
        throw tcf::error::RuntimeError("Work order inData not found");
    }  // WorkOrderProcessorKME::ExecuteWorkOrder
}  // namespace tcf
