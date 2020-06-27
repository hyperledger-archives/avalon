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

#include "types.h"
#include "work_order_data.h"
#include "enclave_data.h"

/*
    This WPE specific class processes work order key info json which KME
    returns after pre-process. Also, does integrity check of the
    work order key info json, decrypts requester (client) specific keys
    so that they can be made use by WPE for work order processing.
*/

class WorkOrderPreProcessedKeys {
public:
    WorkOrderPreProcessedKeys() {
        sym_key = {};
        work_order_session_key = {};
        signing_key = {};
        verification_key = "";
        verification_key_signature = {};
        signature = {};
        in_data_keys = {};
        out_data_keys = {};
        encrypted_in_data_keys = {};
        encrypted_out_data_keys = {};
    }

    tcf_err_t ProcessPreProcessedWorkOrderKeys(
        std::string work_order_keys_data_json, EnclaveData* enclave_data);

    ByteArray DecryptKey(const ByteArray& decryption_key,
        const ByteArray& key_to_decrypt);

    ByteArray sym_key;
    ByteArray work_order_session_key;
    ByteArray signing_key;
    Base64EncodedString verification_key;
    ByteArray verification_key_signature;
    ByteArray signature;
    std::vector<tcf::WorkOrderData> in_data_keys;
    std::vector<tcf::WorkOrderData> out_data_keys;

private:
    tcf_err_t ParsePreProcessingJson(
        std::string work_order_keys_data_json, EnclaveData* enclave_data);

    void Unpack(const JSON_Object* keys_object,
        tcf::WorkOrderData& data_keys, std::string& encrypted_data_key);

    ByteArray CalculateWorkOrderKeyInfoHash();

    tcf_err_t VerifySignatureOfWorkOrderKeys(EnclaveData* enclave_data);

    // Below encrypted keys are used to verify integrity of
    // pre-processed work order key info json
    std::string encrypted_sym_key;
    std::string encrypted_work_order_session_key;
    std::string encrypted_signing_key;
    std::vector<std::string> encrypted_in_data_keys;
    std::vector<std::string> encrypted_out_data_keys;
};
