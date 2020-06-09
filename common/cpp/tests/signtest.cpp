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

#include "crypto_shared.h" // Sets default CRYPTOLIB_* value

#ifdef CRYPTOLIB_OPENSSL
#include <openssl/evp.h>
#if OPENSSL_API_COMPAT < 0x10100000L
#include <openssl/bn.h>
#endif
#endif

#include "error.h"       // tcf::error
#include "sig_private_key.h"
#include "sig_public_key.h"

// Test point (X,Y)
static const char serialized_test_point_xy[] =
    "04"
    "D860F8A251ACF59E6B3F73F403F30B7742EF8F11F56103BF8F65A6E50D875F2F"
    "04D1F982D83534E5FEA9D0096468E7E7B144487BF579BAC65E7129D9D85E4013";

// Test keys
static const char ec_private_key[] =
    "-----BEGIN EC PRIVATE KEY-----\n"
    "MIIBEwIBAQQgvIEpXzorm7Y6e0Pvzdt5hZicLG8k1+OMi0TSUbBZD0+ggaUwgaIC\n"
    "AQEwLAYHKoZIzj0BAQIhAP////////////////////////////////////7///wv\n"
    "MAYEAQAEAQcEQQR5vmZ++dy7rFWgYpXOhwsHApv82y3OKNlZ8oFbFvgXmEg62ncm\n"
    "o8RlXaT7/A4RCKj9F7RIpoVUGZxH0I/7ENS4AiEA/////////////////////rqu\n"
    "3OavSKA7v9JejNA2QUECAQGhRANCAARxy5u39/yqw2tI98mVa4+KOnR4lAMPdFQr\n"
    "uTiAZ2UMH+JrTyzGoChmP7hIrxHirYc7T0hTPbN3oVgWbfQEmXsv\n"
    "-----END EC PRIVATE KEY-----\n";

static const char public_key[] =
    "-----BEGIN PUBLIC KEY-----\n"
    "MIHVMIGOBgcqhkjOPQIBMIGCAgEBMCwGByqGSM49AQECIQD/////////////////\n"
    "///////////////////+///8LzAGBAEABAEHBCECeb5mfvncu6xVoGKVzocLBwKb\n"
    "/NstzijZWfKBWxb4F5gCIQD////////////////////+uq7c5q9IoDu/0l6M0DZB\n"
    "QQIBAQNCAARxy5u39/yqw2tI98mVa4+KOnR4lAMPdFQruTiAZ2UMH+JrTyzGoChm\n"
    "P7hIrxHirYc7T0hTPbN3oVgWbfQEmXsv\n"
    "-----END PUBLIC KEY-----\n";


#ifdef CRYPTOLIB_OPENSSL
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

    printf("Test ECDSA key management functions.\n");
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
        printf("ECDSA keypair constructors test PASSED\n");
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
        printf("Serialized private key:\n%s", privateKeyStr.c_str());
        printf("Serialize ECDSA private key test PASSED\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf("Serialize ECDSA private key test FAILED:\n%s\n", e.what());
        ++count;
    }

    std::string publicKeyStr;
    try {
        publicKeyStr = publicKey.Serialize();
        printf("Serialized public key:\n%s", publicKeyStr.c_str());
        printf("Serialize ECDSA public key test PASSED\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf("Serialize ECDSA public key test FAILED:\n%s\n", e.what());
        ++count;
    }

    // Must begin with BEGIN PUBLIC KEY line
    std::string public_key_hdr("-----BEGIN PUBLIC KEY-----");
    if (publicKeyStr.compare(0, public_key_hdr.size(), public_key_hdr) == 0) {
        printf("BEGIN PUBLIC KEY header line test PASSED\n");
    } else {
        printf("BEGIN PUBLIC KEY header line test FAILED\n");
        ++count;                                              
    }  

    std::string privateKeyStr1;
    std::string publicKeyStr1;
    tcf::crypto::sig::PrivateKey privateKey1;
    privateKey1.Generate();
    tcf::crypto::sig::PublicKey publicKey1(privateKey1);

    try {
        privateKey1.Deserialize("");
        ++count;
        printf("FAILED: Deserialize invalid ECDSA private key NOT detected\n");
    } catch (const tcf::error::ValueError& e) {
        printf("PASSED: Deserialize invalid ECDSA private key detected\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf("Deserialize invalid ECDSA private key internal error:\n%s\n",
            e.what());
        ++count;
    }

    try {
        publicKey1.Deserialize("");
        ++count;
        printf("FAILED: Deserialize invalid ECDSA public key NOT detected\n");
    } catch (const tcf::error::ValueError& e) {
        printf("PASSED: Deserialize invalid ECDSA public key detected\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf("Deserialize invalid ECDSA public key internal error:\n%s\n",
            e.what());
        ++count;
    }

    try {
        std::string XYstr = publicKey1.SerializeXYToHex();
        printf("Serialized EC point (X,Y) is:\n%s\n", XYstr.c_str());
        publicKey1.DeserializeXYFromHex(XYstr);
        printf("Serialize/Deserialize XY test PASSED\n");
    } catch (const std::exception& e) {
        printf("Serialize/Deserialize XY test FAILED:\n%s\n", e.what());
        ++count;
    }

    tcf::crypto::sig::PublicKey publicKey2;
    try {
        publicKey2.DeserializeXYFromHex(serialized_test_point_xy);
        printf("Deserialize static XY point test PASSED\n");
    } catch (const std::exception& e) {
        printf("Deserialize static XY point test FAILED:\n%s\n", e.what());
        ++count;
    }

    try {
        privateKey1.Deserialize(privateKeyStr);
        publicKey1.Deserialize(publicKeyStr);
        privateKeyStr1 = privateKey1.Serialize();
        publicKeyStr1 = publicKey1.Serialize();
        printf("Deserialize ECDSA keypair test PASSED");
    } catch (const tcf::error::RuntimeError& e) {
        printf("Deserialize ECDSA keypair test FAILED:\n%s\n", e.what());
        ++count;
    }


    printf("Test deserializing pre-existing PEM format ECDSA keys\n");
    tcf::crypto::sig::PrivateKey static_rprivate_key;
    try {
        static_rprivate_key.Deserialize(ec_private_key);
        printf("ECDSA static ECDSA PRIVATE KEY deserialize test PASSED\n");
    } catch (const std::exception& e) {
        printf("ECDSA static ECDSA PRIVATE KEY deserialize test FAILED\n%s\n",
            e.what());
        ++count;
    }

    tcf::crypto::sig::PublicKey  static_public_key;
    try {
        static_public_key.Deserialize(public_key);
        printf("ECDSA static PUBLIC KEY deserialize test PASSED\n");
    } catch (const std::exception& e) {
        printf("ECDSA static PUBLIC KEY deserialize test FAILED\n%s\n",
            e.what());
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
