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

#include "enclave_t.h"
#include <algorithm>
#include <vector>
#include <string>

#include "error.h"
#include "tcf_error.h"
#include "types.h"

#include "crypto.h"
#include "jsonvalue.h"
#include "parson.h"
#include "hex_string.h"
#include "json_utils.h"
#include "utils.h"

#include "enclave_utils.h"
#include "enclave_data.h"

#include "work_order_data.h"
#include "work_order_processor.h"
#include "workload_processor.h"

namespace tcf {
    WorkOrderProcessor::~WorkOrderProcessor() {
        // Sanitize class members storing secrets
        worker_encryption_key.clear();
        session_key.clear();
    }

    JsonValue WorkOrderProcessor::ParseJsonInput(std::string json_str) {
        // Parse the work order request
        JsonValue parsed(json_parse_string(json_str.c_str()));
        tcf::error::ThrowIfNull(
            parsed.value, "failed to parse the work order request, badly formed JSON");

        JSON_Object* request_object = json_value_get_object(parsed);
        tcf::error::ThrowIfNull(request_object, "Missing JSON object in work order request");

        json_request_id = GetJsonNumber(request_object, "id");

        JSON_Object* params_object = json_object_dotget_object(request_object, "params");
        tcf::error::ThrowIfNull(params_object, "Missing params object in work order request");

        response_timeout_msecs = GetJsonNumber(
            params_object,
            "responseTimeoutMSecs");

        payload_format = GetJsonStr(
            params_object,
            "payloadFormat",
            "invalid request; failed to retrieve payload format");

        /* verifyingKey is optional field. This parameter is not described
           in spec and the purpose of this parameter is to verify
           requester signature. Hence don't throw exception
           if param is not there or empty value.
        */
        verifying_key = GetJsonStr(
            params_object,
            "verifyingKey",
            nullptr);

        // resultUri is optional field. Hence don't throw exception
        // if param is not there or empty in the request.
        result_uri = GetJsonStr(
            params_object,
            "resultUri",
            nullptr);

        // notifyUri is optional field. Hence don't throw exception
        // if param is not there or empty in the request.
        notify_uri = GetJsonStr(
            params_object,
            "notifyUri",
            nullptr);

        work_order_id = GetJsonStr(
            params_object,
            "workOrderId",
            "invalid request; failed to retrieve work order id");

        worker_id = GetJsonStr(
            params_object,
            "workerId",
            "invalid request; failed to retrieve worker id");

        workload_id = GetJsonStr(
            params_object,
            "workloadId",
            "invalid request; failed to retrieve work load id");

        requester_id = GetJsonStr(
            params_object,
            "requesterId",
            "invalid request; failed to retrieve requester id");

        // workerEncryptionKey is optional field. Hence don't throw exception
        // if param is not there or empty in the request.
        worker_encryption_key = GetJsonStr(
            params_object,
            "workerEncryptionKey",
            nullptr);

        // dataEncryptionAlgorithm is optional field. Hence don't throw exception
        // if param is not there or empty in the request.
        data_encryption_algorithm = GetJsonStr(
            params_object,
            "dataEncryptionAlgorithm",
            nullptr);

        encrypted_session_key = GetJsonStr(
            params_object,
            "encryptedSessionKey",
            "invalid request; failed to retrieve encrypted session key");

        session_key_iv = GetJsonStr(
            params_object,
            "sessionKeyIv",
            "invalid request; failed to retrieve session key iv");

        requester_nonce = GetJsonStr(
            params_object,
            "requesterNonce",
            "invalid request; failed to retrieve requester nonce");

        encrypted_request_hash = GetJsonStr(
            params_object,
            "encryptedRequestHash",
            "invalid request; failed to retrieve encrypted request hash");

        // requesterSignature is optional field. Hence don't throw exception
        // if param is not there or empty in the request.
        requester_signature = GetJsonStr(
            params_object,
            "requesterSignature",
            nullptr);

        if (data_encryption_algorithm.length() > 0) {
            tcf::error::ThrowIf<tcf::error::ValueError>(data_encryption_algorithm != "AES-GCM-256",
                "Unsupported dataEncryptionAlgorithm found in the request");
        }

        // Convert payload_format to lower case
        std::transform(payload_format.begin(), payload_format.end(),
            payload_format.begin(), ::tolower);
        tcf::error::ThrowIf<tcf::error::ValueError>(payload_format != "json-rpc",
            "Unsupported payload format found in the input");

        // return JSON deserialized value
        return parsed;
    }  // WorkOrderProcessor::ParseJsonInput

    void WorkOrderProcessor::DecryptWorkOrderKeys(
        EnclaveData* enclave_data, const JsonValue& wo_req_json_val) {

        // Decrypt Encryption key
        ByteArray encrypted_session_key_bytes = \
            HexStringToBinary(encrypted_session_key);
        session_key = enclave_data->decrypt_message(
            encrypted_session_key_bytes);
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
            wo_data.Unpack(enclave_data, data_object);
            data_items_in.emplace_back(wo_data);
        }
        data_array = json_object_get_array(params_object, "outData");

        count = json_array_get_count(data_array);
        for (i = 0; i < count; i++) {
            JSON_Object* data_object = json_array_get_object(data_array, i);
            WorkOrderDataHandler wo_data(session_key, session_key_iv_bytes);
            wo_data.Unpack(enclave_data, data_object);
            data_items_out.emplace_back(wo_data);
        }
    }  // WorkOrderProcessor::DecryptWorkOrderKeys

    JsonValue WorkOrderProcessor::CreateJsonOutput() {
        JSON_Status jret;

        // Create the response structure
        JsonValue resp_value(json_value_init_object());
        tcf::error::ThrowIf<tcf::error::RuntimeError>(
            !resp_value.value, "Failed to create the response object");

        JSON_Object* resp = json_value_get_object(resp_value);
        tcf::error::ThrowIfNull(resp, "Failed on retrieval of response object value");

        JsonSetStr(resp, "jsonrpc", "2.0", "failed to serialize jsonrpc");
        JsonSetNumber(resp, "id", json_request_id, "failed to serialize json request id");

        jret = json_object_set_value(resp, "result", json_value_init_object());
        tcf::error::ThrowIf<tcf::error::RuntimeError>(
            jret != JSONSuccess, "failed to serialize result");

        JSON_Object* result = json_object_get_object(resp, "result");
        tcf::error::ThrowIfNull(result, "failed to serialize the result");

        JsonSetStr(result, "workOrderId", work_order_id.c_str(),
                  "failed to serialize work order id");
        JsonSetStr(result, "workloadId", workload_id.c_str(),
                "failed to serialize workload id");
        JsonSetStr(result, "workerId", worker_id.c_str(),
                "failed to serialize worker id");
        JsonSetStr(result, "requesterId", requester_id.c_str(),
                "failed to serialize requester id");
        JsonSetStr(result, "workerNonce", worker_nonce.c_str(),
                "failed to serialize worker nonce");
        JsonSetStr(result, "workerSignature", worker_signature.c_str(),
                "failed to serialize worker signature");

        jret = json_object_set_value(result, "outData", json_value_init_array());
        tcf::error::ThrowIf<tcf::error::RuntimeError>(
            jret != JSONSuccess, "failed to serialize the result data");

        JSON_Array* data_array = json_object_get_array(result, "outData");
        tcf::error::ThrowIfNull(data_array, "failed to serialize the dependency array");

        for (auto out_data : data_items_out)
            out_data.Pack(data_array);

        // return constructed json
        return resp_value;
    }  // WorkOrderProcessor::CreateJsonOutput

    ByteArray WorkOrderProcessor::SerializeJson(JsonValue& json_value) {
        size_t serializedSize = json_serialization_size(json_value);
        ByteArray serialized_response;
        serialized_response.resize(serializedSize);

        JSON_Status jret = json_serialize_to_buffer(json_value,
            reinterpret_cast<char*>(&serialized_response[0]), serialized_response.size());
        tcf::error::ThrowIf<tcf::error::RuntimeError>(
            jret != JSONSuccess, "workorder response serialization failed");
        return serialized_response;
    }  // WorkOrderProcessor::SerializeJson

    std::vector<tcf::WorkOrderData> WorkOrderProcessor::ExecuteWorkOrder(
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

            WorkloadProcessor *processor = \
                WorkloadProcessor::CreateWorkloadProcessor(workload_type);
            tcf::error::ThrowIf<tcf::error::WorkloadError>(
                processor == nullptr, "Invalid workload id");
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
        return out_wo_data;
    }

    ByteArray WorkOrderProcessor::ComputeRequestHash() {
        ByteArray concat_hashes;
        std::string concat_string = requester_nonce + work_order_id +
                worker_id + workload_id + requester_id;
        ByteArray hash_1 =  tcf::crypto::ComputeMessageHash(StrToByteArray(concat_string));

        ByteArray hash_data;
        std::string hash_2;
        size_t i;
        std::sort(data_items_in.begin(), data_items_in.end(),
            [](WorkOrderDataHandler x, WorkOrderDataHandler  y)
            {return x.workorder_data.index < y.workorder_data.index;});
        for (i = 0; i < data_items_in.size(); i++) {
            tcf::WorkOrderDataHandler& d = data_items_in.at(i);
            if (!d.concat_string.empty()) {
                concat_hashes = StrToByteArray(d.concat_string);
                hash_data =  tcf::crypto::ComputeMessageHash(concat_hashes);
                hash_2 = hash_2 + base64_encode(hash_data);
            }
        }

        std::sort(data_items_out.begin(),  data_items_out.end(),
            [](WorkOrderDataHandler x, WorkOrderDataHandler  y)
            {return x.workorder_data.index < y.workorder_data.index;});
        std::string hash_3;
        for (i = 0; i < data_items_out.size(); i++) {
            tcf::WorkOrderDataHandler& d = data_items_out.at(i);
            concat_hashes = StrToByteArray(d.concat_string);
            hash_data =  tcf::crypto::ComputeMessageHash(concat_hashes);
            hash_3 = hash_3 + base64_encode(hash_data);
        }

        concat_string = base64_encode(hash_1) + hash_2 + hash_3;
        concat_hashes = StrToByteArray(concat_string);
        return tcf::crypto::ComputeMessageHash(concat_hashes);
    }

    tcf_err_t WorkOrderProcessor::VerifyEncryptedRequestHash() {
        tcf_err_t verify_status = TCF_SUCCESS;
        ByteArray decrypt_request_hash;
        try {
            decrypt_request_hash = tcf::crypto::skenc::DecryptMessage(session_key,
                                     HexStringToBinary(session_key_iv),
                                     HexStringToBinary(encrypted_request_hash));
        } catch (tcf::error::ValueError& e) {
            Log(TCF_LOG_ERROR, "error::DecryptMessage - %d - %s", e.error_code(), e.what());
            return TCF_ERR_CRYPTO;
        } catch (tcf::error::Error& e) {
            Log(TCF_LOG_ERROR, "error::DecryptMessage - %d - %s\n", e.error_code(), e.what());
            return TCF_ERR_CRYPTO;
        } catch (...) {
            Log(TCF_LOG_ERROR, "error::DecryptMessage - unknown internal error");
            return TCF_ERR_CRYPTO;
        }

        // Compare the request hash and decrypted request hash
        ByteArray request_hash = ComputeRequestHash();
        if ( std::equal(request_hash.begin(), request_hash.end(), decrypt_request_hash.begin()) ) {
            Log(TCF_LOG_INFO, "Decrypted request hash matched with original request hash.. PASS");
        } else {
            Log(TCF_LOG_ERROR, "Decrypted Request hash didn't match with original request hash");
            verify_status = TCF_ERR_CRYPTO;
        }

        return verify_status;
    }

    int WorkOrderProcessor::VerifyRequesterSignature() {
        ByteArray final_hash = ComputeRequestHash();
        ByteArray Signature_byte = base64_decode(requester_signature);

        tcf::crypto::sig::PublicKey public_signing_key_(verifying_key);

        size_t SIG_result = public_signing_key_.VerifySignature(final_hash, Signature_byte);
        if (SIG_result == 1) {
            Log(TCF_LOG_INFO, "Client Signature Verification Passed");
        } else if (SIG_result == 0) {
            Log(TCF_LOG_ERROR, "Client Signature Verification Failed");
        } else {
            Log(TCF_LOG_ERROR, "Client Signature Verification Internal Error");
        }
        return SIG_result;
    }

    ByteArray WorkOrderProcessor::ResponseHashCalculate(
                        std::vector<tcf::WorkOrderData>& wo_data) {
        ByteArray concat_hashes;
        ByteArray nonce = tcf::crypto::RandomBitString(16);
        worker_nonce = base64_encode(tcf::crypto::ComputeMessageHash(nonce));
        std::string concat_string = worker_nonce + work_order_id +
                worker_id + workload_id + requester_id;

        std::string hash_1 = base64_encode(tcf::crypto::ComputeMessageHash(StrToByteArray(concat_string)));

        size_t i = 0;
        size_t out_data_size = data_items_out.size();

        for (auto data : wo_data) {
            if (i < out_data_size) {
                // If client request contains outData then update only
                // the data field
                tcf::WorkOrderDataHandler& out_data = data_items_out.at(i);
                out_data.workorder_data.decrypted_data = data.decrypted_data;
                out_data.ComputeHashString();
            } else {
                // If client has not provided outData element then use
                // session keys to encrypt the output data.
                std::string iv = "";
                std::string encrypted_data_encryption_key = "";
                ByteArray data_encryption_key = session_key;
                ByteArray data_iv = HexStringToBinary(session_key_iv);
                tcf::WorkOrderDataHandler out_data(data, data_encryption_key,
                        data_iv, encrypted_data_encryption_key, iv);
                out_data.ComputeHashString();
                data_items_out.emplace_back(out_data);
            }
            tcf::WorkOrderDataHandler& out_data = data_items_out.at(i);
            out_data.workorder_data.decrypted_data = data.decrypted_data;
            out_data.ComputeHashString();
            i++;
        }

        std::sort(data_items_out.begin(),  data_items_out.end(),
            [](WorkOrderDataHandler x, WorkOrderDataHandler  y)
            {return x.workorder_data.index < y.workorder_data.index;});

        ByteArray hash_2;
        std::string outhash = "";
        for (size_t i = 0; i < data_items_out.size(); i++) {
            tcf::WorkOrderDataHandler& d = data_items_out.at(i);
            if (!d.concat_string.empty()) {
                concat_hashes = StrToByteArray(d.concat_string);
                hash_2 =  tcf::crypto::ComputeMessageHash(concat_hashes);
                outhash +=  base64_encode(hash_2);
            }
        }
        concat_string = hash_1 + outhash;
        ByteArray final_hash = tcf::crypto::ComputeMessageHash(StrToByteArray(concat_string));
        return final_hash;
    }

    void WorkOrderProcessor::ComputeSignature(ByteArray& message_hash) {
        EnclaveData* enclave_data = EnclaveData::getInstance();
        ByteArray sig = enclave_data->sign_message(message_hash);
        worker_signature = base64_encode(sig);
    }

    void WorkOrderProcessor::ConcatHash(ByteArray& dst, ByteArray& src) {
        copy(src.begin(), src.end(), back_inserter(dst));
    }

    ByteArray WorkOrderProcessor::CreateErrorResponse(int err_code, const char* err_message) {
        JSON_Status jret;
        // Create the response structure
        JsonValue resp_value(json_value_init_object());
        tcf::error::ThrowIf<tcf::error::RuntimeError>(
            !resp_value.value, "Failed to create the response object");

        JSON_Object* resp = json_value_get_object(resp_value);
        tcf::error::ThrowIfNull(resp, "Failed on retrieval of response object value");

        JsonSetStr(resp, "jsonrpc", "2.0", "failed to serialize jsonrpc");
        JsonSetNumber(resp, "id", json_request_id, "failed to serialize json request id");

        jret = json_object_set_value(resp, "error", json_value_init_object());
        tcf::error::ThrowIf<tcf::error::RuntimeError>(
            jret != JSONSuccess, "failed to serialize error");

        JSON_Object* error = json_object_get_object(resp, "error");
        tcf::error::ThrowIfNull(error, "failed to serialize the result");

        JsonSetNumber(error, "code", err_code, "failed to serialize error code");
        JsonSetStr(error, "message", err_message, "failed to serialize error message");

        jret = json_object_set_value(error, "data", json_value_init_object());
        tcf::error::ThrowIf<tcf::error::RuntimeError>(
            jret != JSONSuccess, "failed to serialize data");
        JSON_Object* data = json_object_get_object(error, "data");
        tcf::error::ThrowIfNull(data, "failed to serialize the data object");

        JsonSetStr(data, "workOrderId", work_order_id.c_str(),
            "failed to serialize work order id");

        // Serialize the resulting json
        size_t serializedSize = json_serialization_size(resp_value);
        ByteArray serialized_response;
        serialized_response.resize(serializedSize);

        jret = json_serialize_to_buffer(resp_value,
            reinterpret_cast<char*>(&serialized_response[0]), serialized_response.size());
        tcf::error::ThrowIf<tcf::error::RuntimeError>(
            jret != JSONSuccess, "workorder response serialization failed");

        return serialized_response;
    }

    ByteArray WorkOrderProcessor::Process(EnclaveData* enclaveData, std::string json_str) {
        try {
            // Parse serialized json request and return serialized json object
            JsonValue wo_req_json_val = ParseJsonInput(json_str);
            DecryptWorkOrderKeys(enclaveData, wo_req_json_val);
            tcf::error::ThrowIf<tcf::error::ValueError>(VerifyEncryptedRequestHash()!= TCF_SUCCESS,
                "Decryption of client request hash failed. Request is tampered.");
            if (!requester_signature.empty()) {
                tcf::error::ThrowIf<tcf::error::ValueError>(VerifyRequesterSignature()!= true,
                    "Signature verification of client request failed. Request is tampered.");
            }
            std::vector<tcf::WorkOrderData> wo_data = ExecuteWorkOrder(enclaveData);
            size_t i = 0;
            size_t out_data_size = data_items_out.size();
            ByteArray hash = ResponseHashCalculate(wo_data);
            ComputeSignature(hash);
            JsonValue response_json = CreateJsonOutput();
            return SerializeJson(response_json);
        } catch (tcf::error::ValueError& e) {
            return CreateErrorResponse(e.error_code(), e.what());
        } catch (tcf::error::Error& e) {
            return CreateErrorResponse(e.error_code(), e.what());
        } catch (...) {
            return CreateErrorResponse(TCF_ERR_UNKNOWN, "unknown internal error");
        }  // WorkOrderProcessor::Process
    }  // WorkOrderProcessor
}  // namespace tcf

