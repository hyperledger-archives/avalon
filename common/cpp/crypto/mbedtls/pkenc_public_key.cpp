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
 * Avalon RSA public key serialization and encryption functions.
 * Serialization reads and writes keys in PEM format strings.
 *
 * Lower-level functions implemented using Mbed TLS.
 * See also pkenc_public_key_common.cpp for Mbed TLS-independent code.
 */

#include <stdlib.h>           // malloc(), free()
#include <string.h>           // memcpy()
#include <mbedtls/ctr_drbg.h>
#include <mbedtls/pk.h>
#include <mbedtls/md.h>       // MBEDTLS_MD_SHA256
#include <mbedtls/bignum.h>   // mbedtls_mpi_init()

#include "crypto_shared.h"
#include "crypto_utils.h"     // RandomBitString()
#include "utils.h"            // ByteArrayToStr()
#include "error.h"
#include "hex_string.h"
#include "pkenc.h"
#include "pkenc_private_key.h"
#include "pkenc_public_key.h"

#ifndef CRYPTOLIB_MBEDTLS
#error "CRYPTOLIB_MBEDTLS must be defined to compile source with Mbed TLS."
#endif

namespace pcrypto = tcf::crypto;
namespace constants = tcf::crypto::constants;
namespace Error = tcf::error; // Error handling


/**
 * Utility function: deserialize RSA Public Key.
 * That is, convert the key from a PEM format string
 * (with either "BEGIN RSA PUBLIC KEY" or "BEGIN PUBLIC KEY").
 *
 * Throws RuntimeError, ValueError.
 *
 * @param PEM encoded Serialized RSA public key to deserialize
 * @returns Allocated RSA context pointer of type mbedtls_rsa_context*
 *          containing key information.
 *          Must be mbedtls_pk_free()'ed and free()'ed.
 */
void* pcrypto::pkenc::PublicKey::deserializeRSAPublicKey(
        const std::string& encoded) {
    mbedtls_pk_context pk_ctx;
    int rc;

    // Sanity check
    if (encoded.size() == 0) {
        std::string msg(
            "Crypto Error (pkenc::PublicKey::deserializeRSAPublicKey(): "
            "RSA public key PEM string is empty");
        throw Error::ValueError(msg);
    }

    mbedtls_pk_init(&pk_ctx);

    // Parse PEM string containing public key
    rc =  mbedtls_pk_parse_public_key(&pk_ctx,
        (const unsigned char *)encoded.c_str(), encoded.size() + 1);
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (pkenc::PublicKey::deserializeRSAPublicKey(): "
            "Cannot parse RSA public key PEM string for serialization");
        throw Error::ValueError(msg);
    }

    // Sanity check if public key
    if (mbedtls_pk_get_type(&pk_ctx) != MBEDTLS_PK_RSA) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (pkenc::PublicKey::deserializeRSAPublicKey(): "
            "Public key in PEM string is not RSA");
        throw Error::ValueError(msg);
    }
    rc = mbedtls_rsa_check_pubkey(mbedtls_pk_rsa(pk_ctx));
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (pkenc::PublicKey::deserializeRSAPublicKey(): "
            "Invalid RSA public key in PEM string");
        throw Error::ValueError(msg);
    }

    // Allocate, copy, and return RSA context
    mbedtls_rsa_context *rsa_ctx =
        (mbedtls_rsa_context *)malloc(sizeof (mbedtls_rsa_context));
    if (rsa_ctx == nullptr) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (pkenc::PublicKey::deserializeRSAPublicKey(): "
            "Could not allocate memory for RSA key context");
        throw Error::RuntimeError(msg);
    }
    mbedtls_rsa_init(rsa_ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);
    rc = mbedtls_rsa_copy(rsa_ctx, mbedtls_pk_rsa(pk_ctx));
    if (rc != 0) {
        std::string msg("Crypto Error (pkenc::deserializeRSAPublicKey(): "
            "Could not copy private key");
        throw Error::RuntimeError(msg);
    }
    mbedtls_rsa_set_padding(rsa_ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);
    mbedtls_pk_free(&pk_ctx);

    return (void *)rsa_ctx;
}  // pcrypto::pkenc::PublicKey::deserializeRSAPublicKey


/**
 * PublicKey constructor from PrivateKey.
 * Extracts the public key portion from a RSA key pair.
 *
 * This is implemented by extracting the public key parts
 * from the private key context (modulus N and public exponent E),
 * then importing the public key (N, E) to a new public key context.
 * The private key components are not imported (that is,
 * primes P and Q (where N=P*Q), and private exponent D).
 *
 * @param privateKey Private key from which to derive a public key
 */
pcrypto::pkenc::PublicKey::PublicKey(
        const pcrypto::pkenc::PrivateKey& privateKey) {
    mbedtls_mpi N, E;
    mbedtls_rsa_context *rsa_ctx;
    int rc;

    // Allocate memory for public key context
    rsa_ctx = (mbedtls_rsa_context *)malloc(sizeof (mbedtls_rsa_context));
    if (rsa_ctx == nullptr) {
        std::string msg("Crypto Error (pkenc::PublicKey(): "
            "Could not allocate memory for RSA key context");
        throw Error::RuntimeError(msg);
    }

    // Extract N and E from private key
   mbedtls_mpi_init(&N);
   mbedtls_mpi_init(&E);
    rc = mbedtls_rsa_export((mbedtls_rsa_context *)privateKey.private_key_, &N,
        nullptr, nullptr, nullptr, &E);
    if (rc != 0) {
        mbedtls_mpi_free(&E);
        mbedtls_mpi_free(&N);
        mbedtls_rsa_free(rsa_ctx);
        free(rsa_ctx);
        std::string msg("Crypto Error (pkenc::PublicKey()): "
            "Could not export public key components from private key");
        throw Error::ValueError(msg);
    }

    // Build public key context from RSA public key (N and E)
    // and sanitized from private key information.
    mbedtls_rsa_init(rsa_ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);

    rc = mbedtls_rsa_import(rsa_ctx, &N, nullptr, nullptr, nullptr, &E);
    if (rc != 0) {
        mbedtls_mpi_free(&E);
        mbedtls_mpi_free(&N);
        mbedtls_rsa_free(rsa_ctx);
        free(rsa_ctx);
        std::string msg("Crypto Error (pkenc::PublicKey()): "
            "Could not import public key components from private key");
        throw Error::ValueError(msg);
    }
    mbedtls_rsa_set_padding(rsa_ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);

    // Fill in other RSA context components, if needed
    rc = mbedtls_rsa_complete(rsa_ctx);
    if (rc != 0) {
        mbedtls_mpi_free(&E);
        mbedtls_mpi_free(&N);
        mbedtls_rsa_free(rsa_ctx);
        free(rsa_ctx);
        std::string msg(
            "Crypto Error (pkenc::PublicKey(): "
            "cannot complete RSA public key context from private key");
        throw Error::RuntimeError(msg);
    }

    // Sanity check RSA public key
    rc = mbedtls_rsa_check_pubkey(rsa_ctx);
    if (rc != 0) {
        mbedtls_mpi_free(&E);
        mbedtls_mpi_free(&N);
        mbedtls_rsa_free(rsa_ctx);
        free(rsa_ctx);
        std::string msg(
            "Crypto Error (pkenc::PublicKey(): "
            "Invalid RSA public key imported from private key");
        throw Error::ValueError(msg);
    }

    // Cleanup
    mbedtls_mpi_free(&E);
    mbedtls_mpi_free(&N);

    // Set key
    public_key_ = (void *)rsa_ctx;
}  // pcrypto::pkenc::PublicKey::PublicKey


/**
 * PublicKey destructor.
 */
pcrypto::pkenc::PublicKey::~PublicKey() {
    if (public_key_ != nullptr) {
        mbedtls_rsa_free((mbedtls_rsa_context *)public_key_);
        free(public_key_);
        public_key_ = nullptr;
    }
}  // pcrypto::pkenc::Public::~PublicKey


/**
 * Copy constructor.
 * Throws RuntimeError.
 */
pcrypto::pkenc::PublicKey::PublicKey(
        const pcrypto::pkenc::PublicKey& publicKey) {
    mbedtls_rsa_context* rsa_ctx;
    int rc;

    rsa_ctx = (mbedtls_rsa_context *)malloc(sizeof (mbedtls_rsa_context));
    if (rsa_ctx == nullptr) {
        std::string msg("Crypto Error (pkenc::PublicKey() copy): "
            "Could not allocate public key");
        throw Error::RuntimeError(msg);
    }

    mbedtls_rsa_init(rsa_ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);
    rc = mbedtls_rsa_copy(rsa_ctx,
        (mbedtls_rsa_context *)publicKey.public_key_);
    if (rc != 0) {
        std::string msg("Crypto Error (pkenc::PublicKey() copy): "
            "Could not copy public key");
        throw Error::RuntimeError(msg);
    }
    mbedtls_rsa_set_padding(rsa_ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);

    public_key_ = (void *)rsa_ctx;
}  // pcrypto::pkenc::PublicKey::PublicKey (copy constructor)


/**
 * Assignment operator= overload.
 * Throws RuntimeError.
 */
pcrypto::pkenc::PublicKey& pcrypto::pkenc::PublicKey::operator=(
        const pcrypto::pkenc::PublicKey& publicKey) {
    mbedtls_rsa_context* rsa_ctx;
    int rc;

    if (this == &publicKey)
        return *this;

    // Allocate and copy context
    rsa_ctx = (mbedtls_rsa_context *)malloc(sizeof (mbedtls_rsa_context));
    if (rsa_ctx == nullptr) {
        std::string msg("Crypto Error (pkenc::PublicKey::operator=): "
            "Could not allocate public key");
        throw Error::RuntimeError(msg);
    }

    mbedtls_rsa_init(rsa_ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);
    rc = mbedtls_rsa_copy(rsa_ctx,
        (mbedtls_rsa_context *)publicKey.public_key_);
    if (rc != 0) {
        std::string msg("Crypto Error (pkenc::PublicKey::operator=): "
            "Could not copy public key");
        throw Error::RuntimeError(msg);
    }
    mbedtls_rsa_set_padding(rsa_ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);

    // Free old context, if any, and set new context
    if (public_key_ != nullptr) {
        mbedtls_rsa_free((mbedtls_rsa_context *)public_key_);
        free(public_key_);
    }

    public_key_ = (void *)rsa_ctx;
    return *this;
}  // pcrypto::pkenc::PublicKey::operator=


/**
 * Deserialize Public Key.
 * That is, convert the key from a PEM format string
 * (with either "BEGIN RSA PUBLIC KEY" or "BEGIN PUBLIC KEY").
 *
 * Implemented with deserializeRSAPublicKey().
 * Throws RuntimeError, ValueError.
 *
 * @param PEM encoded Serialized RSA public key to deserialize
 */
void pcrypto::pkenc::PublicKey::Deserialize(const std::string& encoded) {
    mbedtls_rsa_context* rsa_ctx =
        (mbedtls_rsa_context *)deserializeRSAPublicKey(encoded);

    // Free old context, if any, and set new context
    if (public_key_ != nullptr) {
        mbedtls_rsa_free((mbedtls_rsa_context *)public_key_);
        free(public_key_);
    }

    public_key_ = (void *)rsa_ctx;
}  // pcrypto::pkenc::PublicKey::Deserialize


/**
 * Serialize a RSA public key.
 * That is, convert the key to a PEM format string
 * (with "BEGIN PUBLIC KEY").
 * Throws RuntimeError.
 */
std::string pcrypto::pkenc::PublicKey::Serialize() const {
    static const unsigned int max_pem_len = 16000;
    unsigned char pem_str[max_pem_len];
    mbedtls_pk_context pk_ctx;
    int rc;

    if (public_key_ == nullptr) {
        std::string msg(
            "Crypto Error (Serialize): PublicKey is not initialized");
        throw Error::RuntimeError(msg);
    }

    // Create PK context from the RSA context (public_key_)
    mbedtls_pk_init(&pk_ctx);
    rc = mbedtls_pk_setup(&pk_ctx, mbedtls_pk_info_from_type(MBEDTLS_PK_RSA));
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (pkenc::PublicKey::Serialize): "
            "mbedtls_pk_setup() failed");
        throw Error::RuntimeError(msg);
    }
    mbedtls_rsa_copy(mbedtls_pk_rsa(pk_ctx),
        (mbedtls_rsa_context *)public_key_);

    rc = mbedtls_pk_write_pubkey_pem(&pk_ctx, pem_str, max_pem_len);
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg("Crypto Error (pkenc::PublicKey::Serialize): "
            "Could not write key PEM string\n");
        throw Error::RuntimeError(msg);
    }

    // Cleanup and create return string
    mbedtls_pk_free(&pk_ctx);

    std::string str((char *)pem_str);
    return str;
}  // pcrypto::pkenc::PublicKey::Serialize


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
 * Encrypt message with RSA public key and return ciphertext.
 * Uses PKCS1 OAEP padding.
 * Throws RuntimeError.
 *
 * @param message ByteArray containing raw binary plaintext
 * @returns ByteArray containing raw binary ciphertext
 */
ByteArray pcrypto::pkenc::PublicKey::EncryptMessage(const ByteArray& message)
        const {
    size_t key_byte_len =
        mbedtls_rsa_get_len((mbedtls_rsa_context *)public_key_);
    size_t max_plaintext_byte_len =
        ((key_byte_len * 8)  - constants::RSA_PADDING_SIZE) / 8;
    ByteArray ctext(key_byte_len);
    int rc;

    // Sanity checks
    if (message.size() == 0) {
        std::string msg(
            "Crypto Error (pkenc::PublicKey::EncryptMessage): "
            "RSA plaintext cannot be empty");
        throw Error::ValueError(msg);
    }
    if (message.size() > max_plaintext_byte_len) {
        std::string msg(
            "Crypto Error (pkenc::PublicKey::EncryptMessage): "
            "RSA plaintext size is too large");
        throw Error::ValueError(msg);
    }

    // Encrypt plaintext message
    rc =  mbedtls_rsa_rsaes_oaep_encrypt ((mbedtls_rsa_context *)public_key_,
        mbed_ctr_drbg_random_wrapper, nullptr,
        MBEDTLS_RSA_PUBLIC,
	nullptr, 0,
        message.size(), (const unsigned char *)message.data(),
        (unsigned char *)ctext.data());
    if (rc != 0) {
        std::string msg(
            "Crypto Error (pkenc::PublicKey::EncryptMessage): "
            "mbedtls_rsa_rsaes_oaep_encrypt() failed");
        throw Error::RuntimeError(msg);
    }

    return ctext;
}  // pcrypto::pkenc::PublicKey::EncryptMessage
