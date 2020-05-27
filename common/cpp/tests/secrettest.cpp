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
 * Test AES-GCM 256 secret key encryption in skenc.cpp.
 *
 * Test case from /tc/sgx/trusted_worker_manager/tests/testCrypto.cpp
 * and from upstream common/tests/testCrypto.cpp in
 * https://github.com/hyperledger-labs/private-data-objects
 */

#include <string.h>
#include <stdio.h>

#include "error.h"       // tcf::error
#include "skenc.h"

int
main(void)
{
    bool is_ok;
    int  count = 0;
    // A short ByteArray for testing ValueError detection
    ByteArray empty;

    std::string msgStr("Hyperledger Avalon");
    ByteArray msg;
    msg.insert(msg.end(), msgStr.data(), msgStr.data() + msgStr.size());
    std::string msgStr2("Confidential Computing");

    printf("Test symmetric encryption functions\n");

    ByteArray key;
    try {
        key = tcf::crypto::skenc::GenerateKey();
        printf("AES-GCM key generation test PASSED\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf("AES-GCM key generation test FAILED:\n%s\n", e.what());
        ++count;
    }
    ByteArray iv;
    try {
        iv = tcf::crypto::skenc::GenerateIV();
        printf("AES-GCM IV generation test PASSED\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf("AES-GCM IV generation test FAILED:\n%s\n", e.what());
        ++count;
    }

    ByteArray ctAES;
    try {
        ctAES = tcf::crypto::skenc::EncryptMessage(key, iv, empty);
        printf("FAILED: AES-GCM empty message encryption test FAILED: "
            "undetected.\n");
        ++count;
    } catch (const std::exception& e) {
        printf("PASSED: AES-GCM empty message encryption test PASSED "
            "(detected)\n");
    }

    try {
        ctAES = tcf::crypto::skenc::EncryptMessage(key, empty);
        printf("FAILED: AES-GCM (random IV) empty message encryption FAILED: "
            "undetected.\n");
        ++count;
    } catch (const std::exception& e) {
        printf(
            "AES-GCM (random IV) empty message encryption test PASSED "
            "(detected)!\n");
    }

    try {
        ctAES = tcf::crypto::skenc::EncryptMessage(key, empty, msg);
        printf("AES-GCM encryption test FAILED, bad IV undetected.\n");
        ++count;
    } catch (const tcf::error::ValueError& e) {
        printf("AES-GCM encryption PASSED; bad IV detected\n");
    } catch (const std::exception& e) {
        printf("AES-GCM encryption test FAILED:\n%s\n", e.what());
        ++count;
    }

    try {
        ctAES = tcf::crypto::skenc::EncryptMessage(empty, iv, msg);
        printf("AES-GCM encryption test FAILED, bad key undetected\n");
        ++count;
    } catch (const tcf::error::ValueError& e) {
        printf("AES-GCM encryption PASSED; bad key detected\n");
    } catch (const std::exception& e) {
        printf("AES-GCM encryption test FAILED:\n%s\n", e.what());
        ++count;
    }

    try {
        ctAES = tcf::crypto::skenc::EncryptMessage(empty, msg);
        printf("AES-GCM (random IV) encryption test FAILED; "
            "bad key undetected.\n");
        ++count;
    } catch (const tcf::error::ValueError& e) {
        printf("PASS: AES-GCM (random IV) encryption PASSED; "
            "bad key detected\n");
    } catch (const std::exception& e) {
        printf("AES-GCM (random IV) encryption test FAILED:\n%s\n", e.what());
        ++count;
    }

    try {
        ctAES = tcf::crypto::skenc::EncryptMessage(key, iv, msg);
        printf("AES-GCM encryption test PASSED\n");
    } catch (const std::exception& e) {
        printf("AES-GCM encryption test FAILED:\n%s\n", e.what());
        ++count;
    }

    // TEST AES_GCM decryption
    ByteArray ptAES;
    try {
        ptAES = tcf::crypto::skenc::DecryptMessage(key, empty, ctAES);
        printf("AES-GCM decryption test FAILED, bad IV undetected.\n");
        ++count;
    } catch (const tcf::error::ValueError& e) {
        printf("PASS: AES-GCM decryption PASSED; bad IV detected\n");
    } catch (const std::exception& e) {
        printf("AES-GCM decryption test FAILED:\n%s\n", e.what());
        ++count;
    }

    try {
        ptAES = tcf::crypto::skenc::DecryptMessage(empty, iv, ctAES);
        printf("AES-GCM decryption test FAILED, bad key undetected.\n");
        ++count;
    } catch (const tcf::error::ValueError& e) {
        printf("PASS: AES-GCM decryption PASSED; bad key detected\n");
    } catch (const std::exception& e) {
        printf("AES-GCM decryption test FAILED:\n%s\n", e.what());
        ++count;
    }

    try {
        ptAES = tcf::crypto::skenc::DecryptMessage(key, iv, ctAES);
        printf("AES-GCM decryption test PASSED\n");
    } catch (const std::exception& e) {
        printf("AES-GCM decryption test FAILED:\n%s\n", e.what());
        ++count;
    }

    ctAES[0]++; // tamper with cryptotext to force decryption to fail
    try {
        ptAES = tcf::crypto::skenc::DecryptMessage(key, iv, ctAES);
        printf(
            "AES-GCM decryption test FAILED; ciphertext tampering "
            "undetected.\n");
        ++count;
    } catch (const tcf::error::CryptoError& e) {
        printf("AES-GCM decryption PASSED; ciphertext tampering detected\n");
    } catch (const std::exception& e) {
        printf("AES-GCM decryption test FAILED\n%s\n", e.what());
        ++count;
    }

    try {
        ptAES = tcf::crypto::skenc::DecryptMessage(key, iv, empty);
        printf(
            "AES-GCM decryption test FAILED, invalid ciphertext size "
            "undetected.\n");
        ++count;
    } catch (const tcf::error::ValueError& e) {
        printf(
            "AES-GCM decryption PASSED; invalid ciphertext size "
            "detected\n");
    } catch (const std::exception& e) {
        printf("AES-GCM decryption test FAILED\n%s\n", e.what());
        ++count;
    }

    // AES_GCM (random IV) encrypt
    try {
        ctAES = tcf::crypto::skenc::EncryptMessage(key, msg);
        printf("AES-GCM (random IV) encryption test PASSED\n");
    } catch (const std::exception& e) {
        printf("AES-GCM (random IV) encryption test FAILED:\n%s\n", e.what());
        ++count;
    }

    // TEST AES_GCM (random IV) decryption
    try {
        ptAES = tcf::crypto::skenc::DecryptMessage(empty, ctAES);
        printf("AES-GCM (random IV) decryption test FAILED; "
            "bad key undetected.\n");
        ++count;
    } catch (const tcf::error::ValueError& e) {
        printf("AES-GCM (random IV) decryption PASSED; bad key detected\n");
    } catch (const std::exception& e) {
        printf("AES-GCM (random IV) decryption test FAILED:\n%s\n", e.what());
        ++count;
    }

    try {
        ptAES = tcf::crypto::skenc::DecryptMessage(key, ctAES);
        printf("AES-GCM (random IV) decryption test PASSED\n");
    } catch (const std::exception& e) {
        printf("AES-GCM (random IV) decryption test FAILED:\n%s\n", e.what());
        ++count;
    }

    ctAES[0]++;
    try {
        ptAES = tcf::crypto::skenc::DecryptMessage(key, ctAES);
        printf("AES-GCM (random IV) decryption test FAILED; "
            "ciphertext tampering undetected.\n");
        ++count;
    } catch (const tcf::error::CryptoError& e) {
        printf("AES-GCM (random IV) decryption PASSED; ciphertext tampering "
            "detected\n");
    } catch (const std::exception& e) {
        printf("AES-GCM (random IV) decryption test FAILED\n%s\n", e.what());
        ++count;
    }

    try {
        ptAES = tcf::crypto::skenc::DecryptMessage(key, empty);
        printf("AES-GCM (random IV) decryption test FAILED; "
            "invalid ciphertext size undetected.\n");
        ++count;
    } catch (const tcf::error::ValueError& e) {
        printf("AES-GCM (random IV) decryption PASSED; "
            "invalid ciphertext size detected\n");
    } catch (const std::exception& e) {
        printf("AES-GCM (random IV) decryption test FAILED\n%s\n", e.what());
        ++count;
    }

    // Test user provided IV
    iv = tcf::crypto::skenc::GenerateIV("uniqueID123456789");
    if (iv.size() != tcf::crypto::constants::IV_LEN) {
        printf("AES-GCM IV generation test FAILED\n");
        ++count;
    } else {
        printf("User-seeded IV generation PASSED\n");
    }

    // Summarize
    if (count == 0) {
        printf("Secret key encryption tests PASSED.\n");
    } else {
        printf("Secret key encryption tests FAILED %d tests.\n", count);
    }

    return count;
}
