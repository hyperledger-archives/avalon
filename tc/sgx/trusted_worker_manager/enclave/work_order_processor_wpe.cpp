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

#include "enclave_t.h"
#include <algorithm>
#include <vector>
#include <string>

#include "crypto.h"
#include "jsonvalue.h"
#include "parson.h"
#include "json_utils.h"
#include "error.h"
#include "tcf_error.h"
#include "types.h"
#include "hex_string.h"
#include "utils.h"
#include "enclave_utils.h"

#include "work_order_processor_wpe.h"
#include "work_order_preprocessed_keys_wpe.h"

namespace tcf {

    WorkOrderProcessorWPE::~WorkOrderProcessorWPE() {
        // Sanitize class members storing secrets
        worker_encryption_key.clear();
        session_key.clear();
    }

    /*
     * Decrypt work order request keys by using keys from preprocessed
     * work order key info json
     *
     * @param enclave_data - Instance of EnclaveData class
     * @param wo_req_json_val - Work order request json value
     */
    void WorkOrderProcessorWPE::DecryptWorkOrderKeys(
        EnclaveData* enclave_data, const JsonValue& wo_req_json_val) {
        
        // Decrypt Encryption key
        ByteArray encrypted_session_key_bytes = \
            HexStringToBinary(encrypted_session_key);

        // Use keys from pre-processing json structure
        // passed as ext_work_order_data
        tcf_err_t status = \
            wo_pre_proc_keys.ProcessPreProcessedWorkOrderKeys(
                this->ext_work_order_data, enclave_data);
        tcf::error::ThrowIf<tcf::error::ValueError>(status != TCF_SUCCESS,
            "Failed to process pre-processed work order keys");

        // Decrypt work order encrypted session key using symmetric key
        // from pre-processing json
        session_key = wo_pre_proc_keys.work_order_session_key;
        ByteArray session_key_iv_bytes = HexStringToBinary(session_key_iv);

        JSON_Object* request_object = json_value_get_object(wo_req_json_val);
        tcf::error::ThrowIfNull(request_object,
            "Missing JSON object in work order request");

        JSON_Object* params_object = json_object_dotget_object(request_object, "params");
        tcf::error::ThrowIfNull(params_object,
            "Missing params object in work order request");

	JSON_Array* data_array = json_object_get_array(
            params_object, "inData");
        size_t count = json_array_get_count(data_array);
        tcf::error::ThrowIf<tcf::error::ValueError>(count == 0,
            "Indata is empty");

        size_t i;
        for (i = 0; i < count; i++) {
            JSON_Object* data_object = json_array_get_object(data_array, i);
            WorkOrderDataHandler wo_data(session_key, session_key_iv_bytes);
            // Use in-data key from preprocessed json
            wo_data.Unpack(enclave_data, data_object,
                wo_pre_proc_keys.in_data_keys[i].decrypted_data);
            data_items_in.emplace_back(wo_data);
        }
        data_array = json_object_get_array(params_object, "outData");

        count = json_array_get_count(data_array);
        for (i = 0; i < count; i++) {
            JSON_Object* data_object = json_array_get_object(data_array, i);
            WorkOrderDataHandler wo_data(session_key, session_key_iv_bytes);
            // Use out-data key from preprocessed json
            wo_data.Unpack(enclave_data, data_object,
                wo_pre_proc_keys.out_data_keys[i].decrypted_data);
            data_items_out.emplace_back(wo_data);
        }
    }

    /*
     * Creates Work order response in json format
     */
    JsonValue WorkOrderProcessorWPE::CreateJsonOutput() {
        // Calling base class method to create json response
        JsonValue response = WorkOrderProcessor::CreateJsonOutput();

        JSON_Object* resp_obj = json_value_get_object(response);
        tcf::error::ThrowIfNull(resp_obj,
            "failed to get json object for result");

        JSON_Object* result = json_object_get_object(resp_obj, "result");
        tcf::error::ThrowIfNull(result, "failed to serialize the result");

        // Pack additional parameters extVerificationKey and
        // extVerificationKeySignature from preprocessed json used at client
        // to do 2 step signing verification.
        //
        // extVerificationKey - needs to be used by client to verify signature
        //                of the output
        // extVerificationKeySignature - client needs to verify using
        //                Worker's(KME) public verification key
        JsonSetStr(result, "extVerificationKey",
            ByteArrayToStr(
                wo_pre_proc_keys.verification_key).c_str(),
            "failed to serialize verification key");
        JsonSetStr(result, "extVerificationKeySignature",
            ByteArrayToBase64EncodedString(
                wo_pre_proc_keys.verification_key_signature).c_str(),
            "failed to serialize verification key signature");
        return response;
    }  // WorkOrderProcessorWPE::CreateJsonOutput

    /*
     * Computes signature on the hash by using signing key
     * from work order key info json
     *
     * @param msg_hash - Hash of the message on which signature
     *                   is to be computed
     */
    void WorkOrderProcessorWPE::ComputeSignature(ByteArray& message_hash) {
        // Use signing key from preprocessed json to sign hash
        tcf::crypto::sig::PrivateKey priv_sig_key(
            ByteArrayToStr(wo_pre_proc_keys.signing_key));
        ByteArray sig = priv_sig_key.SignMessage(message_hash);
        worker_signature = base64_encode(sig);
    }  // WorkOrderProcessorWPE::ComputeSignature
}  // namespace tcf
