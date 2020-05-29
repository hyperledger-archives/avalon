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
 *
 */

/*
 * # Script to generate test RSA keys
 * # Create private key
 * openssl genrsa -out avalon.key 4096
 * # Extract public key from private key
 * # Form: BEGIN RSA PUBLIC KEY
 * openssl rsa -in avalon.key -pubout >avalon.key.public
 * # Form: BEGIN PUBLIC KEY
 * openssl rsa -in avalon.key -RSAPublicKey_out >avalon.key.rsa.public
 */

#include <stdexcept>
#include <stdio.h>

#include "error.h"       // tcf::error
#include "pkenc_private_key.h"
#include "pkenc_public_key.h"

// Test keys
static const char rsa_private_key[] =
    "-----BEGIN RSA PRIVATE KEY-----\n"
    "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\n"
    "-----END RSA PRIVATE KEY-----\n";

static const char rsa_public_key[] =
    "-----BEGIN RSA PUBLIC KEY-----\n"
    "MIICCgKCAgEAviXPKQtoVclvf18iWD1cm6xiNei4pl+m6EpMb9RM2S++/iC1ex7i\n"
    "rJWjamFiWsVfh8xsFhByq/suH1vvGWnHoPGrCNNfTjlt6r9mCKHbVMbZ0eTW2TVG\n"
    "JqfdJHWqAd6CVQB0RPdN4nXJ/zzr4/j70wm7vCqEtsIFo6yJsqX5ac8AFUb9rO/O\n"
    "XlVG9a076Jwqm7Lzod3SVX0FTC2LDI6I/CK0blOX4gAPS/8jfpZYPHFQbXERCo0P\n"
    "wgXXJZJ2EWXDlhVIFYgfKiFITlXljIoM8xp1HC9F+LhsKwK0GUVfU7D7kYEVNmV7\n"
    "dWHsQPWbae2BPSmR/w8tSDQDsDeffgOf/OxXUsqWdi83EKqe/xsCkaseujjvKxtk\n"
    "wm/MzMhZMb36piyfBoHUjUqwSgh23jEKD7NjawxG/zuji1+w8a6qt9P4uXzc44jI\n"
    "G4stYcoD+/UF6Jh6teWMnWyYLfcTf2EcgEwdXQbJCl8z1p2N5eVHPZSh7lVD0euO\n"
    "IhhJRVwNWHVnoR4GALIgLOkqECV3RSjZgTVuC8crfJBUt+zOpiXUv8DaD+kVdAdD\n"
    "dZlgHBW2K9gcivXDegAz84WPbhDrQ3CMM9SJ22B99CR1eG/ez/wzY0GiAZOCIB31\n"
    "IWk34Ehc8tTKjm8fVnXWvYJnXKxACnYd3isoueUA1x01+U0HDnY5ZR0CAwEAAQ==\n"
    "-----END RSA PUBLIC KEY-----\n";

static const char public_key[] =
    // Same as rsa_public_key above with the additional prefix
    // specifying the rsaEncryption OID
    // (in base 64, IjANBgkqhkiG9w0BAQEFAAOCAg8AMIICC ).
    "-----BEGIN PUBLIC KEY-----\n"
    "MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAviXPKQtoVclvf18iWD1c\n"
    "m6xiNei4pl+m6EpMb9RM2S++/iC1ex7irJWjamFiWsVfh8xsFhByq/suH1vvGWnH\n"
    "oPGrCNNfTjlt6r9mCKHbVMbZ0eTW2TVGJqfdJHWqAd6CVQB0RPdN4nXJ/zzr4/j7\n"
    "0wm7vCqEtsIFo6yJsqX5ac8AFUb9rO/OXlVG9a076Jwqm7Lzod3SVX0FTC2LDI6I\n"
    "/CK0blOX4gAPS/8jfpZYPHFQbXERCo0PwgXXJZJ2EWXDlhVIFYgfKiFITlXljIoM\n"
    "8xp1HC9F+LhsKwK0GUVfU7D7kYEVNmV7dWHsQPWbae2BPSmR/w8tSDQDsDeffgOf\n"
    "/OxXUsqWdi83EKqe/xsCkaseujjvKxtkwm/MzMhZMb36piyfBoHUjUqwSgh23jEK\n"
    "D7NjawxG/zuji1+w8a6qt9P4uXzc44jIG4stYcoD+/UF6Jh6teWMnWyYLfcTf2Ec\n"
    "gEwdXQbJCl8z1p2N5eVHPZSh7lVD0euOIhhJRVwNWHVnoR4GALIgLOkqECV3RSjZ\n"
    "gTVuC8crfJBUt+zOpiXUv8DaD+kVdAdDdZlgHBW2K9gcivXDegAz84WPbhDrQ3CM\n"
    "M9SJ22B99CR1eG/ez/wzY0GiAZOCIB31IWk34Ehc8tTKjm8fVnXWvYJnXKxACnYd\n"
    "3isoueUA1x01+U0HDnY5ZR0CAwEAAQ==\n"
    "-----END PUBLIC KEY-----\n"
    ;

int
main(void)
{
    int  count = 0;
    // A short ByteArray for testing ValueError detection
    ByteArray empty;
    std::string msgStr("Hyperledger Avalon");
    ByteArray msg;
    msg.insert(msg.end(), msgStr.data(), msgStr.data() + msgStr.size());

    printf("Test RSA key management functions.\n");
    try {
        printf("Test PrivateKey constructors.\n");
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
        printf("Serialized private key:\n%s", rprivateKeyStr.c_str());
        printf("RSA private key serialize test PASSED\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf("RSA private key serialize test FAILED\n%s\n", e.what());
        ++count;
    }

    std::string rpublicKeyStr;
    try {
        rpublicKeyStr = rpublicKey.Serialize();
        printf("Serialized public key:\n%s", rpublicKeyStr.c_str());
        printf("RSA public key serialize test PASSED\n");
    } catch (const tcf::error::RuntimeError& e) {
        printf("RSA public key serialize test FAILED\n%s\n", e.what());
        ++count;
    }

    // Must begin with BEGIN PUBLIC KEY (not BEGIN RSA PUBLIC KEY) line
    std::string public_key_hdr("-----BEGIN PUBLIC KEY-----");
    if (rpublicKeyStr.compare(0, public_key_hdr.size(), public_key_hdr) == 0) {
        printf("BEGIN PUBLIC KEY header line test PASSED\n");
    } else {
        printf("BEGIN PUBLIC KEY header line test FAILED\n");
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

    printf("Test deserializing pre-existing PEM format RSA keys\n");
    tcf::crypto::pkenc::PrivateKey static_rprivate_key;
    try {
        static_rprivate_key.Deserialize(rsa_private_key);
        printf("RSA static RSA PRIVATE KEY deserialize test PASSED\n");
    } catch (const std::exception& e) {
        printf("RSA static RSA PRIVATE KEY deserialize test FAILED\n%s\n",
            e.what());
        ++count;
    }

    tcf::crypto::pkenc::PublicKey static_rsa_public_key;
    try {
        static_rsa_public_key.Deserialize(rsa_public_key);
        printf("RSA static RSA PUBLIC KEY deserialize test PASSED\n");
    } catch (const std::exception& e) {
        printf("RSA static RSA PUBLIC KEY deserialize test FAILED\n%s\n",
            e.what());
        ++count;
    }

    tcf::crypto::pkenc::PublicKey  static_public_key;
    try {
        static_public_key.Deserialize(public_key);
        printf("RSA static PUBLIC KEY deserialize test PASSED\n");
    } catch (const std::exception& e) {
        printf("RSA static PUBLIC KEY deserialize test FAILED\n%s\n",
            e.what());
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
