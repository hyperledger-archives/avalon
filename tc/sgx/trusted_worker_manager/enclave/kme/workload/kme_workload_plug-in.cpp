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

#include "utils.h"
#include "kme_workload_plug-in.h"
#include "enclave_data.h"
#include "error.h"
#include "parson.h"
#include "jsonvalue.h"
#include "json_utils.h"
#include "signup_enclave_util.h"
#include "enclave_utils.h"

using namespace tcf::error;

REGISTER_WORKLOAD_PROCESSOR_KME("kme",KMEWorkloadProcessor);


/*
 *  Generates verification key, verification key signature and
 *  add them to output data.
 *
 *  @param in_work_order_data - vector of work order indata
 *  @param out_work_order_data - vector of work order outdata
 *  @param ext_wo_info_kme - Instance of KMEs extended work order implementation
*/

/* Map of key: Hex of public verification key or unique ID
 * value: private key corresponding to unique ID or verification key */
std::map<ByteArray, ByteArray> KMEWorkloadProcessor::sig_key_map;
/* Map of key: WPE encryption public key and value: private
 * key of unique ID verification key
 */
std::map<ByteArray, WPEInfo> KMEWorkloadProcessor::wpe_enc_key_map;

WPEInfo::WPEInfo() {
    workorder_count = 0;
    signing_key = {};
}

WPEInfo::WPEInfo(const ByteArray& _sk) {
    workorder_count = 0;
    /* signing key corresponds to the private key of
     * unique ID verification key */
    signing_key = _sk;
}

void KMEWorkloadProcessor::GetUniqueId(
    const std::vector<tcf::WorkOrderData>& in_work_order_data,
    std::vector<tcf::WorkOrderData>& out_work_order_data) {

    ByteArray signing_key = {};
    ByteArray verification_key_hex = {};
    ByteArray verification_key_signature_hex = {};
    ByteArray nonce_hex = in_work_order_data[0].decrypted_data;

    tcf::error::ThrowIf<tcf::error::WorkloadError>(
        (this->ext_work_order_info_kme == nullptr),
        "ExtWorkOrderInfoKME instance is not initialized");

    int err = ext_work_order_info_kme->GenerateSigningKey(
        ExtWorkOrderInfo::KeyType_SECP256K1, nonce_hex, signing_key,
        verification_key_hex, verification_key_signature_hex);

    if (!err) {
        sig_key_map[verification_key_hex] = signing_key;

        std::string result_str = std::to_string(err);
        // Concatenate status, verification_key and verification_key_signature
        // delimited by " "
        ByteArray out_data_bytes = StrToByteArray( result_str
                                   + " "
                                   + ByteArrayToStr(verification_key_hex)
                                   + " "
                                   + ByteArrayToStr(verification_key_signature_hex));

        AddOutput(0, out_data_bytes, out_work_order_data);
    }
}  // KMEWorkloadProcessor::GetUniqueId

/* 
 *  Register WPE enclave with this instance of KME enclave.
 *
 *  @param in_work_order_data - vector of work order indata
 *  @param out_work_order_data - vector of work order outdata
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
    /* Registration request is serialized json rpc string
     * with params
      {
       "unique_id": <unique_id>,
       "proof_data": <proof_data>,
       "wpe_encryption_key": <wpe_encryption_key>,
       "mr_enclave": <mr_enclave>
      }
    */
    // Parse the work order request
    ByteArray reg_request = in_work_order_data[0].decrypted_data;
    std::string reg_request_string = ByteArrayToStr(reg_request);
    JsonValue parsed(json_parse_string(reg_request_string.c_str()));
    tcf::error::ThrowIfNull(
        parsed.value,
	"failed to parse the registration request, badly formed JSON");

    JSON_Object* request_object = json_value_get_object(parsed);
    tcf::error::ThrowIfNull(request_object,
	"Missing JSON object in registration request");

    /* Get unique_id from params */
    const char* s_value = nullptr;
    s_value = json_object_dotget_string(request_object, "unique_id");
    if (s_value == nullptr) {
        this->SetStatus((int)ERR_WPE_REG_FAILED,
            out_work_order_data);
        ThrowIf<ValueError>(true,
                        "Extracting unique_id from params failed");
    }
    std::string unique_id(s_value);

    /* Get attestation_data from params */
    s_value = json_object_dotget_string(request_object, "proof_data");
    if (s_value == nullptr) {
        this->SetStatus((int)ERR_WPE_REG_FAILED,
            out_work_order_data);
        ThrowIf<ValueError>(true,
                        "Extracting proof_data from params failed");
    }
    std::string proof_data(s_value);

    /* Get wpe_encryption_key from params */
    s_value = json_object_dotget_string(request_object, "wpe_encryption_key");
    if (s_value == nullptr) {
        this->SetStatus((int)ERR_WPE_REG_FAILED,
            out_work_order_data);
        ThrowIf<ValueError>(true,
                        "Extracting wpe_encryption_key from params failed");
    }
    std::string wpe_encryption_key(s_value);

    /* Get mr_enclave from params */
    s_value = json_object_dotget_string(request_object, "mr_enclave");
    if (s_value == nullptr) {
        this->SetStatus((int)ERR_WPE_REG_FAILED,
            out_work_order_data);
        ThrowIf<ValueError>(true,
                        "Extracting mr_enclave from params failed");
    }
    std::string mr_enclave(s_value);
 
    ByteArray unique_id_bytes = StrToByteArray(unique_id);
    ByteArray e_key = {};
    ByteArray verification_key_hash = {};
    ByteArray mr_enclave_bytes = {};
    ByteArray mr_signer = {};

    tcf::error::ThrowIf<tcf::error::WorkloadError>(
        (this->ext_work_order_info_kme == nullptr),
        "ExtWorkOrderInfoKME instance is not initialized");

    // Not simulator mode
    if (!this->isSgxSimulator()) {
        int err = ext_work_order_info_kme->VerifyAttestationWpe(
	    StrToByteArray(proof_data),
            unique_id_bytes,
            mr_enclave_bytes, mr_signer,
            e_key, verification_key_hash);
        if (err != 0) {
            this->SetStatus(err, out_work_order_data);
            ThrowIf<ValueError>(true, "WPE attestation verification failed");
        }
    }
    auto search = sig_key_map.find(unique_id_bytes);

    if (search != sig_key_map.end()) {

        // If this is simulator mode, mr_enclave_bytes should not be
        // populated yet. Read the mr_enclave received as a parameter
        // in this WPE registration request and populate it.
        if (this->isSgxSimulator())
            mr_enclave_bytes = HexEncodedStringToByteArray(mr_enclave);

        // Compare MRENCLAVE value
        EnclaveData* enclaveData = EnclaveData::getInstance();
        ByteArray ext_data = enclaveData->get_extended_data();
        if (memcmp(ext_data.data(),
		        mr_enclave_bytes.data(), SGX_HASH_SIZE) != 0) {
            this->SetStatus((int)ERR_MRENCLAVE_NOT_MATCH, out_work_order_data);
            ThrowIf<ValueError>(true, "WPE MRENCLAVE value didn't match");
        }

        if (this->isSgxSimulator()) {
            /// Add the WPE to the sig_key_map
            wpe_enc_key_map[StrToByteArray(wpe_encryption_key)] = WPEInfo(
                sig_key_map[unique_id_bytes]);

            /// Remove the entry to avoid replay attack
            sig_key_map.erase(unique_id_bytes);
            this->SetStatus((int)ERR_WPE_REG_SUCCESS,
                out_work_order_data);
            return;
        }

        // Verify the hash of verification key in the report data and
        // unique_id in in_data
        uint8_t unique_id_hash[SGX_HASH_SIZE] = {0};
        ComputeSHA256Hash(unique_id.c_str(), unique_id_hash);
        if (verification_key_hash != ByteArray(std::begin(unique_id_hash),
                                               std::end(unique_id_hash))){

            this->SetStatus((int)ERR_UNIQUE_ID_NOT_MATCH, out_work_order_data);
            ThrowIf<ValueError>(true, "Unique id value didn't match");
        }

        // Compare if SHA256(wpe_encryption_key) matches
        // with WPE report data [0:31]
        uint8_t encryption_key_hash[SGX_HASH_SIZE] = {0};
        ComputeSHA256Hash(wpe_encryption_key.c_str(), encryption_key_hash);
        if (memcmp(e_key.data(), encryption_key_hash,
                SGX_HASH_SIZE) != 0) {
            this->SetStatus((int)ERR_ENCRYPTION_KEY_NOT_MATCH,
                out_work_order_data);
            ThrowIf<ValueError>(true, "Encryption key hash didn't match");
        }
        // TODO: MRSIGNER value check

        /// Add the WPE to the sig_key_map
        wpe_enc_key_map[StrToByteArray(wpe_encryption_key)] = WPEInfo(
            sig_key_map[unique_id_bytes]);

        /// Remove the entry to avoid replay attack
        sig_key_map.erase(unique_id_bytes);
    }
    else {
        this->SetStatus((int)ERR_WPE_KEY_NOT_FOUND, out_work_order_data);
        ThrowIf<ValueError>(true, "WPE verification key not found");
    }
    this->SetStatus((int)ERR_WPE_REG_SUCCESS, out_work_order_data);
}  // KMEWorkloadProcessor::Register


/*
 *  Generate work order key data to be used by WPE for
 *  work order response signing and encryption.
 *
 *  @param in_work_order_data - vector of work order indata
 *  @param out_work_order_data - vector of work order outdata
*/
void KMEWorkloadProcessor::PreprocessWorkorder(
    const std::vector<tcf::WorkOrderData>& in_work_order_data,
    std::vector<tcf::WorkOrderData>& out_work_order_data) {

    tcf::error::ThrowIf<tcf::error::WorkloadError>(
        (this->ext_work_order_info_kme == nullptr),
        "ExtWorkOrderInfoKME instance is not initialized");

    // Get WPE encryption key from in data
    ByteArray wpe_encrypt_key = StrToByteArray(
        ext_work_order_info_kme->GetExtWorkOrderData().c_str());

    auto search_enc_key = wpe_enc_key_map.find(wpe_encrypt_key);
    if (search_enc_key != wpe_enc_key_map.end()) {
        WPEInfo wpe_info = wpe_enc_key_map[wpe_encrypt_key];
        ByteArray wo_key_data = {};

        int status = ext_work_order_info_kme->CreateWorkOrderKeyInfo(
            wpe_encrypt_key, wpe_info.signing_key, wo_key_data);

        if (!status) {
            // skip the key map update if number of allowed work orders
            // for pre-processing is unlimited
            if (max_wo_count_ != KME_WO_COUNT_UNLIMITED) {
                wpe_info.workorder_count++;
                if (wpe_info.workorder_count >= max_wo_count_) {
                    // remove the encryption key from the map because
                    // number of pre-processed work orders reached max limit
                    wpe_enc_key_map.erase(wpe_encrypt_key);
                    SetStatus(ERR_WPE_MAX_WO_COUNT_REACHED,
                        out_work_order_data);
                    return;
                } else {
                    wpe_enc_key_map[wpe_encrypt_key] = wpe_info;
                }
            }
            AddOutput(0, wo_key_data, out_work_order_data);
        } else {
            SetStatus(ERR_WPE_KEY_NOT_FOUND, out_work_order_data);
        }
    }
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
        PreprocessWorkorder(
            in_work_order_data, out_work_order_data);
    }
}  // KMEWorkloadProcessor::ProcessWorkOrder

int KMEWorkloadProcessor::isSgxSimulator() {
#if defined(SGX_SIMULATOR)
#if SGX_SIMULATOR == 1
    return 1;
#else  // SGX_SIMULATOR not 1
    return 0;
#endif  //  #if SGX_SIMULATOR == 1
#else  // SGX_SIMULATOR not defined
    return 0;
#endif  // defined(SGX_SIMULATOR)
}

