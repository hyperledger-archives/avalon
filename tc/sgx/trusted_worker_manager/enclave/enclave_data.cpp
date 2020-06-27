/* Copyright 2019 Intel Corporation
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

#include "enclave_common_t.h"
#include "sgx_tseal.h"

#include <stdlib.h>
#include <string>
#include <vector>
#include <string.h>
#include<mbusafecrt.h>

#include "crypto.h"
#include "error.h"
#include "avalon_sgx_error.h"
#include "tcf_error.h"
#include "zero.h"
#include "enclave_utils.h"

#include "jsonvalue.h"
#include "parson.h"

#include "enclave_data.h"

// Below constants are the max limit for serialized version(base64 encoded)
// of private signature and private encryption keys
#define MAX_SERIALIZED_SIG_PRIV_KEY_SIZE 256
#define MAX_SERIALIZED_ENC_PRIV_KEY_SIZE 2048

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
EnclaveData::EnclaveData(void) {
    // Do not attempt to catch errors here... let the calling procedure
    // handle the constructor errors

    // Generate private signing key
    private_signing_key_.Generate();

    // Create the public verifying key
    public_signing_key_ = private_signing_key_.GetPublicKey();

    // Generate private encryption key
    private_encryption_key_.Generate();

    // Create the public encryption key
    public_encryption_key_ = private_encryption_key_.GetPublicKey();

    // Create encryption key signature
    generate_encryption_key_signature();

    SerializePrivateData();
    SerializePublicData();
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
EnclaveData::~EnclaveData(void) {
    // Sanitizing class instance members other than below leads to enclave
    // crash hence avoid the sanitization.
    serialized_private_data_.clear();
    serialized_public_data_.clear();
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void EnclaveData::SerializePrivateData(void) {
    JSON_Status jret;

    // Create serialized wait certificate
    JsonValue dataValue(json_value_init_object());
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        !dataValue.value, "Failed to create enclave data serialization object");

    JSON_Object* dataObject = json_value_get_object(dataValue);
    tcf::error::ThrowIfNull(dataObject, "Failed to retrieve serialization object");

    // Private signing key
    std::string b64_private_signing_key = private_signing_key_.Serialize();
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        b64_private_signing_key.empty(), "failed to serialize the private signing key");

    jret = json_object_dotset_string(
        dataObject, "SigningKey.PrivateKey", b64_private_signing_key.c_str());
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        jret != JSONSuccess, "enclave data serialization failed on private signing key");

    // Sanitize local variables storing secrets
    b64_private_signing_key.clear();

    // Public signing key
    std::string b64_public_signing_key = public_signing_key_.Serialize();
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        b64_public_signing_key.empty(), "failed to serialize the public signing key");

    jret = json_object_dotset_string(
        dataObject, "SigningKey.PublicKey", b64_public_signing_key.c_str());
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        jret != JSONSuccess, "enclave data serialization failed on public signing key");

    // Private encryption key
    std::string b64_private_encryption_key = private_encryption_key_.Serialize();
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        b64_private_encryption_key.empty(), "failed to serialize the private encryption key");

    jret = json_object_dotset_string(
        dataObject, "EncryptionKey.PrivateKey", b64_private_encryption_key.c_str());
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        jret != JSONSuccess, "enclave data serialization failed on private encryption key");

    // Sanitize local variables storing secrets
    b64_private_encryption_key.clear();

    // Public encryption key
    std::string b64_public_encryption_key = public_encryption_key_.Serialize();
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        b64_public_encryption_key.empty(), "failed to serialize the public encryption key");

    jret = json_object_dotset_string(
        dataObject, "EncryptionKey.PublicKey", b64_public_encryption_key.c_str());
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        jret != JSONSuccess, "enclave data serialization failed on public encryption key");

    // Sanitize local variables storing secrets
    b64_public_encryption_key.clear();

    size_t serializedSize = json_serialization_size(dataValue);

    std::vector<char> serialized_buffer;
    serialized_buffer.resize(serializedSize + 1);

    jret = json_serialize_to_buffer(dataValue, &serialized_buffer[0], serializedSize);
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        jret != JSONSuccess, "enclave data serialization failed");

    serialized_private_data_.assign(&serialized_buffer[0]);
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void EnclaveData::SerializePublicData(void) {
    JSON_Status jret;

    // Create serialized wait certificate
    JsonValue dataValue(json_value_init_object());
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        !dataValue.value, "Failed to create enclave data serialization object");

    JSON_Object* dataObject = json_value_get_object(dataValue);
    tcf::error::ThrowIfNull(dataObject, "Failed to retrieve serialization object");

    // Public signing key
    std::string b64_public_signing_key = public_signing_key_.Serialize();
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        b64_public_signing_key.empty(), "failed to serialize the public signing key");

    jret = json_object_dotset_string(dataObject, "VerifyingKey", b64_public_signing_key.c_str());
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        jret != JSONSuccess, "enclave data serialization failed on public signing key");

    // Public encryption key
    std::string b64_public_encryption_key = public_encryption_key_.Serialize();
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        b64_public_encryption_key.empty(), "failed to serialize the public encryption key");

    jret =
        json_object_dotset_string(dataObject, "EncryptionKey", b64_public_encryption_key.c_str());
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        jret != JSONSuccess, "enclave data serialization failed on public encryption key");

    // Public encryption key signature
    jret =
        json_object_dotset_string(dataObject, "EncryptionKeySignature", \
            encryption_key_signature_.c_str());
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        jret != JSONSuccess, \
        "enclave data serialization failed on public encryption key signature");

    size_t serializedSize = json_serialization_size(dataValue);

    std::vector<char> serialized_buffer;
    serialized_buffer.resize(serializedSize + 1);

    jret = json_serialize_to_buffer(dataValue, &serialized_buffer[0], serializedSize);
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        jret != JSONSuccess, "enclave data serialization failed");

    serialized_public_data_.assign(&serialized_buffer[0]);
}
