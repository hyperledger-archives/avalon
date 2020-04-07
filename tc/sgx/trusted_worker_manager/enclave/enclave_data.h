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

#include "sgx_tseal.h"

#include <stdint.h>
#include <cassert>
#include <string>

#include "crypto.h"
#include "utils.h"
#include "base64.h"

// JSON format for private data:
// {
//     "SigningKey" :
//     {
//         "PublicKey" : "",
//         "PrivateKey" : "",
//     },
//
//     "EncryptionKey" :
//     {
//         "PublicKey" : "",
//         "PrivateKey" : "",
//     }
// }
//
// JSON format for public data
// {
//     "SigningKey" : "",
//     "EncryptionKey" : ""
//     "EncryptionKeySignature" : ""
// }

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
class EnclaveData {
private:
    EnclaveData(void);
    ~EnclaveData(void);

    static EnclaveData* instance;
 
protected:
    void SerializePrivateData(void);
    void SerializePublicData(void);

    tcf::crypto::sig::PublicKey public_signing_key_;
    tcf::crypto::sig::PrivateKey private_signing_key_;
    tcf::crypto::pkenc::PublicKey public_encryption_key_;
    tcf::crypto::pkenc::PrivateKey private_encryption_key_;
    std::string encryption_key_signature_;

    std::string serialized_private_data_;
    std::string serialized_public_data_;

public:
    static EnclaveData* getInstance() {
        if(!instance) {
            instance = new EnclaveData;
        }
        return instance;
    }

    ByteArray encrypt_message(const ByteArray& message) const {
        return public_encryption_key_.EncryptMessage(message);
    }

    ByteArray decrypt_message(const ByteArray& cipher) const {
        return private_encryption_key_.DecryptMessage(cipher);
    }

    ByteArray sign_message(const ByteArray& message) const {
        return private_signing_key_.SignMessage(message);
    }

    int verify_signature(const ByteArray& message, const ByteArray& signature) const {
        return public_signing_key_.VerifySignature(message, signature);
    }

    std::string get_serialized_signing_key(void) const { return public_signing_key_.Serialize(); }

    std::string get_serialized_encryption_key(void) const {
        return public_encryption_key_.Serialize();
    }

    std::string get_enclave_id(void) const { return public_signing_key_.Serialize(); }

    std::string get_public_data(void) const { return serialized_public_data_; }

    size_t get_public_data_size(void) const { return serialized_public_data_.length(); }

    std::string get_private_data(void) const { return serialized_private_data_; }

    size_t get_private_data_size(void) const { return serialized_private_data_.length(); }

    void generate_encryption_key_signature() {
        std::string b64_pub_encr_key = public_encryption_key_.Serialize();
        ByteArray encr_key_sig_bytes = \
            private_signing_key_.SignMessage(StrToByteArray(b64_pub_encr_key));
        encryption_key_signature_ = base64_encode(encr_key_sig_bytes);
    }

    size_t get_sealed_data_size(void) const {
        size_t sdsize = sgx_calc_sealed_data_size(0, get_private_data_size());
        return sdsize;
    }
};
