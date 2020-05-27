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

#include "kme_workload_plug-in.h"
#include "enclave_data.h"
#include "error.h"
#include "parson.h"
#include "jsonvalue.h"
#include "utils.h"
#include "signup_enclave_util.h"

using namespace tcf::error;

REGISTER_WORKLOAD_PROCESSOR("kme",KEY_MANAGEMENT_ENCLAVE,KMEWorkloadProcessor);

/*
 *  Generates verification key, verification key signature and
 *  add them to output data.
 *
 *  @param in_work_order_data - vector of work order indata
 *  @param out_work_order_data - vector of work order outdata
 *  @param ext_wo_info_kme - Instance of KMEs extended work order implementation
*/

WPEInfo::WPEInfo() {
    workorder_count = 0;
    signing_key = {};
}

WPEInfo::WPEInfo(const ByteArray& _sk) {
    workorder_count = 0;
    signing_key = _sk;
}

void KMEWorkloadProcessor::GetUniqueId(
    const std::vector<tcf::WorkOrderData>& in_work_order_data,
    std::vector<tcf::WorkOrderData>& out_work_order_data) {
    ByteArray signing_key = {};
    ByteArray verification_key_hex = {};
    ByteArray verification_key_signature_hex = {};
    ByteArray nonce_hex = in_work_order_data[0].decrypted_data;

    int err = ext_wo_info_kme->GenerateSigningKey(
        ExtWorkOrderInfo::KeyType_SECP256K1, nonce_hex, signing_key,
        verification_key_hex, verification_key_signature_hex);

    this->SetStatus(err, out_work_order_data);

    if (!err) {
        /* Compute hash of verification key and use it as key.
        WPE attestation report contains hash value of this key
        and same report is verified during registration. */
        std::string v_key_str = ByteArrayToString(verification_key_hex);
        uint8_t v_key_hash[SGX_HASH_SIZE] = {0};
        ComputeSHA256Hash(v_key_str, v_key_hash);
        ByteArray v_key_bytes(std::begin(v_key_hash), std::end(v_key_hash));
        this->sig_key_map[v_key_bytes] = signing_key;
        this->AddOutput(1, verification_key_hex, out_work_order_data);
        this->AddOutput(2, verification_key_signature_hex,
            out_work_order_data);
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
    std::vector<tcf::WorkOrderData>& out_work_order_data) {
    // If in_work_order_data is empty
    if (in_work_order_data.size() == 0) {
        this->SetStatus((int)ERR_WPE_REG_FAILED,
            out_work_order_data);
        ThrowIf<ValueError>(true, "Registration request is empty");
    }
    /* Registration request is serialized json string
      {
       "attestation_data": <attestation_report>
      }
    */
    ByteArray reg_request = in_work_order_data[0].decrypted_data;

    std::string reg_data_string = ByteArrayToString(reg_request);
    /// Parse the registration request
    JsonValue reg_data_string_parsed(json_parse_string(
        reg_data_string.c_str()));
    if (reg_data_string_parsed.value == nullptr) {
        this->SetStatus((int)ERR_WPE_REG_FAILED,
            out_work_order_data);
        ThrowIf<ValueError>(true,
            "Failed to parse the WPE registration request");
    }
    JSON_Object* reg_data_json_object = \
        json_value_get_object(reg_data_string_parsed);
    if (reg_data_json_object == nullptr) {
        this->SetStatus((int)ERR_WPE_REG_FAILED,
            out_work_order_data);
        ThrowIf<ValueError>(true,
            "Invalid registration request, expecting valid json object");
    }

    const char* s_value = nullptr;
    
    s_value = json_object_dotget_string(
        reg_data_json_object, "attestation_data");
    if (s_value == nullptr) {
        this->SetStatus((int)ERR_WPE_REG_FAILED,
            out_work_order_data);
        ThrowIf<ValueError>(true, "Invalid attestation data");
    }

    std::string attestation_data_str(s_value);
    ByteArray attestation_data(attestation_data_str.begin(),
        attestation_data_str.end());

    ByteArray e_key = {};
    ByteArray verification_key_hash = {};
    ByteArray mr_enclave = {};
    ByteArray mr_signer = {};
    int err = this->ext_wo_info_kme->VerifyAttestation(
        attestation_data, mr_enclave, mr_signer,
        verification_key_hash, e_key);
    if (err != 0) {
        this->SetStatus(err, out_work_order_data);
        ThrowIf<ValueError>(true, "WPE attestation verification failed");
    }
    auto search = this->sig_key_map.find(verification_key_hash);
    if (search != this->sig_key_map.end()) {
        /// Compare MRENCLAVE value
        EnclaveData* enclaveData = EnclaveData::getInstance();
        std::string ext_data(enclaveData->get_extended_data());
        std::string mr_enclave_str = ByteArrayToString(mr_enclave);
        if (ext_data.compare(mr_enclave_str) != 0) {
            this->SetStatus((int)ERR_MRENCLAVE_NOT_MATCH,
                out_work_order_data);
            ThrowIf<ValueError>(true, "WPE MRENCLAVE value didn't match");
        }
        // TODO: MRSIGNER value check

        /// Add the WPE to the sig_key_map
        this->wpe_enc_key_map[e_key] = WPEInfo(
            this->sig_key_map[verification_key_hash]);

        /// Remove the entry to avoid replace attack
        this->sig_key_map.erase(verification_key_hash);
    }
    else {
        this->SetStatus((int)ERR_WPE_NOT_FOUND,
            out_work_order_data);
        ThrowIf<ValueError>(true, "WPE verification key not found");
    }
    this->SetStatus((int)ERR_WPE_REG_SUCCESS,
        out_work_order_data);
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
    std::vector<tcf::WorkOrderData>& out_work_order_data) {

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
void KMEWorkloadProcessor::SetStatus(const int result,
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

    if (workload_id == "kme-uid") {
        GetUniqueId(in_work_order_data, out_work_order_data);
    } else if (workload_id == "kme-reg") {
        Register(in_work_order_data, out_work_order_data);
    } else {
        PreprocessWorkorder(in_work_order_data, out_work_order_data);
    }
}  // KMEWorkloadProcessor::ProcessWorkOrder
