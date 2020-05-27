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

#include "crypto.h"
#include "utils.h"
#include "types.h"
#include"error.h"

#include "jsonvalue.h"
#include "parson.h"

#include "enclave_utils.h"
#include "ext_work_order_info_kme.h"

ExtWorkOrderInfoKME::ExtWorkOrderInfoKME(void) {}

ExtWorkOrderInfoKME::~ExtWorkOrderInfoKME(void) {}

int ExtWorkOrderInfoKME::GenerateSigningKey(
    KeyType type, const ByteArray& nonce_hex,
    ByteArray& signing_key, ByteArray& verification_key_hex,
    ByteArray& verification_key_signature_hex) {

    tcf_err_t result = TCF_SUCCESS;

    if (type != KeyType_SECP256K1) {
        Log(TCF_LOG_ERROR,
            "Unsupported KeyType passed to generate signig key pair");
        result = TCF_ERR_CRYPTO;
        return result;
    }

    tcf::crypto::sig::PrivateKey private_sig_key;
    tcf::crypto::sig::PublicKey public_sig_key;

    try {
        // Generate Signing key pair
        private_sig_key.Generate();
        public_sig_key = private_sig_key.GetPublicKey();

        signing_key = StrToByteArray(private_sig_key.Serialize());

        ByteArray v_key_bytes = StrToByteArray(public_sig_key.Serialize());
        std::string v_key_hex_str = ByteArrayToHexEncodedString(v_key_bytes);
        verification_key_hex = StrToByteArray(v_key_hex_str);

        // Generate signature on verification and nonce
        std::string msg = ByteArrayToStr(nonce_hex) +
            ByteArrayToStr(v_key_bytes);
        ByteArray signature = private_sig_key.SignMessage(StrToByteArray(msg));

        std::string signature_hex = ByteArrayToHexEncodedString(signature);
        verification_key_signature_hex = StrToByteArray(signature_hex);
    } catch (tcf::error::CryptoError& e) {
        Log(TCF_LOG_ERROR,
            "Caught Exception while generating Signing key pair: %s, %s",
            e.error_code(), e.what());
        result = TCF_ERR_CRYPTO;
    }

    return result;
}  // ExtWorkOrderInfoKME::GenerateSigningKey

int ExtWorkOrderInfoKME::CreateWorkorderKeyInfo(const ByteArray& wpe_key,
    const ByteArray& kme_skey, ByteArray& json_key_data) {

    // To be implemented
    return 0;
}  // ExtWorkOrderInfoKME::CreateWorkorderKeyInfo

bool ExtWorkOrderInfoKME::CheckAttestationSelf(
    const ByteArray& attestation_data, ByteArray& mrenclave,
    ByteArray& mrsigner, ByteArray& verification_key,
    ByteArray& encryption_public_key) {

    // To be implemented
    return 0;
}  // ExtWorkOrderInfoKME::CheckAttestationSelf
