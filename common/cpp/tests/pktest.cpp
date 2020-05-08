/*
 * Copyright 2020 Intel Corporation
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

/*
 * Test RSA public/private key pair crypto in pkenc_*_key.cpp.
 *
 * Test case from /tc/sgx/trusted_worker_manager/tests/testCrypto.cpp
 * and from upstream common/tests/testCrypto.cpp in
 * https://github.com/hyperledger-labs/private-data-objects
 */

#include <stdexcept>
#include <stdio.h>
#include <openssl/evp.h> // OpenSSL_add_all_digests()

#include "error.h"       // tcf::error
#include "pkenc_private_key.h"
#include "pkenc_public_key.h"


int
main(void)
{
    int  count = 0;
    // A short ByteArray for testing ValueError detection
    ByteArray empty;
    std::string msgStr("Hyperledger Avalon");
    ByteArray msg;
    msg.insert(msg.end(), msgStr.data(), msgStr.data() + msgStr.size());

#if OPENSSL_API_COMPAT < 0x10100000L
    OpenSSL_add_all_digests();
#endif

    printf("Test RSA key management functions.\n");
    try {
        // Default constructor
        tcf::crypto::pkenc::PrivateKey privateKey_t;
        privateKey_t.Generate();
        // PublicKey constructor from PrivateKey
        tcf::crypto::pkenc::PublicKey publicKey_t(privateKey_t);

        publicKey_t = privateKey_t.GetPublicKey();

        // Copy constructors
        tcf::crypto::pkenc::PrivateKey privateKey_t2 = privateKey_t;
        tcf::crypto::pkenc::PublicKey publicKey_t2 = publicKey_t;

        // Assignment operators
        privateKey_t2 = privateKey_t;
        publicKey_t2 = publicKey_t;

        // Move constructors
        privateKey_t2 = tcf::crypto::pkenc::PrivateKey(privateKey_t);
        publicKey_t2 = tcf::crypto::pkenc::PublicKey(privateKey_t2);
        printf("RSA keypair constructors test PASSED\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf("RSA keypair constructors test FAILED\n%s\n", e.what());
        ++count;
    }

    // Default constructor
    tcf::crypto::pkenc::PrivateKey rprivateKey;
    rprivateKey.Generate();
    // PublicKey constructor from PrivateKey
    tcf::crypto::pkenc::PublicKey rpublicKey(rprivateKey);

    printf("Test key serialize functions.\n");
    std::string rprivateKeyStr;
    try {
        rprivateKeyStr = rprivateKey.Serialize();
        printf("RSA private key serialize test PASSED\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf("RSA private key serialize test FAILED\n%s\n", e.what());
        ++count;
    }

    std::string rpublicKeyStr;
    try {
        rpublicKeyStr = rpublicKey.Serialize();
        printf("RSA public key serialize test PASSED\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf("RSA public key serialize test FAILED\n%s\n", e.what());
        ++count;
    }

    printf("Test key deserialize functions.\n");
    tcf::crypto::pkenc::PrivateKey rprivateKey1;
    rprivateKey1.Generate();
    tcf::crypto::pkenc::PublicKey rpublicKey1(rprivateKey1);
    std::string rprivateKeyStr1;
    std::string rpublicKeyStr1;

    try {
        rprivateKey1.Deserialize("");
        printf("FAILED: RSA invalid private key deserialize undetected.\n");
        ++count;
    } catch (const tcf::error::ValueError& e) {
        printf("PASSED: RSA invalid private key deserialize "
            "correctly detected.\n");
    } catch (const std::exception& e) {
        printf("FAILED: RSA invalid private key deserialize "
            "internal error.\n%s\n",
            e.what());
        ++count;
    }

    try {
        rpublicKey1.Deserialize("");
        printf("FAILED: RSA invalid public key deserialize undetected.\n");
        ++count;
    } catch (const tcf::error::ValueError& e) {
        printf(
            "PASS: RSA invalid public key deserialize correctly detected.\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf(
            "FAILED: RSA invalid public key deserialize internal error.\n%s\n",
            e.what());
        ++count;
    }

    try {
        rprivateKey1.Deserialize(rprivateKeyStr);
        rpublicKey1.Deserialize(rpublicKeyStr);
        rprivateKeyStr1 = rprivateKey1.Serialize();
        rpublicKeyStr1 = rpublicKey1.Serialize();
        printf("RSA keypair deserialize test PASSED\n");
    } catch (const std::exception& e) {
        printf("RSA keypair deserialize test FAILED\n%s\n", e.what());
        ++count;
    }


    printf("Test RSA encryption/decryption\n");
    ByteArray ct;
    try {
        ct = rpublicKey.EncryptMessage(msg);
        printf("RSA encryption test PASSED\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf("RSA encryption test FAILED\n%s\n", e.what());
        ++count;
    }

    ByteArray pt;
    try {
        pt = rprivateKey.DecryptMessage(empty);
        printf("FAILED: RSA decryption invalid RSA ciphertext undetected.\n");
        ++count;
    } catch (const tcf::error::ValueError& e) {
        printf("PASSED: RSA decryption test invalid RSA ciphertext "
            "correctly detected.\n");
    } catch (const std::exception& e) {
        printf("FAILED: RSA decryption internal error.\n%s\n", e.what());
        ++count;
    }

    try {
        pt = rprivateKey.DecryptMessage(ct);
        printf("RSA decryption test PASSED\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf("RSA decryption test FAILED\n%s\n", e.what());
        ++count;
    }

    if (!std::equal(pt.begin(), pt.end(), msg.begin())) {
        printf("RSA encryption/decryption test FAILED\n");
        ++count;
    } else {
        printf("RSA encryption/decryption test PASSED\n");
    }

    // Summarize
    if (count == 0) {
        printf("RSA public/private key pair tests PASSED.\n");
    } else {
        printf("RSA public/private key pair tests FAILED %d tests.\n", count);
    }

    return count;
}
