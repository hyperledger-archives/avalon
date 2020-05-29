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
 * Avalon RSA private key generation, serialization, and decryption functions.
 * Serialization reads and writes keys in PEM format strings.
 *
 * Lower-level functions implemented using Mbed TLS.
 * See also pkenc_private_key_common.cpp for Mbed TLS-independent code.
 */

#include <stdlib.h>           // malloc(), free()
#include <string.h>           // memcpy()
#include <mbedtls/entropy.h>
#include <mbedtls/ctr_drbg.h>
#include <mbedtls/pk.h>
#include <mbedtls/md.h>       // MBEDTLS_MD_SHA256

#include "crypto_shared.h"
#include "crypto_utils.h"     // RandomBitString()
#include "utils.h"            // ByteArrayToStr()
#include "error.h"
#include "hex_string.h"
#include "pkenc.h"
#include "pkenc_public_key.h"
#include "pkenc_private_key.h"

#ifndef CRYPTOLIB_MBEDTLS
#error "CRYPTOLIB_MBEDTLS must be defined to compile source with Mbed TLS."
#endif

namespace pcrypto = tcf::crypto;
namespace constants = tcf::crypto::constants;
namespace Error = tcf::error; // Error handling


/**
 * Utility function: deserialize RSA Private Key.
 * That is, convert the key from a PEM format string
 * (with "BEGIN RSA PRIVATE KEY").
 *
 * Throws RuntimeError, ValueError.
 *
 * @param PEM encoded Serialized RSA private key to deserialize
 * @returns Allocated RSA context pointer of type mbedtls_rsa_context*
 *          containing key information.
 *          Must be mbedtls_rsa_free()'ed and free()'ed.
 */
void* pcrypto::pkenc::PrivateKey::deserializeRSAPrivateKey(
        const std::string& encoded) {
    mbedtls_pk_context pk_ctx;
    int rc;

    // Sanity check
    if (encoded.size() == 0) {
        std::string msg(
            "Crypto Error (pkenc::PrivateKey::deserializeRSAPrivateKey(): "
            "RSA private key PEM string is empty");
        throw Error::ValueError(msg);
    }

    mbedtls_pk_init(&pk_ctx);

    // Parse PEM string containing private key
    rc =  mbedtls_pk_parse_key(&pk_ctx, (const unsigned char *)encoded.c_str(),
        encoded.size() + 1, nullptr, 0);
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (pkenc::PrivateKey::deserializeRSAPrivateKey(): "
            "Cannot parse RSA private key PEM string for serialization");
        throw Error::ValueError(msg);
    }

    // Sanity check private key
    if (mbedtls_pk_get_type(&pk_ctx) != MBEDTLS_PK_RSA) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (pkenc::PrivateKey::deserializeRSAPrivateKey(): "
            "Private key in PEM string is not RSA");
        throw Error::ValueError(msg);
    }
    rc = mbedtls_rsa_check_privkey(mbedtls_pk_rsa(pk_ctx));
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (pkenc::PrivateKey::deserializeRSAPrivateKey(): "
            "Invalid RSA private key in PEM string");
        throw Error::ValueError(msg);
    }

    // Allocate, copy, and return RSA context
    mbedtls_rsa_context *rsa_ctx =
        (mbedtls_rsa_context *)malloc(sizeof (mbedtls_rsa_context));
    if (rsa_ctx == nullptr) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (pkenc::PrivateKey::deserializeRSAPrivateKey(): "
            "Could not allocate memory for RSA key context");
        throw Error::RuntimeError(msg);
    }
    mbedtls_rsa_init(rsa_ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);
    rc = mbedtls_rsa_copy(rsa_ctx, mbedtls_pk_rsa(pk_ctx));
    if (rc != 0) {
        std::string msg(
            "Crypto Error (pkenc::PrivateKeydeserializeRSAPrivateKey()): "
            "Could not copy private key");
        throw Error::RuntimeError(msg);
    }
    mbedtls_rsa_set_padding(rsa_ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);
    mbedtls_pk_free(&pk_ctx);

    return (void *)rsa_ctx;
}  // deserializeRSAPrivateKey


/**
 * Copy constructor.
 * Throws RuntimeError.
 */
pcrypto::pkenc::PrivateKey::PrivateKey(
        const pcrypto::pkenc::PrivateKey& privateKey) {
    mbedtls_rsa_context* rsa_ctx;
    int rc;

    rsa_ctx = (mbedtls_rsa_context *)malloc(sizeof (mbedtls_rsa_context));
    if (rsa_ctx == nullptr) {
        std::string msg("Crypto Error (pkenc::PrivateKey() copy): "
            "Could not allocate private key");
        throw Error::RuntimeError(msg);
    }

    mbedtls_rsa_init(rsa_ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);
    rc = mbedtls_rsa_copy(rsa_ctx,
        (mbedtls_rsa_context *)privateKey.private_key_);
    if (rc != 0) {
        std::string msg("Crypto Error (pkenc::PrivateKey() copy): "
            "Could not copy private key");
        throw Error::RuntimeError(msg);
    }
    mbedtls_rsa_set_padding(rsa_ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);
    private_key_ = (void *)rsa_ctx;
}  // pcrypto::pkenc::PrivateKey::PrivateKey (copy constructor)


/**
 * PrivateKey Destructor.
 */
pcrypto::pkenc::PrivateKey::~PrivateKey() {
    if (private_key_ != nullptr) {
        mbedtls_rsa_free((mbedtls_rsa_context *)private_key_);
        free(private_key_);
        private_key_ = nullptr;
    }
}  // pcrypto::pkenc::Private::~PrivateKey


/**
 * Assignment operator= overload.
 * Throws RuntimeError.
 */
pcrypto::pkenc::PrivateKey& pcrypto::pkenc::PrivateKey::operator=(
        const pcrypto::pkenc::PrivateKey& privateKey) {
    mbedtls_rsa_context* rsa_ctx;
    int rc;

    if (this == &privateKey)
        return *this;

    // Allocate and copy context
    rsa_ctx = (mbedtls_rsa_context *)malloc(sizeof (mbedtls_rsa_context));
    if (rsa_ctx == nullptr) {
        std::string msg("Crypto Error (pkenc::PrivateKey::operator=): "
            "Could not allocate private key");
        throw Error::RuntimeError(msg);
    }

    mbedtls_rsa_init(rsa_ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);
    rc = mbedtls_rsa_copy(rsa_ctx,
        (mbedtls_rsa_context *)privateKey.private_key_);
    if (rc != 0) {
        std::string msg("Crypto Error (pkenc::PrivateKey::operator=): "
            "Could not copy private key");
        throw Error::RuntimeError(msg);
    }
    mbedtls_rsa_set_padding(rsa_ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);

    // Free old context, if any, and set new context
    if (private_key_ != nullptr) {
        mbedtls_rsa_free((mbedtls_rsa_context *)private_key_);
        free(private_key_);
    }

    private_key_ = (void *)rsa_ctx;
    return *this;
}  // pcrypto::pkenc::PrivateKey::operator=


/**
 * Deserialize RSA Private Key.
 * That is, convert the key from a PEM format string
 * (with "BEGIN RSA PRIVATE KEY").
 *
 * Implemented using deserializeRSAPrivateKey().
 * Throws RuntimeError, ValueError.
 *
 * @param PEM encoded Serialized RSA private key to deserialize
 */
void pcrypto::pkenc::PrivateKey::Deserialize(const std::string& encoded) {
    mbedtls_rsa_context* rsa_ctx =
        (mbedtls_rsa_context *)deserializeRSAPrivateKey(encoded);

    // Free old context, if any, and set new context
    if (private_key_ != nullptr) {
        mbedtls_rsa_free((mbedtls_rsa_context *)private_key_);
        free(private_key_);
    }

    private_key_ = (void *)rsa_ctx;
}  // pcrypto::pkenc::PrivateKey::Deserialize


/*
 * Wrapper function to generate a cryptographically strong random bit string.
 * Uses the interface expected by mbedtls_rsa_gen_key() and
 * mbedtls_rsa_rsaes_oaep_decrypt(). That is, the same interface as
 * mbedtls_ctr_drbg_random().
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
}


/**
 * Generate RSA private key.
 * Throws RuntimeError.
 */
void pcrypto::pkenc::PrivateKey::Generate() {
    mbedtls_pk_context pk_ctx;
    int rc;

    // RSA key setup
    mbedtls_pk_init(&pk_ctx);
    rc = mbedtls_pk_setup(&pk_ctx, mbedtls_pk_info_from_type(MBEDTLS_PK_RSA));
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg("Crypto Error (pkenc::PrivateKey::Generate): "
            "mbedtls_pk_setup() failed");
        throw Error::RuntimeError(msg);
    }

    if (constants::RSA_KEY_SIZE > MBEDTLS_MPI_MAX_BITS) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg("Crypto Error (pkenc::PrivateKey::Generate): "
            "RSA key size is larger than what is supported by Mbed TLS");
        throw Error::RuntimeError(msg);
    }

    // Generate key
    rc = mbedtls_rsa_gen_key(mbedtls_pk_rsa(pk_ctx),
        mbed_ctr_drbg_random_wrapper, nullptr,
        constants::RSA_KEY_SIZE, 0x10001);
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg("Crypto Error (pkenc::PrivateKey::Generate): "
            "mbedtls_rsa_gen_key() failed");
        throw Error::RuntimeError(msg);
    }

    // Allocate and copy context
    mbedtls_rsa_context *rsa_ctx =
        (mbedtls_rsa_context *)malloc(sizeof (mbedtls_rsa_context));
    if (rsa_ctx == nullptr) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (pkenc::PrivateKey::Generate(): "
            "Could not allocate memory for RSA key context");
        throw Error::RuntimeError(msg);
    }
    mbedtls_rsa_init(rsa_ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);
    rc = mbedtls_rsa_copy(rsa_ctx, mbedtls_pk_rsa(pk_ctx));
    if (rc != 0) {
        std::string msg("Crypto Error (pkenc::PrivateKey::Generate()): "
            "Could not copy private key");
        throw Error::RuntimeError(msg);
    }
    mbedtls_rsa_set_padding(rsa_ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);
    mbedtls_pk_free(&pk_ctx);

    // Free old context, if any, and set new context
    if (private_key_ != nullptr) {
        mbedtls_rsa_free((mbedtls_rsa_context *)private_key_);
        free(private_key_);
    }

    private_key_ = (void *)rsa_ctx;
}  // pcrypto::pkenc::PrivateKey::Generate


/**
 * Serialize a RSA private key.
 * That is convert the key to a PEM format string
 * (with "BEGIN RSA PRIVATE KEY").
 * Throws RuntimeError.
 */
std::string pcrypto::pkenc::PrivateKey::Serialize() const {
    static const unsigned int max_pem_len = 16000;
    unsigned char pem_str[max_pem_len];
    mbedtls_pk_context pk_ctx;
    int rc;

    if (private_key_ == nullptr) {
        std::string msg(
            "Crypto Error (Serialize): PrivateKey is not initialized");
        throw Error::RuntimeError(msg);
    }

    // Create PK context from the RSA context (private_key_)
    mbedtls_pk_init(&pk_ctx);
    rc = mbedtls_pk_setup(&pk_ctx, mbedtls_pk_info_from_type(MBEDTLS_PK_RSA));
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (pkenc::PrivateKey::Serialize): "
            "mbedtls_pk_setup() failed");
        throw Error::RuntimeError(msg);
    }
    mbedtls_rsa_copy(mbedtls_pk_rsa(pk_ctx),
        (mbedtls_rsa_context *)private_key_);

    // Write NUL-terminated RSA private key PEM string
    // of the form "BEGIN RSA PRIVATE KEY"
    rc = mbedtls_pk_write_key_pem(&pk_ctx, pem_str, max_pem_len);
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg("Crypto Error (pkenc::PrivateKey::Serialize): "
            "Could not write key PEM string\n");
        throw Error::RuntimeError(msg);
    }

    // Cleanup and create return string
    mbedtls_pk_free(&pk_ctx);

    std::string str((char *)pem_str);
    return str;
}  // pcrypto::pkenc::PrivateKey::Serialize


/**
 * Decrypt message with RSA private key and return plaintext.
 * Uses PKCS1 OAEP padding.
 * Throws RuntimeError.
 *
 * @param ciphertext string contains raw binary ciphertext
 * @returns ByteArray containing raw binary plaintext
 */
ByteArray pcrypto::pkenc::PrivateKey::DecryptMessage(
        const ByteArray& ciphertext) const {
    size_t key_byte_len =
        mbedtls_rsa_get_len((mbedtls_rsa_context *)private_key_);
    size_t ptext_byte_len = 0;
    int rc;

    // Sanity checks
    if (ciphertext.size() == 0) {
        std::string msg(
            "Crypto Error (DecryptMessage): RSA ciphertext cannot be empty");
        throw Error::ValueError(msg);
    }
    if (ciphertext.size() != (key_byte_len)) {
        std::string msg("Crypto Error (DecryptMessage): "
            "RSA ciphertext length must match key length");
        throw Error::ValueError(msg);
    }

    // Decrypt ciphertext
    ByteArray ptext(key_byte_len);

    rc =  mbedtls_rsa_rsaes_oaep_decrypt ((mbedtls_rsa_context *)private_key_,
        nullptr, nullptr, MBEDTLS_RSA_PRIVATE,
	nullptr, 0,
        &ptext_byte_len,
        (const unsigned char *)ciphertext.data(),
        (unsigned char *)ptext.data(),
        key_byte_len);
    if (rc != 0) {
        std::string msg(
            "Crypto Error (pkenc::PrivateKey::DecryptMessage): "
            "mbedtls_rsa_rsaes_oaep_decrypt() failed");
        throw Error::RuntimeError(msg);
    }

    // Verify decrypted ptext_byte_len
    if (ptext_byte_len > key_byte_len) {
        std::string msg(
            "Crypto Error (pkenc::PrivateKey::DecryptMessage(): "
            "Invalid decrypted plaintext output length "
            "exceeds key length");
        throw Error::ValueError(msg);
    }

    ptext.resize(ptext_byte_len);
    return ptext;
}  // pcrypto::pkenc::PrivateKey::DecryptMessage
