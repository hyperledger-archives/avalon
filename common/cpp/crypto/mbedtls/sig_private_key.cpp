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

/**
 * @file
 * Avalon ECDSA private key functions: generation, serialization, and signing.
 * Used for Secp256k1.
 *
 * Lower-level functions implemented using Mbed TLS.
 * See also sig_private_key_common.cpp for Mbed TLS-independent code.
 */

/*
 * Note on Private and Public Key Context for MBed TLS
 *
 * For MBed TLS, Avalon defines the context (private_key_ and public_key_)
 * as a pointer to mbedtls_ecdsa_context, defined in /usr/include/mbedtls/pk.h.
 *
 * mbedtls_ecp_keypair is the same as mbedtls_ecdsa_context
 * (from a typedef in mbedtls/ecdsa.h)
 *
 * The mbedtls_ecp_keypair structure contains three fields:
 * grp (the EC name (secp256k1 in our case) and base point),
 * d (secret key, a bignum), and
 * Q (public key, a point).
 *
 * Furthermore, function mbedtls_pk_ec() extracts a mbedtls_ecp_keypair*
 * pointer from a mbedtls_pk_context (which is MBed TLS's public key
 * certificate object, and is defined in mbedtls/pk.h).
 */

#include <stdlib.h>           // malloc(), free()
#include <string.h>           // memcpy()
#include <mbedtls/entropy.h>
#include <mbedtls/ctr_drbg.h>
#include <mbedtls/pk.h>
#include <mbedtls/md.h>       // MBEDTLS_MD_SHA256
#include <mbedtls/bignum.h>   // mbedtls_mpi_copy()
#include <mbedtls/ecp.h>
#include <mbedtls/ecdsa.h>

#include "crypto_shared.h"
#include "crypto_utils.h"     // RandomBitString()
#include "utils.h"            // ByteArrayToStr(), StrToByteArray()
#include "error.h"
#include "sig.h"
#include "sig_public_key.h"
#include "sig_private_key.h"

#ifndef CRYPTOLIB_MBEDTLS
#error "CRYPTOLIB_MBEDTLS must be defined to compile source with Mbed TLS."
#endif

namespace pcrypto = tcf::crypto;
namespace constants = tcf::crypto::constants;
namespace Error = tcf::error; // Error handling


/**
 * Utility function: copy ECDSA private key context.
 * The context is the keypair components (group G, bignum d, point Q).
 *
 * @param src The destination to copy the private key context.
 *            Must be previously initialized by mbedtls_ecdsa_init()
 * @param dst The private key context to copy
 * @returns 0 on success, Mbed TLS error code on error
 */
static int copy_ecdsa_private_key_context(
        mbedtls_ecdsa_context *dst, const mbedtls_ecdsa_context *src) {
    int rc;

    // Copy ECDSA context with keypair components (G, d, Q)
    rc = mbedtls_ecp_group_copy(&dst->grp, &src->grp);
    if (rc != 0) {
        return rc;
    }
    rc = mbedtls_mpi_copy(&dst->d, &src->d);
    if (rc != 0) {
        return rc;
    }
    rc = mbedtls_ecp_copy(&dst->Q, &src->Q);
    if (rc != 0) {
        return rc;
    }
}   // copy_ecdsa_private_key_context()


/**
 * Utility function: allocate and copy ECDSA private key context.
 * The context is the keypair components (group G, bignum d, point Q).
 *
 * Throws RuntimeError.
 *
 * @param ecdsa_ctx The private key context to copy
 * @returns An allocated copy of ecdsa_ctx.
 *          Must be ecdsa_free()'ed and free()ed.
 */
static mbedtls_ecdsa_context* duplicate_ecdsa_private_key_context(
        const mbedtls_ecdsa_context *ecdsa_ctx) {
    int rc;

    // Allocate ECDSA context
    mbedtls_ecdsa_context *new_ecdsa_ctx =
        (mbedtls_ecdsa_context *)malloc(sizeof (mbedtls_ecdsa_context));
    if (new_ecdsa_ctx == nullptr) {
        std::string msg(
            "Crypto Error (duplicate_ecdsa_private_key_context(): "
            "Could not allocate memory for ECDSA key context");
        throw Error::RuntimeError(msg);
    }
    mbedtls_ecdsa_init(new_ecdsa_ctx);

    // Copy ECDSA context with keypair components (G, d, Q)
    rc = copy_ecdsa_private_key_context(new_ecdsa_ctx, ecdsa_ctx);
    if (rc != 0) {
        mbedtls_ecdsa_free(new_ecdsa_ctx);
        free(new_ecdsa_ctx);
        std::string msg(
            "Crypto Error (duplicate_ecdsa_private_key_context(): "
            "Could not copy ECDSA key context");
        throw Error::RuntimeError(msg);
    }

    return new_ecdsa_ctx;
}   // duplicate_ecdsa_private_key_context()


/**
 * Utility function: deserialize ECDSA Private Key.
 *
 * For example,
 * -----BEGIN EC PRIVATE KEY-----
 * MIIBEwIBAQQgvIEpXzorm7Y6e0Pvzdt5hZicLG8k1+OMi0TSUbBZD0+ggaUwgaIC
 * AQEwLAYHKoZIzj0BAQIhAP////////////////////////////////////7///wv
 * MAYEAQAEAQcEQQR5vmZ++dy7rFWgYpXOhwsHApv82y3OKNlZ8oFbFvgXmEg62ncm
 * o8RlXaT7/A4RCKj9F7RIpoVUGZxH0I/7ENS4AiEA/////////////////////rqu
 * 3OavSKA7v9JejNA2QUECAQGhRANCAARxy5u39/yqw2tI98mVa4+KOnR4lAMPdFQr
 * uTiAZ2UMH+JrTyzGoChmP7hIrxHirYc7T0hTPbN3oVgWbfQEmXsv
 * -----END EC PRIVATE KEY-----
 *
 * Throws RuntimeError, ValueError.
 *
 * @param encoded Serialized ECDSA private key to deserialize
 * @returns deserialized ECDSA private key as a mbedtls_ecdsa_context* cast to void*
 */
void* pcrypto::sig::PrivateKey::deserializeECDSAPrivateKey(
        const std::string& encoded) {
    mbedtls_pk_context pk_ctx;
    int rc;

    // Sanity check
    if (encoded.size() == 0) {
        std::string msg(
            "Crypto Error (sig::PrivateKey::deserializeECDSAPrivateKey(): "
            "ECDSA private key PEM string is empty");
        throw Error::ValueError(msg);
    }

    mbedtls_pk_init(&pk_ctx);

    // Parse PEM string containing private key
    rc =  mbedtls_pk_parse_key(&pk_ctx, (const unsigned char *)encoded.c_str(),
        encoded.size() + 1, nullptr, 0);
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (sig::PrivateKey::deserializeECDSAPrivateKey(): "
            "Cannot parse ECDSA private key PEM string for serialization");
        throw Error::ValueError(msg);
    }

    // Extract ECDSA keypair
    mbedtls_ecp_keypair *ec_keypair = mbedtls_pk_ec(pk_ctx);

    // Sanity check private key
    if (mbedtls_pk_get_type(&pk_ctx) != MBEDTLS_PK_ECKEY) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (sig::PrivateKey::deserializeECDSAPrivateKey(): "
            "Private key in PEM string is not ECDSA");
        throw Error::ValueError(msg);
    }
    rc = mbedtls_ecp_check_privkey(&ec_keypair->grp, &ec_keypair->d);
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (sig::PrivateKey::deserializeECDSAPrivateKey(): "
            "Invalid ECDSA private key in PEM string");
        throw Error::ValueError(msg);
    }
    // Check public key component of private key
    rc = mbedtls_ecp_check_pubkey(&ec_keypair->grp, &ec_keypair->Q);
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (sig::PrivateKey::deserializeECDSAPrivateKey(): "
            "Invalid ECDSA public key in PEM string");
        throw Error::ValueError(msg);
    }

    // Allocate and copy ECDSA context
    mbedtls_ecdsa_context *ecdsa_ctx =
        duplicate_ecdsa_private_key_context(ec_keypair);
    if (ecdsa_ctx == nullptr) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (sig::PrivateKey::deserializeECDSAPrivateKey): "
            "Could not copy public key");
        throw Error::RuntimeError(msg);
    }

    mbedtls_pk_free(&pk_ctx);

    return (void *)ecdsa_ctx;
}  // pcrypto::sig::PrivateKey::deserializeECDSAPrivateKey


/**
 * Copy constructor.
 * Throws RuntimeError.
 *
 * @param privateKey ECDSA private key to copy. Created by Generate()
 */
pcrypto::sig::PrivateKey::PrivateKey(
        const pcrypto::sig::PrivateKey& privateKey) {
    // Allocate and copy ECDSA context
    private_key_ = (void *)duplicate_ecdsa_private_key_context(
        (mbedtls_ecdsa_context *)privateKey.private_key_);
    if (private_key_ == nullptr) {
        std::string msg("Crypto Error (sig::PrivateKey()): "
            "Could not copy private key");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::sig::PrivateKey::PrivateKey (copy constructor)


/**
 * PrivateKey Destructor.
 */
pcrypto::sig::PrivateKey::~PrivateKey() {
    if (private_key_ != nullptr) {
        mbedtls_ecdsa_free((mbedtls_ecdsa_context *)private_key_);
        free(private_key_);
        private_key_ = nullptr;
    }
}  // pcrypto::sig::PrivateKey::~PrivateKey


/**
 * Assignment operator = overload.
 * Throws RuntimeError.
 *
 * @param privateKey ECDSA private key to assign. Created by Generate()
 */
pcrypto::sig::PrivateKey& pcrypto::sig::PrivateKey::operator=(
    const pcrypto::sig::PrivateKey& privateKey) {
    if (this == &privateKey)
        return *this;

    if (private_key_ != nullptr) {
        mbedtls_ecdsa_free((mbedtls_ecdsa_context *)private_key_);
        free(private_key_);
        private_key_ = nullptr;
    }

    // Allocate and copy ECDSA context
    private_key_ = (void *)duplicate_ecdsa_private_key_context(
        (mbedtls_ecdsa_context *)privateKey.private_key_);
    if (private_key_ == nullptr) {
        std::string msg("Crypto Error (sig::PrivateKey operator =): "
            "Could not copy private key");
        throw Error::RuntimeError(msg);
    }

    return *this;
}  // pcrypto::sig::PrivateKey::operator =


/**
 * Deserialize ECDSA Private Key.
 *
 * For example,
 * -----BEGIN EC PRIVATE KEY-----
 * MIIBEwIBAQQgvIEpXzorm7Y6e0Pvzdt5hZicLG8k1+OMi0TSUbBZD0+ggaUwgaIC
 * AQEwLAYHKoZIzj0BAQIhAP////////////////////////////////////7///wv
 * MAYEAQAEAQcEQQR5vmZ++dy7rFWgYpXOhwsHApv82y3OKNlZ8oFbFvgXmEg62ncm
 * o8RlXaT7/A4RCKj9F7RIpoVUGZxH0I/7ENS4AiEA/////////////////////rqu
 * 3OavSKA7v9JejNA2QUECAQGhRANCAARxy5u39/yqw2tI98mVa4+KOnR4lAMPdFQr
 * uTiAZ2UMH+JrTyzGoChmP7hIrxHirYc7T0hTPbN3oVgWbfQEmXsv
 * -----END EC PRIVATE KEY-----
 *
 * Implemented with deserializeECDSAPrivateKey().
 * Throws RuntimeError, ValueError.
 *
 * @param encoded Serialized ECDSA private key generated by Serialize()
 *                to deserialize
 */
void pcrypto::sig::PrivateKey::Deserialize(const std::string& encoded) {
    mbedtls_ecdsa_context *key =
        (mbedtls_ecdsa_context *)deserializeECDSAPrivateKey(encoded);

    if (private_key_ != nullptr) {
        mbedtls_ecdsa_free((mbedtls_ecdsa_context *)private_key_);
        free(private_key_);
        private_key_ = nullptr;
    }

    private_key_ = (void *)key;
}  // pcrypto::sig::PrivateKey::Deserialize


/*
 * Wrapper function to generate a cryptographically strong random bit string.
 * Uses the interface expected by mbedtls_ecdsa_genkey()
 * That is, the same interface as mbedtls_ctr_drbg_random().
 * Implemented with RandomBitString().
 *
 * @param unused     Unused and ignored parameter for context. Set to nullptr
 * @param output     String containing raw binary plaintext
 * @param output_len Length of random bit string in bytes
 * @returns          0 on success
 *                   MBEDTLS_ERR_CTR_DRBG_REQUEST_TOO_BIG if output_len >1024
 *                   non-0 on other failures
 */
static int mbed_ctr_drbg_random_wrapper(void *unused,
        unsigned char *output, size_t output_len) {
    std::string s;

    // Sanity check
    if (output_len > MBEDTLS_CTR_DRBG_MAX_REQUEST)
        return MBEDTLS_ERR_CTR_DRBG_REQUEST_TOO_BIG;

    try {
        s = ByteArrayToStr(tcf::crypto::RandomBitString(output_len));
    } catch (const tcf::error::RuntimeError) {
        return 1; // failure
    }
    memcpy(output, s.data(), output_len);
    return 0; // success
}   // mbed_ctr_drbg_random_wrapper()


/**
 * Generate ECDSA private key.
 * Throws RuntimeError.
 */
void pcrypto::sig::PrivateKey::Generate() {
    int rc;

    // Allocate and initialize context
    mbedtls_ecdsa_context *ecdsa_ctx =
        (mbedtls_ecdsa_context *)malloc(sizeof (mbedtls_ecdsa_context));
    if (ecdsa_ctx == nullptr) {
        std::string msg(
            "Crypto Error (sig::PrivateKey::Generate(): "
            "Could not allocate memory for ECDSA key context");
        throw Error::RuntimeError(msg);
    }
    mbedtls_ecdsa_init(ecdsa_ctx);

    // Generate key
    rc = mbedtls_ecdsa_genkey(ecdsa_ctx, MBEDTLS_ECP_DP_SECP256K1,
        mbed_ctr_drbg_random_wrapper, nullptr);
    if (rc != 0) {
        mbedtls_ecdsa_free(ecdsa_ctx);
        free(ecdsa_ctx);
        std::string msg("Crypto Error (sig::PrivateKey::Generate): "
            "mbedtls_ecdsa_genkey() failed");
        throw Error::RuntimeError(msg);
    }

    // Free old context, if any, and set new context
    if (private_key_ != nullptr) {
        mbedtls_ecdsa_free((mbedtls_ecdsa_context *)private_key_);
        free(private_key_);
    }

    private_key_ = (void *)ecdsa_ctx;
}  // pcrypto::sig::PrivateKey::Generate


/**
 * Serialize ECDSA PrivateKey.
 *
 * For example,
 * -----BEGIN EC PRIVATE KEY-----
 * MIIBEwIBAQQgvIEpXzorm7Y6e0Pvzdt5hZicLG8k1+OMi0TSUbBZD0+ggaUwgaIC
 * AQEwLAYHKoZIzj0BAQIhAP////////////////////////////////////7///wv
 * MAYEAQAEAQcEQQR5vmZ++dy7rFWgYpXOhwsHApv82y3OKNlZ8oFbFvgXmEg62ncm
 * o8RlXaT7/A4RCKj9F7RIpoVUGZxH0I/7ENS4AiEA/////////////////////rqu
 * 3OavSKA7v9JejNA2QUECAQGhRANCAARxy5u39/yqw2tI98mVa4+KOnR4lAMPdFQr
 * uTiAZ2UMH+JrTyzGoChmP7hIrxHirYc7T0hTPbN3oVgWbfQEmXsv
 * -----END EC PRIVATE KEY-----
 *
 * Throws RuntimeError.
 *
 * @returns Serialized ECDSA private key as a string
 */
std::string pcrypto::sig::PrivateKey::Serialize() const {
    unsigned char pem_str[constants::MAX_PEM_LEN];
    mbedtls_pk_context pk_ctx;
    int rc;

    if (private_key_ == nullptr) {
        std::string msg(
            "Crypto Error (Serialize): PrivateKey is not initialized");
        throw Error::RuntimeError(msg);
    }

    // Create PK context from the ECDSA context (private_key_)
    mbedtls_pk_init(&pk_ctx);
    rc = mbedtls_pk_setup(&pk_ctx, mbedtls_pk_info_from_type(MBEDTLS_PK_ECKEY));
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (sig::PrivateKey::Serialize): "
            "mbedtls_pk_setup() failed");
        throw Error::RuntimeError(msg);
    }

    rc = copy_ecdsa_private_key_context(mbedtls_pk_ec(pk_ctx),
        (mbedtls_ecdsa_context *)private_key_);
    if (rc != 0) {
        std::string msg(
            "Crypto Error (sig::PrivateKey::Serialize(): "
            "Could not copy ECDSA key context");
        throw Error::RuntimeError(msg);
    }

    // Write NUL-terminated ECDSA private key PEM string
    // of the form "BEGIN EC PRIVATE KEY"
    rc = mbedtls_pk_write_key_pem(&pk_ctx, pem_str, constants::MAX_PEM_LEN);
    if (rc != 0) {
        std::string msg("Crypto Error (sig::PrivateKey::Serialize): "
            "Could not write key PEM string\n");
        throw Error::RuntimeError(msg);
    }

    // Cleanup and create return string
    mbedtls_pk_free(&pk_ctx);

    std::string str((char *)pem_str);
    return str;
}  // pcrypto::sig::PrivateKey::Serialize


/**
 * Signs hashMessage.data() with ECDSA privkey.
 * It's expected that caller of this function passes the
 * hash value of the original message to this function for signing.
 *
 * Sample DER-encoded signature in hexadecimal (71 bytes):
 * 30450221008e6b04abffea7dab1d2c6190619096262e567fa9f94be337953aab
 * 8742158d1c022034bd23799bc27308ce645191c43c16d5fb767e6cb5ab002442
 * 7194cbba59783c
 *
 * Throws RuntimeError.
 *
 * @param hashMessage Data in a byte array to sign; 32 bytes for SHA-256.
 *                    This is not the message to sign but a hash of the message
 * @returns ByteArray containing signature data in DER format
 *                    as defined in RFC 4492
 */
ByteArray pcrypto::sig::PrivateKey::SignMessage(
        const ByteArray& hashMessage) const {
    mbedtls_ecdsa_context ecdsa_ctx;
    int rc;
    unsigned char signature[constants::MAX_SIG_SIZE];
    size_t signature_len = 0;

    // Generate signature from hash and key
    rc = mbedtls_ecdsa_write_signature((mbedtls_ecdsa_context *)private_key_,
        MBEDTLS_MD_SHA256,
        (const unsigned char *)hashMessage.data(), hashMessage.size(),
        signature, &signature_len,
        mbed_ctr_drbg_random_wrapper, nullptr);
    if (rc != 0) {
        std::string msg("Crypto Error (sig::PrivateKey::SignMessage): "
            "Could not compute ECDSA signature");
        throw Error::RuntimeError(msg);
    }

    // Return signature
    return StrToByteArray(std::string((const char *)signature, signature_len));
}  // pcrypto::sig::PrivateKey::SignMessage
