/* Copyright 2020 Intel Corporation
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

#include <string.h>
#include <mbedtls/x509_crt.h> // mbedtls_x509_crt_parse(), *_info()

#include "verify_certificate.h"

// Mbed TLS library sanity test
#if !defined(MBEDTLS_RSA_C) || !defined(MBEDTLS_X509_CRT_PARSE_C) || \
    !defined(MBEDTLS_FS_IO) || !defined(MBEDTLS_X509_CRL_PARSE_C)
#error "One of MBEDTLS_{RSA_C,X509_CRT_PARSE_C,_IO,X509_CRL_PARSE_C undefined."
#endif

#ifndef CRYPTOLIB_MBEDTLS
#error "CRYPTOLIB_MBEDTLS must be defined to compile source with Mbed TLS."
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

    int rc;
    mbedtls_x509_crt cert, ca_cert;
    uint32_t result_flags;

    // Parse CA cert and cert
    mbedtls_x509_crt_init(&ca_cert);
    rc = mbedtls_x509_crt_parse(&ca_cert, (const unsigned char *)ca_cert_pem,
        strlen(ca_cert_pem) + 1);
    if (rc != 0) {
        mbedtls_x509_crt_free(&ca_cert);
        return false;
    }

    mbedtls_x509_crt_init(&cert);
    rc = mbedtls_x509_crt_parse(&cert, (const unsigned char *)cert_pem,
        strlen(cert_pem) + 1);
    if (rc != 0) {
        mbedtls_x509_crt_free(&ca_cert);
        mbedtls_x509_crt_free(&cert);
        return false;
    }

    // Verify cert against CA cert
    rc = mbedtls_x509_crt_verify(&cert, &ca_cert, nullptr, nullptr,
        &result_flags, nullptr, nullptr);

    // Cleanup
    mbedtls_x509_crt_free(&ca_cert);
    mbedtls_x509_crt_free(&cert);

    return (rc == 0); // success
}
