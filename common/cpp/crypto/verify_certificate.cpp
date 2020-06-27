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
#include "verify_certificate.h"

#ifndef CRYPTOLIB_OPENSSL
#error "CRYPTOLIB_OPENSSL must be defined to compile source with OpenSSL."
#endif


/**
 * Verify that cert_pem is signed by CA,
 * using CA certificate ca_cert_pem as a root of trust.
 *
 * @param cert_pem    X.509 Certificate to verify
 *                    with BEGIN and END lines and new lines
 * @param ca_cert_pem CA Certificate (usually the IAS CA cert)
 *                    with BEGIN and END lines and new lines
 * @returns true on success and false on failure
 */
bool verify_certificate_chain(const char* cert_pem,
                              const char* ca_cert_pem)
{
    if (cert_pem == nullptr || ca_cert_pem == nullptr) // sanity check
        return false;

    BIO* crt_bio = BIO_new_mem_buf((void*)cert_pem, -1);
    X509* crt = PEM_read_bio_X509(crt_bio, nullptr, 0, nullptr);
    assert(crt != nullptr);

    BIO* cacrt_bio = BIO_new_mem_buf((void*)ca_cert_pem, -1);
    X509* cacrt = PEM_read_bio_X509(cacrt_bio, nullptr, 0, nullptr);
    assert(cacrt != nullptr);

    X509_STORE* s = X509_STORE_new();
    X509_STORE_add_cert(s, cacrt);
    X509_STORE_CTX* ctx = X509_STORE_CTX_new();
    X509_STORE_CTX_init(ctx, s, crt, nullptr);
    int rc = X509_verify_cert(ctx);

    X509_STORE_CTX_free(ctx);
    X509_STORE_free(s);
    X509_free(crt);
    X509_free(cacrt);
    BIO_free(crt_bio);
    BIO_free(cacrt_bio);

    return (rc > 0);
}
