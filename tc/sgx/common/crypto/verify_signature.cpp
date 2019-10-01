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

#include "verify_signature.h"
#include "c11_support.h"
#include "crypto_utils.h"

bool verify_signature(const char* cert_pem,
                                 const char* msg,
                                 unsigned int msg_len,
                                 char* signature,
                                 unsigned int signature_len)
{
    X509* crt = NULL;
    int ret;

    BIO* crt_bio = BIO_new_mem_buf((void*)cert_pem, -1);

    crt = PEM_read_bio_X509(crt_bio, NULL, 0, NULL);
    assert(crt != NULL);

    EVP_PKEY* key = X509_get_pubkey(crt);
    assert(key != NULL);

    EVP_MD_CTX* ctx = EVP_MD_CTX_create();
    ret = EVP_VerifyInit_ex(ctx, EVP_sha256(), NULL);
    assert(ret == 1);

    ret = EVP_VerifyUpdate(ctx, msg, msg_len);
    assert(ret == 1);

    int signature_decoded_len = 2048;
    unsigned char signature_decoded[signature_decoded_len];
    ret = tcf::crypto::EVP_DecodeBlock_wrapper(signature_decoded,
                                  signature_decoded_len,
                                  (unsigned char*)signature,
                                  signature_len);
    assert(ret!=-1);

    ret = EVP_VerifyFinal(ctx, (unsigned char*)signature_decoded, ret, key);

    EVP_MD_CTX_destroy(ctx);
    EVP_PKEY_free(key);
    X509_free(crt);
    BIO_free(crt_bio);

    if(ret != 1) // Error
        return false;

    return true; /* Success */
}

