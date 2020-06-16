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

#include <vector>

#include "error.h"
#include "jsonvalue.h"
#include "packages/parson/parson.h"
#include "tcf_error.h"
#include "swig_utils.h"
#include "types.h"

#include "base.h"
#include "signup_info.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t SignupInfo::DeserializeSignupInfo(
    const std::string& serialized_signup_info) {
    tcf_err_t presult = TCF_SUCCESS;

    try {
        const char* pvalue = nullptr;

        JsonValue parsed(json_parse_string(serialized_signup_info.c_str()));
        tcf::error::ThrowIfNull(parsed.value,
            "failed to parse serialized signup info; badly formed JSON");

        JSON_Object* data_object = json_value_get_object(parsed);
        tcf::error::ThrowIfNull(data_object,
            "invalid serialized signup info; missing root object");

        // --------------- verifying key ---------------
        pvalue = json_object_dotget_string(data_object, "verifying_key");
        tcf::error::ThrowIfNull(pvalue,
            "invalid serialized signup info; missing verifying_key");

        this->verifying_key.assign(pvalue);

        // --------------- encryption key ---------------
        pvalue = json_object_dotget_string(data_object, "encryption_key");
        tcf::error::ThrowIfNull(pvalue,
            "invalid serialized signup info; missing encryption_key");

        this->encryption_key.assign(pvalue);

        // --------------- encryption key signature ---------------
        pvalue = json_object_dotget_string(data_object,
            "encryption_key_signature");
        tcf::error::ThrowIfNull(pvalue,
            "invalid serialized signup info; missing encryption_key_signature");

        this->encryption_key_signature.assign(pvalue);

        // --------------- proof data ---------------
        pvalue = json_object_dotget_string(data_object, "proof_data");
        tcf::error::ThrowIfNull(pvalue,
            "invalid serialized signup info; missing proof_data");

        this->proof_data.assign(pvalue);

        // --------------- enclave id ---------------
        pvalue = json_object_dotget_string(data_object, "enclave_persistent_id");
        tcf::error::ThrowIfNull(pvalue,
            "invalid serialized signup info; missing enclave_persistent_id");

        this->enclave_persistent_id.assign(pvalue);
    } catch (tcf::error::Error& e) {
        tcf::enclave_api::base::SetLastError(e.what());
        presult = e.error_code();
    } catch(std::exception& e) {
        tcf::enclave_api::base::SetLastError(e.what());
        presult = TCF_ERR_UNKNOWN;
    } catch(...) {
        tcf::enclave_api::base::SetLastError("Unexpected exception");
        presult = TCF_ERR_UNKNOWN;
    }

    return presult;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// the parallel serialization is in enclave_data.cpp
tcf_err_t SignupInfo::DeserializePublicEnclaveData(
    const std::string& public_enclave_data,
    std::string& verifying_key,
    std::string& encryption_key,
    std::string& encryption_key_signature) {

    tcf_err_t result = TCF_SUCCESS;

    try {
        const char* pvalue = nullptr;

        JsonValue parsed(json_parse_string(public_enclave_data.c_str()));
        tcf::error::ThrowIfNull(parsed.value,
            "failed to parse the public enclave data, badly formed JSON");

        JSON_Object* data_object = json_value_get_object(parsed);
        tcf::error::ThrowIfNull(data_object,
            "invalid public enclave data; missing root object");

        // --------------- verifying key ---------------
        pvalue = json_object_dotget_string(data_object, "VerifyingKey");
        tcf::error::ThrowIfNull(pvalue,
            "invalid public enclave data; missing VerifyingKey");

        verifying_key.assign(pvalue);

        // --------------- encryption key ---------------
        pvalue = json_object_dotget_string(data_object, "EncryptionKey");
        tcf::error::ThrowIfNull(pvalue,
            "invalid public enclave data; missing EncryptionKey");

        encryption_key.assign(pvalue);

        // --------------- encryption key signature ---------------
        pvalue = json_object_dotget_string(data_object,
            "EncryptionKeySignature");
        tcf::error::ThrowIfNull(pvalue,
            "invalid public enclave data; missing EncryptionKeySignature");

        encryption_key_signature.assign(pvalue);
    } catch (tcf::error::Error& e) {
        tcf::enclave_api::base::SetLastError(e.what());
        result = e.error_code();
    } catch(std::exception& e) {
        tcf::enclave_api::base::SetLastError(e.what());
        result = TCF_ERR_UNKNOWN;
    } catch(...) {
        tcf::enclave_api::base::SetLastError("Unexpected exception");
        result = TCF_ERR_UNKNOWN;
    }

    return result;
}  // SignupInfo::DeserializePublicEnclaveData
