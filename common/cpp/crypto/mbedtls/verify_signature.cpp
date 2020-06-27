/* Copyright 2018-2020 Intel Corporation
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

#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <mbedtls/x509_crt.h> // mbedtls_x509_crt_parse(), *_info()
#include <mbedtls/sha256.h>
#include <mbedtls/rsa.h>
#include <mbedtls/pk.h>       // mbedtls_pk_rsa()

#include "types.h"            // ByteArray
#include "utils.h"            // ByteArrayToStr()
#include "base64.h"           // base64_decode()
#include "crypto_shared.h"
#include "verify_signature.h"

// Mbed TLS library sanity test
#if !defined(MBEDTLS_BIGNUM_C) || !defined(MBEDTLS_RSA_C) || \
    !defined(MBEDTLS_SHA256_C) || !defined(MBEDTLS_MD_C)  || \
    !defined(MBEDTLS_X509_CRT_PARSE_C)
#error "One of MBEDTLS_{BIGNUM,RSA,SHA256,MD,X509_CRT_PARSE}_C undefined."
#endif

#ifndef CRYPTOLIB_MBEDTLS
#error "CRYPTOLIB_MBEDTLS must be defined to compile source with Mbed TLS."
#endif


/**
 * Verify a RSA signature given a message, signature, and cert.
 * Use SHA-256 to hash the message.
 * Use OAEP padding (not PKCS#1 v1.5).
 * Use PKCS#1 v1.5 encryption scheme (not PSS).
 *
 * @param cert_pem X.509 Certificate to verify
 *                 with BEGIN and END BLOCKS and new lines
 * @param msg Message to verify
 * @param msg_len Length of msg
 * @param signature RSA signature to verify message, base64 encoded
 * @param signature_len Length of signature
 * @returns true on success and false on failure.
 */
bool verify_signature(const char *cert_pem,
    const char *msg, unsigned int msg_len,
    const char *signature, unsigned int signature_len)
{
    // RSA keys larger than 16384 are not in practical use in the
    // near future. Increase buffer size if necessary.
    static const unsigned int max_decoded_len = 2048; // <=16384 bit signatures
    static const unsigned int SHA256_HASH_LEN = (256 / 8);
    int rc;
    mbedtls_x509_crt cert;
    mbedtls_rsa_context *rsa_ptr;

    // Sanity checks
    if (cert_pem == nullptr || signature == nullptr)
        return false;
    unsigned int predicted_len = base64_decoded_length(
        signature, signature_len);
    if (predicted_len > max_decoded_len)
        return false;

    // Decode base64-encoded signature
    ByteArray v = base64_decode(std::string(signature, signature_len));
    std::string decoded_str = ByteArrayToStr(v);
    unsigned char *signature_decoded = (unsigned char *)decoded_str.c_str();
    unsigned int decoded_len = decoded_str.size();
    if (decoded_len != predicted_len) {
        goto error_return; // unexpected length--corrupt b64 string?
    }

    // Parse X.509 cert
    mbedtls_x509_crt_init(&cert);
    rc = mbedtls_x509_crt_parse(&cert, (const unsigned char *)cert_pem,
        strlen(cert_pem) + 1);
    if (rc != 0)
        goto error_return;

    // Extract RSA public key (with N and E) from X.509 cert context
    rsa_ptr = mbedtls_pk_rsa(cert.pk);
    if (rsa_ptr == nullptr)
        goto error_return;
    if ((rc = mbedtls_rsa_check_pubkey(rsa_ptr)) != 0)
        goto error_return;

    // Perform SHA-256 hash on message
    unsigned char hash_result[SHA256_HASH_LEN];
    mbedtls_sha256_ret((const unsigned char*)msg, msg_len, hash_result, 0);

    // Verify the signature against the hash digest and RSA public key (N & E)
      rc = mbedtls_rsa_pkcs1_verify(
          rsa_ptr, nullptr, nullptr, MBEDTLS_RSA_PUBLIC,
          MBEDTLS_MD_SHA256, SHA256_HASH_LEN, hash_result,
          signature_decoded);

    // Cleanup
error_return:
    mbedtls_x509_crt_free(&cert);

    return (rc == 0);
}
