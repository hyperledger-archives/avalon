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


#include <map>
#include "kme_workload_plug-in.h"

REGISTER_WORKLOAD_PROCESSOR("kme",KEY_MANAGEMENT_ENCLAVE,KMEWorkloadProcessor);

/*
 *  Generates verification key, verification key signature and
 *  add them to output data.
 *
 *  @param in_work_order_data - vector of work order indata
 *  @param out_work_order_data - vector of work order outdata
 *  @param ext_wo_info_kme - Instance of KMEs extended work order implementation
*/
void KMEWorkloadProcessor::GetUniqueId(
    const std::vector<tcf::WorkOrderData>& in_work_order_data,
    std::vector<tcf::WorkOrderData>& out_work_order_data,
    ExtWorkOrderInfoKME* ext_wo_info_kme) {

    ByteArray signing_key = {};
    ByteArray verification_key_hex = {};
    ByteArray verification_key_signature_hex = {};
    ByteArray nonce_hex = in_work_order_data[0].decrypted_data;

    int err = ext_wo_info_kme->GenerateSigningKey(
        ExtWorkOrderInfo::KeyType_SECP256K1, nonce_hex, signing_key,
        verification_key_hex, verification_key_signature_hex);

    SetStatus(err, out_work_order_data);

    if (!err) {
        sig_key_map[verification_key_hex] = signing_key;
        AddOutput(1, verification_key_hex, out_work_order_data);
        AddOutput(2, verification_key_signature_hex, out_work_order_data);
    }
}  // KMEWorkloadProcessor::GetUniqueId

/* 
 *  Register WPE enclave with this instance of KME enclave.
 *
 *  @param in_work_order_data - vector of work order indata
 *  @param out_work_order_data - vector of work order outdata
 *  @param ext_wo_info_kme - Instance of KMEs extended work order implementation
*/
void KMEWorkloadProcessor::Register(
    const std::vector<tcf::WorkOrderData>& in_work_order_data,
    std::vector<tcf::WorkOrderData>& out_work_order_data,
    ExtWorkOrderInfoKME* ext_wo_info_kme) {

    // To be implemented
}  // KMEWorkloadProcessor::Register


/*
 *  Generate work order key data to be used by WPE for
 *  work order response signing and encryption.
 *
 *  @param in_work_order_data - vector of work order indata
 *  @param out_work_order_data - vector of work order outdata
 *  @param ext_wo_info_kme - Instance of KMEs extended work order implementation
*/
void KMEWorkloadProcessor::PreprocessWorkorder(
    const std::vector<tcf::WorkOrderData>& in_work_order_data,
    std::vector<tcf::WorkOrderData>& out_work_order_data,
    ExtWorkOrderInfoKME* ext_wo_info_kme) {

    // To be implemented
}  // KMEWorkloadProcessor::PreprocessWorkorder

/*
 *  Add output data after work order processing to out data vector.
 *
 *  @param index - index of the out data in the vector
 *  @param out_work_order_data - vector of work order outdata
*/
void KMEWorkloadProcessor::AddOutput(int index, ByteArray& data,
    std::vector<tcf::WorkOrderData>& out_work_order_data) {

    int out_wo_data_size = out_work_order_data.size();
    // If the out_work_order_data has entry to hold the data
    if (index < out_wo_data_size) {
        tcf::WorkOrderData out_wo_data = out_work_order_data.at(index);
        out_wo_data.decrypted_data = data;
    }
    else {
        // Create a new entry
        out_work_order_data.emplace_back(index, data);
    }
}  // KMEWorkloadProcessor::AddOutput

/*
 *  Set status of workload execution in work order out data.
 *
 *  @param result - Result of workload execution
 *  @param out_work_order_data - vector of work order outdata
*/
void KMEWorkloadProcessor::SetStatus(int result,
    std::vector<tcf::WorkOrderData>& out_work_order_data) {

    std::string result_str = std::to_string(result);
    ByteArray ba(result_str.begin(), result_str.end());
    AddOutput(0, ba, out_work_order_data);
}  // KMEWorkloadProcessor::SetStatus

/*
 *  Process work order request based on workload identifier
 *  and package the result in the work order out data.
 *
 *  @param workload_id         Workload identifier string
 *  @param requester_id        Requester ID to identify who submitted
 *                           the work order
 *  @param worker_id           Worker ID, a unique string identifying
 *                           this type of work order processor
 *  @param work_order_id       Unique work order ID for this type of
 *                           work order processor
 *  @param in_work_order_data  Work order data input submitted to the
 *                           work order processor
 *  @param out_work_order_data Work order data returned by the
 *                           work order processor
*/
void KMEWorkloadProcessor::ProcessWorkOrder(
    std::string workload_id,
    const ByteArray& requester_id,
    const ByteArray& worker_id,
    const ByteArray& work_order_id,
    const std::vector<tcf::WorkOrderData>& in_work_order_data,
    std::vector<tcf::WorkOrderData>& out_work_order_data) {

    ExtWorkOrderInfoKME* ext_wo_info_kme = \
        (ExtWorkOrderInfoKME*) ext_work_order_info;

    if (workload_id == "kme-uid") {
        GetUniqueId(in_work_order_data, out_work_order_data, ext_wo_info_kme);
    } else if (workload_id == "kme-reg") {
        Register(in_work_order_data, out_work_order_data, ext_wo_info_kme);
    } else {
        PreprocessWorkorder(in_work_order_data, out_work_order_data, ext_wo_info_kme);
    }
}  // KMEWorkloadProcessor::ProcessWorkOrder
