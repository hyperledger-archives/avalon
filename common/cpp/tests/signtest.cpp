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
 * Test ECDSA Secp256k1 ECDSA signatures in sig_*_key.cpp.
 *
 * Test case from /tc/sgx/trusted_worker_manager/tests/testCrypto.cpp
 * and from upstream common/tests/testCrypto.cpp in
 * https://github.com/hyperledger-labs/private-data-objects
 */

#include <string.h>
#include <stdio.h>
#include <openssl/evp.h>
#if OPENSSL_API_COMPAT < 0x10100000L
#include <openssl/bn.h>
#endif

#include "error.h"       // tcf::error
#include "sig_private_key.h"
#include "sig_public_key.h"

#if OPENSSL_API_COMPAT < 0x10100000L
// For backwards compatibility with older versions of OpenSSL.
// Needed for sig_private_key.cpp.

typedef struct ECDSA_SIG_st {
    BIGNUM *r;
    BIGNUM *s;
} ECDSA_SIG;

// Get the R and S bignumber values of an ECDSA signature.
void ECDSA_SIG_get0(const ECDSA_SIG *sig, const BIGNUM **ptr_r,
        const BIGNUM **ptr_s) {
    if (ptr_r != nullptr)
        *ptr_r = sig->r;
    if (ptr_s != nullptr)
        *ptr_s = sig->s;
}

// Set the R and S bignumber values of an ECDSA signature.
int ECDSA_SIG_set0(ECDSA_SIG *sig, BIGNUM *r, BIGNUM *s) {
    if (r == nullptr || s == nullptr)
        return 0;

    BN_clear_free(sig->r);
    sig->r = r;
    BN_clear_free(sig->s);
    sig->s = s;
    return 1;
}
#endif

int
main(void)
{
    bool is_ok;
    int  count = 0;

    std::string msgStr("Hyperledger Avalon");
    ByteArray msg;
    msg.insert(msg.end(), msgStr.data(), msgStr.data() + msgStr.size());
    std::string msgStr2("Confidential Computing");
    ByteArray msg2;
    msg2.insert(msg2.end(), msgStr2.data(), msgStr2.data() + msgStr2.size());

#if OPENSSL_API_COMPAT < 0x10100000L
    OpenSSL_add_all_digests();
#endif

    // Test ECDSA key management functions
    try {
        // Default constructor
        tcf::crypto::sig::PrivateKey privateKey_t;
        privateKey_t.Generate();
        // PublicKey constructor from PrivateKey
        tcf::crypto::sig::PublicKey publicKey_t(privateKey_t);

        publicKey_t = privateKey_t.GetPublicKey();

        // Copy constructors
        tcf::crypto::sig::PrivateKey privateKey_t2 = privateKey_t;
        tcf::crypto::sig::PublicKey publicKey_t2 = publicKey_t;

        // Assignment operators
        privateKey_t2 = privateKey_t;
        publicKey_t2 = publicKey_t;

        // Move constructors
        privateKey_t2 = tcf::crypto::sig::PrivateKey(privateKey_t);
        publicKey_t2 = tcf::crypto::sig::PublicKey(privateKey_t2);
    } catch (const tcf::error::RuntimeError& e) {
        printf("ECDSA keypair constructors test FAILED:\n%s\n", e.what());
        ++count;
    }

    // Default constructor
    tcf::crypto::sig::PrivateKey privateKey;
    privateKey.Generate();
    // PublicKey constructor from PrivateKey
    tcf::crypto::sig::PublicKey publicKey(privateKey);

    std::string privateKeyStr;
    try {
        privateKeyStr = privateKey.Serialize();
    } catch (const tcf::error::RuntimeError& e) {
        printf("Serialize ECDSA private key test FAILED:\n%s\n", e.what());
        ++count;
    }

    std::string publicKeyStr;
    try {
        publicKeyStr = publicKey.Serialize();
    } catch (const tcf::error::RuntimeError& e) {
        printf("Serialize ECDSA public key test FAILED:\n%s\n", e.what());
        ++count;
    }

    std::string privateKeyStr1;
    std::string publicKeyStr1;
    tcf::crypto::sig::PrivateKey privateKey1;
    privateKey1.Generate();
    tcf::crypto::sig::PublicKey publicKey1(privateKey1);

    try {
        privateKey1.Deserialize("");
    } catch (const tcf::error::ValueError& e) {
        printf("PASSED: Deserialize invalid ECDSA private key detected\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf("Deserialize invalid ECDSA private key internal error:\n%s\n",
            e.what());
        ++count;
    }

    try {
        publicKey1.Deserialize("");
    } catch (const tcf::error::ValueError& e) {
        printf("PASSED: Deserialize invalid ECDSA public key detected\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf("Deserialize invalid ECDSA public key internal error:\n%s\n",
            e.what());
        ++count;
    }

    try {
        std::string XYstr = publicKey1.SerializeXYToHex();
        publicKey1.DeserializeXYFromHex(XYstr);
    } catch (const std::exception& e) {
        printf("Serialize/Deserialize XY test FAILED:\n%s\n", e.what());
        ++count;
    }

    try {
        privateKey1.Deserialize(privateKeyStr);
        publicKey1.Deserialize(publicKeyStr);
        privateKeyStr1 = privateKey1.Serialize();
        publicKeyStr1 = publicKey1.Serialize();
    } catch (const tcf::error::RuntimeError& e) {
        printf("Deserialize ECDSA keypair test FAILED:\n%s\n", e.what());
        ++count;
    }

    // Test of SignMessage and VerifySignature
    printf("SignMessage() Test\n");
    ByteArray sig;
    try {
        sig = privateKey1.SignMessage(msg);
        printf("SignMessage test PASSED\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf("SignMessage test FAILED, signature not computed:\n%s\n",
            e.what());
        ++count;
    }

    printf("VerifySignature() Test\n");
    int res = publicKey1.VerifySignature(msg, sig);
    if (res == -1) {
        printf("VerifySignature test FAILED, internal error.\n");
        ++count;
    } else if (res == 0) {
        printf("VerifySignature test FAILED, invalid signature.\n");
        ++count;
    } else {
        printf("VerifySignature test PASSED\n");
    }

    printf("Negative Test: SignMessage()/VerifySignature()\n");
    ByteArray sig2 = privateKey1.SignMessage(msg2);

    res = publicKey1.VerifySignature(msg2, sig);
    if (res == -1) {
        printf("VerifySignature test FAILED, internal error.\n");
        ++count;
    } else if (res == 1) {
        printf("VerifySignature test FAILED, invalid message not detected\n");
        ++count;
    }

    res = publicKey1.VerifySignature(msg, sig2);
    if (res == -1) {
        printf("VerifySignature test FAILED, internal error.\n");
        ++count;
    } else if (res == 1) {
        printf("VerifySignature negative test FAILED; "
            "invalid signature NOT detected\n");
        ++count;
    } else {
       printf("PASSED: VerifySignature negative test; "
           "expected invalid message detected\n");
    }

    // Summarize
    if (count == 0) {
        printf("Signature verification tests PASSED.\n");
    } else {
        printf("Signature verification FAILED %d tests.\n", count);
    }

    return count;
}
