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

#include "verify_certificate.h"
#include "c11_support.h"

bool verify_certificate_chain(const char* cert_pem,
                              const char* ca_cert_pem)
{
    assert(cert_pem!=NULL);

    /* Using the IAS CA certificate as a root of trust. */
    /* Checking that cert is signed by CA. */

    X509* cacrt;
    X509* crt;

    BIO* crt_bio = BIO_new_mem_buf((void*)cert_pem, -1);
    crt = PEM_read_bio_X509(crt_bio, NULL, 0, NULL);
    assert(crt != NULL);

    BIO* cacrt_bio = BIO_new_mem_buf((void*)ca_cert_pem, -1);
    cacrt = PEM_read_bio_X509(cacrt_bio, NULL, 0, NULL);
    assert(cacrt != NULL);

    X509_STORE* s = X509_STORE_new();
    X509_STORE_add_cert(s, cacrt);
    X509_STORE_CTX* ctx = X509_STORE_CTX_new();
    X509_STORE_CTX_init(ctx, s, crt, NULL);
    int rc = X509_verify_cert(ctx);

    X509_STORE_CTX_free(ctx);
    X509_STORE_free(s);
    X509_free(crt);
    X509_free(cacrt);
    BIO_free(crt_bio);
    BIO_free(cacrt_bio);

    if(rc <= 0 ) {  // Error
        return false; // Fail
    }
    // Else success
    return true; /* 1 .. fail, 0 .. success */
}

