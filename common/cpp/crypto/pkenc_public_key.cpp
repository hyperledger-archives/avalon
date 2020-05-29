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

/**
 * @file
 * Avalon RSA public key serialization and encryption functions.
 * Serialization reads and writes keys in PEM format strings.
 *
 * Lower-level functions implemented using OpenSSL.
 * See also pkenc_public_key_common.cpp for OpenSSL-independent code.
 */

#include <openssl/err.h>
#include <openssl/pem.h>
#include <memory>    // std::unique_ptr

#include "crypto_shared.h"
#include "error.h"
#include "hex_string.h"
#include "pkenc.h"
#include "pkenc_private_key.h"
#include "pkenc_public_key.h"

#ifndef CRYPTOLIB_OPENSSL
#error "CRYPTOLIB_OPENSSL must be defined to compile source with OpenSSL."
#endif

namespace pcrypto = tcf::crypto;
namespace constants = tcf::crypto::constants;

// Typedefs for memory management.
// Specify type and destroy function type for unique_ptr.
typedef std::unique_ptr<BIO, void (*)(BIO*)> BIO_ptr;
typedef std::unique_ptr<EVP_CIPHER_CTX, void (*)(EVP_CIPHER_CTX*)> CTX_ptr;
typedef std::unique_ptr<BN_CTX, void (*)(BN_CTX*)> BN_CTX_ptr;
typedef std::unique_ptr<BIGNUM, void (*)(BIGNUM*)> BIGNUM_ptr;
typedef std::unique_ptr<RSA, void (*)(RSA*)> RSA_ptr;

// Error handling
namespace Error = tcf::error;


/**
 * Utility function: deserialize RSA Public Key.
 * That is, convert the key from a PEM format string
 * (with either "BEGIN RSA PUBLIC KEY" or "BEGIN PUBLIC KEY").
 *
 * Throws RuntimeError, ValueError.
 *
 * @param encoded  PEM encoded Serialized RSA public key to deserialize
 * @returns Allocated RSA context containing key information.
 *          Must be RSA_free()'ed.
 */
void *pcrypto::pkenc::PublicKey::deserializeRSAPublicKey(
        const std::string& encoded) {
    RSA *public_key;

    // Sanity check
    if (encoded.size() == 0) {
        std::string msg(
            "Crypto Error (pkenc::PublicKey::deserializeRSAPublicKey(): "
            "RSA public key PEM string is empty");
        throw Error::ValueError(msg);
    }

    BIO_ptr bio(BIO_new_mem_buf(encoded.c_str(), -1), BIO_free_all);
    if (bio == nullptr) {
        std::string msg(
            "Crypto Error (pkenc::PublicKey::deserializeRSAPublicKey): "
            "Could not create BIO");
        throw Error::RuntimeError(msg);
    }

    // Reads RSA public key PEM string.
    // First attempt read of PEM with BEGIN PUBLIC KEY
    public_key = PEM_read_bio_RSA_PUBKEY(bio.get(),
        nullptr, nullptr, nullptr);
    if (public_key == nullptr) {
        // If that fails, next attempt to read PEM with BEGIN RSA PUBLIC KEY
        BIO_ptr bio2(BIO_new_mem_buf(encoded.c_str(), -1), BIO_free_all);
        if (bio == nullptr) {
            std::string msg(
                "Crypto Error (pkenc::PublicKey::deserializeRSAPublicKey): "
                "Could not create BIO");
            throw Error::RuntimeError(msg);
        }
        public_key = PEM_read_bio_RSAPublicKey(bio2.get(),
            nullptr, nullptr, nullptr);
        if (public_key == nullptr) {
            std::string msg(
                "Crypto Error (pkenc::PublicKey::deserializeRSAPublicKey): "
                "Could not deserialize public RSA key");
            throw Error::ValueError(msg);
        }
    }
    return public_key;
}  // pcrypto::pkenc::PublicKey::deserializeRSAPublicKey


/**
 * PublicKey constructor from PrivateKey.
 * Extracts the public key portion from a RSA key pair.
 *
 * @param privateKey Private key from which to derive a public key
 */
pcrypto::pkenc::PublicKey::PublicKey(
        const pcrypto::pkenc::PrivateKey& privateKey) {
    public_key_ = (void *)RSAPublicKey_dup((RSA *)privateKey.private_key_);
    if (public_key_ == nullptr) {
        std::string msg("Crypto  Error (pkenc::PublicKey()): "
            "Could not duplicate RSA public key");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::pkenc::PublicKey::PublicKey



/**
 * PublicKey destructor.
 */
pcrypto::pkenc::PublicKey::~PublicKey() {
    if (public_key_ != nullptr) {
        RSA_free((RSA *)public_key_);
        public_key_ = nullptr;
    }
}  // pcrypto::pkenc::Public::~PublicKey


/**
 * Copy constructor.
 * Throws RuntimeError.
 */
pcrypto::pkenc::PublicKey::PublicKey(
        const pcrypto::pkenc::PublicKey& publicKey) {
    public_key_ = (void *)RSAPublicKey_dup((RSA *)publicKey.public_key_);
    if (public_key_ == nullptr) {
        std::string msg("Crypto Error (pkenc::PublicKey() copy): "
            "Could not copy public key");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::pkenc::PublicKey::PublicKey (copy constructor)


/**
 * Assignment operator = overload.
 * Throws RuntimeError.
 */
pcrypto::pkenc::PublicKey& pcrypto::pkenc::PublicKey::operator=(
        const pcrypto::pkenc::PublicKey& publicKey) {
    if (this == &publicKey)
        return *this;
    if (public_key_ != nullptr)
        RSA_free((RSA *)public_key_);
    public_key_ = (void *)RSAPublicKey_dup((RSA *)publicKey.public_key_);
    if (public_key_ == nullptr) {
        std::string msg("Crypto Error (pkenc::PublicKey::operator =): "
            "Could not copy public key");
        throw Error::RuntimeError(msg);
    }
    return *this;
}  // pcrypto::pkenc::PublicKey::operator =


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
    RSA* key = (RSA *)deserializeRSAPublicKey(encoded);
    if (public_key_ != nullptr)
        RSA_free((RSA *)public_key_);
    public_key_ = (void *)key;
}  // pcrypto::pkenc::PublicKey::Deserialize


/**
 * Serialize a RSA public key.
 * That is, convert the key to a PEM format string
 * (with "BEGIN PUBLIC KEY").
 * Throws RuntimeError.
 */
std::string pcrypto::pkenc::PublicKey::Serialize() const {
    if (public_key_ == nullptr) {
        std::string msg(
            "Crypto Error (pkenc::PublicKey::Serialize): "
            "PublicKey is not initialized");
        throw Error::RuntimeError(msg);
    }

    BIO_ptr bio(BIO_new(BIO_s_mem()), BIO_free_all);
    if (bio == nullptr) {
        std::string msg("Crypto Error (pkenc::PublicKey::Serialize): "
            "Could not create BIO");
        throw Error::RuntimeError(msg);
    }

    // This writes a RSA public key PEM string of the form "BEGIN PUBLIC KEY"
    int res = PEM_write_bio_RSA_PUBKEY(bio.get(), (RSA *)public_key_);
    if (res == 0) {
        std::string msg("Crypto Error (pkenc::PublicKey::Serialize): "
            "Could not write public key");
        throw Error::RuntimeError(msg);
    }

    int keylen = BIO_pending(bio.get());
    ByteArray pem_str(keylen + 1);

    res = BIO_read(bio.get(), pem_str.data(), keylen);
    if (res == 0) {
        std::string msg("Crypto Error (pkenc::PublicKey::Serialize): "
            "Could not read BIO");
        throw Error::RuntimeError(msg);
    }

    pem_str[keylen] = '\0';
    std::string str(reinterpret_cast<char*>(pem_str.data()));
    return str;
}  // pcrypto::pkenc::PublicKey::Serialize


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
    char err[constants::ERR_BUF_LEN];
    int ctext_len;

    // Sanity checks
    if (message.size() == 0) {
        std::string msg(
            "Crypto Error (pkenc::PublicKey::EncryptMessage): "
            "RSA plaintext cannot be empty");
        throw Error::ValueError(msg);
    }
    if (message.size() > constants::RSA_PLAINTEXT_LEN) {
        std::string msg(
            "Crypto Error (pkenc::PublicKey::EncryptMessage): "
            "RSA plaintext size is too large");
        throw Error::ValueError(msg);
    }

    ByteArray ctext(RSA_size((RSA *)public_key_));
    ctext_len = RSA_public_encrypt(message.size(), message.data(),
        ctext.data(), (RSA *)public_key_, constants::RSA_PADDING_SCHEME);

    if (ctext_len == -1) {
        std::string msg("Crypto Error (pkenc::PublicKey::EncryptMessage): "
            "RSA encryption internal error.\n");
        ERR_load_crypto_strings();
        ERR_error_string(ERR_get_error(), err);
        msg += err;
        throw Error::RuntimeError(msg);
    }

    return ctext;
}  // pcrypto::pkenc::PublicKey::EncryptMessage
