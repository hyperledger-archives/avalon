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

//***Unit Test***////
#include "testCrypto.h"
#include "base64.h"
#include "crypto.h"
#include "error.h"

#include <assert.h>
#include <string.h>
#if _UNTRUSTED_

#include <openssl/crypto.h>
#include <stdio.h>
#else

#include "tSgxSSL_api.h"

extern "C" {
void printf(const char* fmt, ...);
}

#endif

namespace pcrypto = tcf::crypto;
namespace constants = tcf::crypto::constants;

// Error handling
namespace Error = tcf::error;

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
int pcrypto::testCrypto()
{
    // A short ByteArray for testing ValueError detection
    ByteArray empty;

    // Test RandomBitString
    size_t rand_length = 32;
    ByteArray rand;
    try
    {
        rand = pcrypto::RandomBitString(rand_length);
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: RandomBitString generation failed.\n%s\n", e.what());
        return -1;
    }

    try
    {
        rand = pcrypto::RandomBitString(0);
        printf("testCrypto: RandomBitString invalid length argument undetected.\n");
        return -1;
    }
    catch (const Error::ValueError& e)
    {
        printf("testCrypto: RandomBitString invalid length argument detected!\n");
    }
    catch (const Error::RuntimeError& e)
    {
        printf("testCrypto: RandomBitString internal error.\n%s\n", e.what());
        return -1;
    }

    printf("RandomBitString test successful!\n%s\n\n", base64_encode(rand).c_str());

    // Test ECDSA key management functions
    try
    {
        // Default constructor
        pcrypto::sig::PrivateKey privateKey_t;
        privateKey_t.Generate();
        // PublicKey constructor from PrivateKey
        pcrypto::sig::PublicKey publicKey_t(privateKey_t);

        publicKey_t = privateKey_t.GetPublicKey();

        // Copy constructors
        pcrypto::sig::PrivateKey privateKey_t2 = privateKey_t;
        pcrypto::sig::PublicKey publicKey_t2 = publicKey_t;

        // Assignment operators
        privateKey_t2 = privateKey_t;
        publicKey_t2 = publicKey_t;

        // Move constructors
        privateKey_t2 = pcrypto::sig::PrivateKey(privateKey_t);
        publicKey_t2 = pcrypto::sig::PublicKey(privateKey_t2);
    }
    catch (const Error::RuntimeError& e)
    {
        printf("testCrypto: ECDSA keypair constructors test failed.\n%s\n", e.what());
        return -1;
    }

    printf("testCrypto: ECDSA keypair constructors test successful!\n\n");

    // Default constructor
    pcrypto::sig::PrivateKey privateKey;
    privateKey.Generate();
    // PublicKey constructor from PrivateKey
    pcrypto::sig::PublicKey publicKey(privateKey);

    std::string privateKeyStr;
    try
    {
        privateKeyStr = privateKey.Serialize();
    }
    catch (const Error::RuntimeError& e)
    {
        printf("testCrypto: Serialize ECDSA private key test failed.\n%s\n", e.what());
        return -1;
    }

    std::string publicKeyStr;
    try
    {
        publicKeyStr = publicKey.Serialize();
    }
    catch (const Error::RuntimeError& e)
    {
        printf("testCrypto: Serialize ECDSA public key test failed.\n%s\n", e.what());
        return -1;
    }

    std::string privateKeyStr1;
    std::string publicKeyStr1;
    pcrypto::sig::PrivateKey privateKey1;
    privateKey1.Generate();
    pcrypto::sig::PublicKey publicKey1(privateKey1);

    try
    {
        privateKey1.Deserialize("");
    }
    catch (const Error::ValueError& e)
    {
        printf("testCrypto: Deserialize invalid ECDSA private key detected!\n%s\n", e.what());
    }
    catch (const Error::RuntimeError& e)
    {
        printf(
            "testCrypto: Deserialize invalid ECDSA private key internal "
            "error.\n%s\n",
            e.what());
        return -1;
    }

    try
    {
        publicKey1.Deserialize("");
    }
    catch (const Error::ValueError& e)
    {
        printf("testCrypto: Deserialize invalid ECDSA public key detected!\n%s\n", e.what());
    }
    catch (const Error::RuntimeError& e)
    {
        printf(
            "testCrypto: Deserialize invalid ECDSA public key internal "
            "error.\n%s\n",
            e.what());
        return -1;
    }

    try
    {
        std::string XYstr = publicKey1.SerializeXYToHex();
        publicKey1.DeserializeXYFromHex(XYstr);
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: Serialize/Deserialize XY test failed\n%s\n", e.what());
        return -1;
    }

    try
    {
        privateKey1.Deserialize(privateKeyStr);
        publicKey1.Deserialize(publicKeyStr);
        privateKeyStr1 = privateKey1.Serialize();
        publicKeyStr1 = publicKey1.Serialize();
    }
    catch (const Error::RuntimeError& e)
    {
        printf("testCrypto: Deserialize ECDSA keypair test failed.\n%s\n", e.what());
        return -1;
    }

    printf("testCrypto: Serialize/Deserialize ECDSA keypairs tests successful!\n\n");
    // Test ComputeMessageHash

    std::string msgStr("Proof of Elapsed Time");
    ByteArray msg;
    msg.insert(msg.end(), msgStr.data(), msgStr.data() + msgStr.size());
    std::string msg_SHA256_B64("43fTaEjBzvug9rf0RRU6anIHfgdoqNjQ/dy/jzcVcAk=");
    ByteArray hash = ComputeMessageHash(msg);
    std::string hashStr_B64 = base64_encode(hash);
    if (hashStr_B64.compare(msg_SHA256_B64) != 0)
    {
        printf(
            "testCrypto: ComputeMessageHash test failed, SHA256 digest "
            "mismatch.\n");
        return -1;
    }
    printf("testCrypto: ComputeMessageHash test passed!\n\n");
    // End Test ComputMessageHash

    // Test of SignMessage and VerifySignature
    ByteArray sig;
    try
    {
        sig = privateKey1.SignMessage(msg);
    }
    catch (const Error::RuntimeError& e)
    {
        printf("testCrypto: SignMessage test failed, signature not computed.\n%s\n", e.what());
        return -1;
    }
    printf("testCrypto: SignMessage test passed!\n\n");

    int res = publicKey1.VerifySignature(msg, sig);
    if (res == -1)
    {
        printf("testCrypto: VerifySignature test failed, internal error.\n");
        return -1;
    }
    if (res == 0)
    {
        printf("testCrypto: VerifySignature test failed, invalid signature.\n");
        return -1;
    }

    std::string msgStr2("Proof of Work");
    ByteArray sig2;
    ByteArray msg2;
    msg2.insert(msg2.end(), msgStr2.data(), msgStr2.data() + msgStr2.size());
    try
    {
        sig2 = privateKey1.SignMessage(msg2);
    }
    catch (const Error::RuntimeError& e)
    {
        printf("testCrypto: SignMessage test failed, signature not computed.\n%s\n", e.what());
        return -1;
    }

    res = publicKey1.VerifySignature(msg2, sig);
    if (res == -1)
    {
        printf("testCrypto: VerifySignature test failed, internal error.\n");
        return -1;
    }
    if (res == 1)
    {
        printf("testCrypto: VerifySignature test failed, invalid message not detected!\n");
        return -1;
    }

    printf("testCrypto: VerifySignature, invalid message detected!\n");
    res = publicKey1.VerifySignature(msg, sig2);
    if (res == -1)
    {
        printf("testCrypto: VerifySignature test failed, internal error.\n");
        return -1;
    }
    if (res == 1)
    {
        printf("testCrypto: VerifySignature test failed, invalid signature not detected!\n");
        return -1;
    }
    printf("testCrypto: VerifySignature, invalid signature detected!\n");
    printf("testCrypto: VerifySignature test passed!\n\n");

    // RSA encryption tests

    // Test RSA key management functions
    try
    {
        // Default constructor
        pcrypto::pkenc::PrivateKey privateKey_t;
        privateKey_t.Generate();
        // PublicKey constructor from PrivateKey
        pcrypto::pkenc::PublicKey publicKey_t(privateKey_t);

        publicKey_t = privateKey_t.GetPublicKey();

        // Copy constructors
        pcrypto::pkenc::PrivateKey privateKey_t2 = privateKey_t;
        pcrypto::pkenc::PublicKey publicKey_t2 = publicKey_t;

        // Assignment operators
        privateKey_t2 = privateKey_t;
        publicKey_t2 = publicKey_t;

        // Move constructors
        privateKey_t2 = pcrypto::pkenc::PrivateKey(privateKey_t);
        publicKey_t2 = pcrypto::pkenc::PublicKey(privateKey_t2);
    }
    catch (const Error::RuntimeError& e)
    {
        printf("testCrypto: RSA keypair constructors test failed.\n%s\n", e.what());
        return -1;
    }

    printf("testCrypto: RSA keypair constructors test successful!\n\n");

    // Default constructor
    pcrypto::pkenc::PrivateKey rprivateKey;
    rprivateKey.Generate();
    // PublicKey constructor from PrivateKey
    pcrypto::pkenc::PublicKey rpublicKey(rprivateKey);

    std::string rprivateKeyStr;
    try
    {
        rprivateKeyStr = rprivateKey.Serialize();
    }
    catch (const Error::RuntimeError& e)
    {
        printf("testCrypto: RSA private key serialize test failed.\n%s\n", e.what());
        return -1;
    }

    std::string rpublicKeyStr;
    try
    {
        rpublicKeyStr = rpublicKey.Serialize();
    }
    catch (const Error::RuntimeError& e)
    {
        printf("testCrypto: RSA public key serialize test failed.\n%s\n", e.what());
        return -1;
    }

    pcrypto::pkenc::PrivateKey rprivateKey1;
    rprivateKey1.Generate();
    pcrypto::pkenc::PublicKey rpublicKey1(rprivateKey1);
    std::string rprivateKeyStr1;
    std::string rpublicKeyStr1;
    try
    {
        rprivateKey1.Deserialize("");
        printf("testCrypto: RSA invalid private key deserialize undetected.\n");
        return -1;
    }
    catch (const Error::ValueError& e)
    {
        printf("testCrypto: RSA invalid private key deserialize detected!\n%s\n", e.what());
    }
    catch (const std::exception& e)
    {
        printf(
            "testCrypto: RSA invalid private key deserialize internal "
            "error!\n%s\n",
            e.what());
        return -1;
    }

    try
    {
        rpublicKey1.Deserialize("");
        printf("testCrypto: RSA invalid public key deserialize undetected.\n");
        return -1;
    }
    catch (const Error::ValueError& e)
    {
        printf("testCrypto: RSA invalid public key deserialize detected!\n%s\n", e.what());
    }
    catch (const Error::RuntimeError& e)
    {
        printf("testCrypto: RSA invalid public key deserialize internal error!\n%s\n", e.what());
        return -1;
    }

    try
    {
        rprivateKey1.Deserialize(rprivateKeyStr);
        rpublicKey1.Deserialize(rpublicKeyStr);
        rprivateKeyStr1 = rprivateKey1.Serialize();
        rpublicKeyStr1 = rpublicKey1.Serialize();
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: RSA keypair deserialize test failed.\n%s\n", e.what());
        return -1;
    }
    // Test RSA encryption/decryption

    ByteArray ct;
    try
    {
        ct = rpublicKey.EncryptMessage(msg);
    }
    catch (const Error::RuntimeError& e)
    {
        printf("testCrypto: RSA encryption test failed.\n%s\n", e.what());
        return -1;
    }

    ByteArray pt;
    try
    {
        pt = rprivateKey.DecryptMessage(empty);
        printf("testCrypto: RSA decryption invalid RSA ciphertext undetected.\n");
        return -1;
    }
    catch (const Error::ValueError& e)
    {
        printf("testCrypto: RSA decryption test invalid RSA ciphertext correctly detected!\n");
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: RSA decryption internal error.\n%s\n", e.what());
        return -1;
    }

    try
    {
        pt = rprivateKey.DecryptMessage(ct);
    }
    catch (const Error::RuntimeError& e)
    {
        printf("testCrypto: RSA decryption test failed.\n%s\n", e.what());
        return -1;
    }

    if (!std::equal(pt.begin(), pt.end(), msg.begin()))
    {
        printf("testCrypto: RSA encryption/decryption test failed.\n");
        return -1;
    }
    printf("testCrypto: RSA encryption/decryption test passed!\n\n");

    // Test symmetric encryption functions

    ByteArray key;
    try
    {
        key = pcrypto::skenc::GenerateKey();
    }
    catch (const Error::RuntimeError& e)
    {
        printf("testCrypto: AES-GCM key generation test failed.\n%s\n", e.what());
        return -1;
    }
    ByteArray iv;
    try
    {
        iv = pcrypto::skenc::GenerateIV();
    }
    catch (const Error::RuntimeError& e)
    {
        printf("testCrypto: AES-GCM IV generation test failed.\n%s\n", e.what());
        return -1;
    }

    ByteArray ctAES;
    try
    {
        ctAES = pcrypto::skenc::EncryptMessage(key, iv, empty);
        printf("testCrypto: AES-GCM empty message encryption test failed: undetected.\n");
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: AES-GCM empty message encryption test successful (detected)!\n%s\n",
            e.what());
    }

    try
    {
        ctAES = pcrypto::skenc::EncryptMessage(key, empty);
        printf(
            "testCrypto: AES-GCM (random IV) empty message encryption test failed: undetected.\n");
    }
    catch (const std::exception& e)
    {
        printf(
            "testCrypto: AES-GCM (random IV) empty message encryption test successful "
            "(detected)!\n%s\n",
            e.what());
    }

    try
    {
        ctAES = pcrypto::skenc::EncryptMessage(key, empty, msg);
        printf("testCrypto: AES-GCM encryption test failed, bad IV undetected.\n");
        return -1;
    }
    catch (const Error::ValueError& e)
    {
        printf("testCrypto: AES-GCM encryption correct, bad IV detected!\n\n");
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: AES-GCM encryption test failed.\n%s\n", e.what());
        return -1;
    }

    try
    {
        ctAES = pcrypto::skenc::EncryptMessage(empty, iv, msg);
        printf("testCrypto: AES-GCM encryption test failed, bad key undetected.\n");
        return -1;
    }
    catch (const Error::ValueError& e)
    {
        printf("testCrypto: AES-GCM encryption correct, bad key detected!\n\n");
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: AES-GCM encryption test failed.\n%s\n", e.what());
        return -1;
    }

    try
    {
        ctAES = pcrypto::skenc::EncryptMessage(empty, msg);
        printf("testCrypto: AES-GCM (random IV) encryption test failed, bad key undetected.\n");
        return -1;
    }
    catch (const Error::ValueError& e)
    {
        printf("testCrypto: AES-GCM (random IV) encryption correct, bad key detected!\n\n");
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: AES-GCM (random IV) encryption test failed.\n%s\n", e.what());
        return -1;
    }

    try
    {
        ctAES = pcrypto::skenc::EncryptMessage(key, iv, msg);
        printf("testCrypto: AES-GCM encryption test successful!\n\n");
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: AES-GCM encryption test failed.\n%s\n", e.what());
        return -1;
    }

    // TEST AES_GCM decryption
    ByteArray ptAES;
    try
    {
        ptAES = pcrypto::skenc::DecryptMessage(key, empty, ctAES);
        printf("testCrypto: AES-GCM decryption test failed, bad IV undetected.\n");
        return -1;
    }
    catch (const Error::ValueError& e)
    {
        printf("testCrypto: AES-GCM decryption correct, bad IV detected!\n\n");
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: AES-GCM decryption test failed.\n%s\n", e.what());
        return -1;
    }

    try
    {
        ptAES = pcrypto::skenc::DecryptMessage(empty, iv, ctAES);
        printf("testCrypto: AES-GCM decryption test failed, bad key undetected.\n");
        return -1;
    }
    catch (const Error::ValueError& e)
    {
        printf("testCrypto: AES-GCM decryption correct, bad key detected!\n\n");
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: AES-GCM decryption test failed.\n%s\n", e.what());
        return -1;
    }

    try
    {
        ptAES = pcrypto::skenc::DecryptMessage(key, iv, ctAES);
        printf("testCrypto: AES-GCM decryption test successful!\n\n");
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: AES-GCM decryption test failed.\n%s\n", e.what());
        return -1;
    }

    ctAES[0]++;
    try
    {
        ptAES = pcrypto::skenc::DecryptMessage(key, iv, ctAES);
        printf(
            "testCrypto: AES-GCM decryption test failed, ciphertext tampering "
            "undetected.\n");
        return -1;
    }
    catch (const Error::CryptoError& e)
    {
        printf(
            "testCrypto: AES-GCM decryption correct, ciphertext tampering "
            "detected!\n\n");
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: AES-GCM decryption test failed\n%s\n", e.what());
        return -1;
    }

    try
    {
        ptAES = pcrypto::skenc::DecryptMessage(key, iv, empty);
        printf(
            "testCrypto: AES-GCM decryption test failed, invalid ciphertext size "
            "undetected.\n");
        return -1;
    }
    catch (const Error::ValueError& e)
    {
        printf(
            "testCrypto: AES-GCM decryption correct, invalid ciphertext size "
            "detected!\n\n");
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: AES-GCM decryption test failed\n%s\n", e.what());
        return -1;
    }

    // AES_GCM (random IV) encrypt
    try
    {
        ctAES = pcrypto::skenc::EncryptMessage(key, msg);
        printf("testCrypto: AES-GCM (random IV) encryption test successful!\n\n");
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: AES-GCM (random IV) encryption test failed.\n%s\n", e.what());
        return -1;
    }

    // TEST AES_GCM (random IV) decryption
    try
    {
        ptAES = pcrypto::skenc::DecryptMessage(empty, ctAES);
        printf("testCrypto: AES-GCM (random IV) decryption test failed, bad key undetected.\n");
        return -1;
    }
    catch (const Error::ValueError& e)
    {
        printf("testCrypto: AES-GCM (random IV) decryption correct, bad key detected!\n\n");
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: AES-GCM (random IV) decryption test failed.\n%s\n", e.what());
        return -1;
    }

    try
    {
        ptAES = pcrypto::skenc::DecryptMessage(key, ctAES);
        printf("testCrypto: AES-GCM (random IV) decryption test successful!\n\n");
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: AES-GCM (random IV) decryption test failed.\n%s\n", e.what());
        return -1;
    }

    ctAES[0]++;
    try
    {
        ptAES = pcrypto::skenc::DecryptMessage(key, ctAES);
        printf(
            "testCrypto: AES-GCM (random IV) decryption test failed, ciphertext tampering "
            "undetected.\n");
        return -1;
    }
    catch (const Error::CryptoError& e)
    {
        printf(
            "testCrypto: AES-GCM (random IV) decryption correct, ciphertext tampering "
            "detected!\n\n");
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: AES-GCM (random IV) decryption test failed\n%s\n", e.what());
        return -1;
    }

    try
    {
        ptAES = pcrypto::skenc::DecryptMessage(key, empty);
        printf(
            "testCrypto: AES-GCM (random IV) decryption test failed, invalid ciphertext size "
            "undetected.\n");
        return -1;
    }
    catch (const Error::ValueError& e)
    {
        printf(
            "testCrypto: AES-GCM (random IV) decryption correct, invalid ciphertext size "
            "detected!\n\n");
    }
    catch (const std::exception& e)
    {
        printf("testCrypto: AES-GCM (random IV) decryption test failed\n%s\n", e.what());
        return -1;
    }

    // Test user provided IV
    iv = pcrypto::skenc::GenerateIV("uniqueID123456789");
    if (iv.size() != constants::IV_LEN)
    {
        printf("testCrypto: AES-GCM IV generation test failed.\n");
        return -1;
    }
    printf("testCrypto: user seeded IV generation successful!\n\n");

    //Test verify report
    res = testVerifyReport();
    if(res != 0) {
        printf("testCrypto: verify report failed\n");
        return -1;
    }
    printf("testCrypto: verify report successful\n");

    return 0;
}  // pcrypto::testCrypto()

int pcrypto::testVerifyReport() {
    unsigned char mock_verification_report[] = "{\"nonce\":\"35E8FB64ACFB4A8E\",\"id\":\"284773557701539118279755254416631834508\",\"timestamp\":\"2018-07-11T19:30:35.556996\",\"epidPseudonym\":\"2iBfFyk5LE9du4skK9JjlRh1x5RvCIz/Z2nnoViIYY8W8TmIHg53UlEm2sp8NYVgT+LGSp0oxZgFcIg4p0BWxXqoBEEDnJFaVxgw0fS/RfhtF8yVNbVQjYjgQjw06wPalXzzNnjFpb873Rycj3JKSzkR3KfvKZfA/CJqEkTZK7U=\",\"isvEnclaveQuoteStatus\":\"GROUP_OUT_OF_DATE\",\"platformInfoBlob\":\"1502006504000700000808010101010000000000000000000007000006000000020000000000000AE791776C1D5C169132CA96D56CC2D59E5A46F23E39933DFB3B4962A8608AB53D84F77D254627D906B46F08073D33FF511E74BC318E8E0C37483C5B08899D1B5E9F\",\"isvEnclaveQuoteBody\":\"AgABAOcKAAAGAAUAAAAAAImTjvVbjrhQGXLFwbdtyMgAAAAAAAAAAAAAAAAAAAAABwf///8BAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAAAAAAAHAAAAAAAAAMnL+UpC5HcF6MBCXsbYd5KUw2gc1tWgNPHNtK4g1NgKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACp0uDGT8avpUCoA1LU47KLt5L/RJSpeFFT9807MyvETgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOeQAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAy7+m9Dx2rPbbbBWJUud3AHHnxoFWhlMQCyNjtVRvD2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\"}";
    unsigned int mock_report_len = strlen((char*)mock_verification_report);
    unsigned char mock_signature[] = "TuHse3QCPZtyZP436ltUAc6cVlIDzwKyjguOBDMmoou/NlGylzY0EtOEbHvVZ28HT8U1CiCVVmZso2ut2HY3zFDfpUg5/FV7FUSw/UhDOu3xkDwicrOvd/P1C3BKWJ6vJWghv3QLpgDItQPapFH/3OfciWs10kC3KV4UY+Irkrrck9+h3+FaltM/52AL1m1QWZIutMk1gDs5nz5N87gGvbc9VJKXx/RDDmvX1rLfqnPpH3owkprVLhU8iLcmPPN+irjfH4f4GGrnbWYCYK5wfB1BBbFl8ppqxm4Gr8ekePCPLMjYYLpKYWEipvTgaYl63zg+C9r8g+sIA3I9Jr3Exg==";

    sgx_quote_t q;
    get_quote_from_report(mock_verification_report, mock_report_len, &q);
    printf("verify_report: get_quote_from_report: successful\n");

    bool r;
    //verify good quote, but group-of-date is not considered ok
    r = verify_enclave_quote_status((char*)mock_verification_report, mock_report_len, 0);
    assert(r==false); //failure because group_out_of_date not ok
    printf("verify_report: verify_enclave_quote_status: successful\n");

    //verify good quote and group-of-date is considered ok
    r = verify_enclave_quote_status((char*)mock_verification_report, mock_report_len, 1);
    assert(r==true);
    printf("verify_report: verify_enclave_quote_status: successful\n");

    //verify chain of hard-coded certificates
    r = verify_ias_certificate_chain(NULL, 0);
#ifdef IAS_CA_CERT_REQUIRED
    assert(r==true);
#else
    assert(r==false);
#endif
    printf("verify_report: verify_ias_certificate_chain: successful\n");

    //verify the passed certificate (though it's the one stored) against the hard-coded CA certificate
    r = verify_ias_certificate_chain((char*)ias_report_signing_cert_der, ias_report_signing_cert_der_len);
#ifdef IAS_CA_CERT_REQUIRED
    assert(r==true);
#else
    assert(r==false);
#endif
    printf("verify_report: verify_ias_certificate_chain: successful\n");

    //verify good IAS signature
    r = verify_ias_report_signature((char*)ias_report_signing_cert_der,
                                        ias_report_signing_cert_der_len,
                                        (char*)mock_verification_report,
                                        mock_report_len,
                                        (char*)mock_signature,
                                        strlen((char*)mock_signature));
    assert(r==true);
    printf("verify_report: verify_ias_report_signature: successful\n");

    //change one byte of report and recheck
    mock_verification_report[0] = 'r'; //change 1 byte
    //verify corrupted report
    r = verify_ias_report_signature((char*)ias_report_signing_cert_der,
                                        ias_report_signing_cert_der_len,
                                        (char*)mock_verification_report,
                                        mock_report_len,
                                        (char*)mock_signature,
                                        strlen((char*)mock_signature));
    assert(r==false);
    printf("verify_report: verify_ias_report_signature: successful\n");
    return 0;
} //int pcrypto::testVerifyReport()
