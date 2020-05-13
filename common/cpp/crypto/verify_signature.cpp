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

#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/x509v3.h>
#include <openssl/pem.h>
#include <openssl/evp.h>

#include "crypto_shared.h"
#include "verify_signature.h"


/*
 * EVP_DecodeBlock pads its output with \0 if the output length is not
 * a multiple of 3. Check if the base64 string is padded at the end with '='
 * and adjust the output length.
 * For details, see the OpenSSL EVP_EncodeInit man page.
 */
#define ADJUST_DECODE_LENGTH(in, in_len) \
    ((((in)[(in_len) - 1] == '=') ? -1 : 0) + \
     (((in)[(in_len) - 2] == '=') ? -1 : 0))


/* Calculate the length of a base 64 encoded string after decoding. */
static unsigned int
base64_decoded_length(const char *encoded, unsigned int encoded_len)
{
    if (encoded == NULL || encoded_len == 0) {
        return 0;
    }

    unsigned int len = (encoded_len / 4) * 3;

    if (encoded_len > 3)
        len += ADJUST_DECODE_LENGTH(encoded, encoded_len);
    return (len);
}


/**
 * Verify a signature given a message, signature, and cert.
 * Use SHA-256 to hash the message.
 *
 * @param cert_pem X.509 Certificate to verify
 *                 with BEGIN end BLOCKS and new lines
 * @param msg Message to verify
 * @param msg_len Length of msg
 * @param signature Signature to verify message, base64 encoded
 * @param signature_len Length of signature
 * @returns true on success and false on failure.
 */
bool verify_signature(const char* cert_pem,
    const char* msg, unsigned int msg_len,
    const char* signature, unsigned int signature_len)
{
    // DSA or RSA keys larger than 16384 are not in practical use in the
    // near future. Increase buffer size if necessary.
    static const unsigned int max_decoded_len = 2048; // <=16384 bit signatures
    // Decoded result may have 1-2 extra '\0' bytes + ending '\0' byte.
    unsigned char signature_decoded[max_decoded_len + 3];
    int ret;

    // Sanity checks
    if (cert_pem == NULL || signature == NULL)
        return false;
    unsigned int decoded_len = base64_decoded_length(signature, signature_len);
    if (decoded_len > max_decoded_len)
        return false;

    BIO* crt_bio = BIO_new_mem_buf((void*)cert_pem, -1);

    X509* crt = PEM_read_bio_X509(crt_bio, NULL, 0, NULL);
    assert(crt != NULL);

    EVP_PKEY* key = X509_get_pubkey(crt);
    assert(key != NULL);

    EVP_MD_CTX* ctx = EVP_MD_CTX_create();
    ret = EVP_VerifyInit_ex(ctx, EVP_sha256(), NULL);
    assert(ret == 1);

    ret = EVP_VerifyUpdate(ctx, msg, msg_len);
    assert(ret == 1);

    // Decode base64-encoded signature.
    ret = EVP_DecodeBlock(signature_decoded,
        (unsigned char*)signature, signature_len);
    assert(ret != -1);

    ret = EVP_VerifyFinal(ctx, (unsigned char*)signature_decoded, decoded_len,
        key);

    EVP_MD_CTX_destroy(ctx);
    EVP_PKEY_free(key);
    X509_free(crt);
    BIO_free(crt_bio);

    return (ret == 1);
}
