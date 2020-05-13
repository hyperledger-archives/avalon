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
 * Avalon RSA public key generation, serialization, and decryption functions.
 */

#include <openssl/err.h>
#include <openssl/pem.h>
#include <memory>    // std::unique_ptr

#include "crypto_shared.h"
#include "error.h"
#include "hex_string.h"
#include "pkenc.h"
#include "pkenc_public_key.h"
#include "pkenc_private_key.h"

namespace pcrypto = tcf::crypto;
namespace constants = tcf::crypto::constants;

// Typedefs for memory management.
// Specify type and destroy function type for unique_ptr.
typedef std::unique_ptr<BIO, void (*)(BIO*)> BIO_ptr;
typedef std::unique_ptr<EVP_CIPHER_CTX, void (*)(EVP_CIPHER_CTX*)> CTX_ptr;
typedef std::unique_ptr<BN_CTX, void (*)(BN_CTX*)> BN_CTX_ptr;
typedef std::unique_ptr<BIGNUM, void (*)(BIGNUM*)> BIGNUM_ptr;
typedef std::unique_ptr<RSA, void (*)(RSA*)> RSA_ptr;

// Error handling.
namespace Error = tcf::error;


/**
 * Utility function: deserialize RSA Private Key.
 * Throws RuntimeError, ValueError.
 *
 * @param encoded Serialized RSA private key to deserialize
 */
RSA* deserializeRSAPrivateKey(const std::string& encoded) {
    BIO_ptr bio(BIO_new_mem_buf(encoded.c_str(), -1), BIO_free_all);
    if (!bio) {
        std::string msg(
            "Crypto Error (deserializeRSAPrivateKey): Could not create BIO");
        throw Error::RuntimeError(msg);
    }

    RSA* private_key = PEM_read_bio_RSAPrivateKey(bio.get(), NULL, NULL, NULL);
    if (!private_key) {
        std::string msg("Crypto Error (deserializeRSAPrivateKey): "
            "Could not deserialize private RSA key");
        throw Error::ValueError(msg);
    }
    return private_key;
}  // deserializeRSAPrivateKey


/**
 * Constructor from encoded string.
 * Throws RuntimeError, ValueError.
 *
 * @param encoded serialized RSA private key
 */
pcrypto::pkenc::PrivateKey::PrivateKey(const std::string& encoded) {
    private_key_ = deserializeRSAPrivateKey(encoded);
}  // pcrypto::pkenc::PrivateKey::PrivateKey


/**
 * Copy constructor.
 * Throws RuntimeError.
 */
pcrypto::pkenc::PrivateKey::PrivateKey(
        const pcrypto::pkenc::PrivateKey& privateKey) {
    private_key_ = RSAPrivateKey_dup(privateKey.private_key_);
    if (!private_key_) {
        std::string msg("Crypto Error (pkenc::PrivateKey() copy): "
            "Could not copy public key");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::pkenc::PrivateKey::PrivateKey (copy constructor)


/**
 * Move constructor.
 * Throws RuntimeError.
 */
pcrypto::pkenc::PrivateKey::PrivateKey(pcrypto::pkenc::PrivateKey&& privateKey) {
    private_key_ = privateKey.private_key_;
    privateKey.private_key_ = nullptr;
    if (!private_key_) {
        std::string msg("Crypto Error (pkenc::PrivateKey() move): "
            "Cannot move null private key");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::pkenc::PrivateKey::PrivateKey (move constructor)


/**
 * PrivateKey Destructor.
 */
pcrypto::pkenc::PrivateKey::~PrivateKey() {
    if (private_key_)
        RSA_free(private_key_);
}  // pcrypto::pkenc::Private::~PrivateKey


/**
 * Assignment operator = overload.
 * Throws RuntimeError.
 */
pcrypto::pkenc::PrivateKey& pcrypto::pkenc::PrivateKey::operator=(
    const pcrypto::pkenc::PrivateKey& privateKey) {
    if (this == &privateKey)
        return *this;
    if (private_key_)
        RSA_free(private_key_);
    private_key_ = RSAPrivateKey_dup(privateKey.private_key_);
    if (!private_key_) {
        std::string msg("Crypto Error (pkenc::PrivateKey::operator =): "
            "Could not copy private key");
        throw Error::RuntimeError(msg);
    }
    return *this;
}  // pcrypto::pkenc::PrivateKey::operator =


/**
 * Deserialize RSA Private Key.
 * Implemented using deserializeRSAPrivateKey().
 * Throws RunrimeError, ValueError.
 *
 * @param encoded Serialized RSA private key to deserialize
 */
void pcrypto::pkenc::PrivateKey::Deserialize(const std::string& encoded) {
    RSA* key = deserializeRSAPrivateKey(encoded);
    if (private_key_)
        RSA_free(private_key_);
    private_key_ = key;
}  // pcrypto::pkenc::PrivateKey::Deserialize


/**
 * Generate RSA private key.
 * Throws RuntimeError.
 */
void pcrypto::pkenc::PrivateKey::Generate() {
    if (private_key_)
        RSA_free(private_key_);

    unsigned long e = RSA_F4;
    BIGNUM_ptr exp(BN_new(), BN_free);
    private_key_ = nullptr;

    if (!exp) {
        std::string msg("Crypto  Error (pkenc::PrivateKey()): "
            "Could not create BIGNUM for RSA exponent");
        throw Error::RuntimeError(msg);
    }

    if (!BN_set_word(exp.get(), e)) {
        std::string msg("Crypto  Error (pkenc::PrivateKey()): "
            "Could not set RSA exponent");
        throw Error::RuntimeError(msg);
    }

    RSA_ptr private_key(RSA_new(), RSA_free);
    if (!private_key) {
        std::string msg("Crypto  Error (pkenc::PrivateKey()): "
            "Could not create new RSA key");
        throw Error::RuntimeError(msg);
    }
    if (!RSA_generate_key_ex(private_key.get(), constants::RSA_KEY_SIZE,
            exp.get(), NULL)) {
        std::string msg("Crypto  Error (pkenc::PrivateKey()): "
            "Could not generate RSA key");
        throw Error::RuntimeError(msg);
    }
    private_key_ = RSAPrivateKey_dup(private_key.get());
    if (!private_key_) {
        std::string msg("Crypto  Error (pkenc::PrivateKey()): "
            "Could not dup RSA private key");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::pkenc::PrivateKey::Generate


/**
 * Serialize a RSA private key.
 * Throws RunrimeError.
 */
std::string pcrypto::pkenc::PrivateKey::Serialize() const {
    if (private_key_ == nullptr) {
        std::string msg(
            "Crypto Error (Serialize): PrivateKey is not initialized");
        throw Error::RuntimeError(msg);
    }
    BIO_ptr bio(BIO_new(BIO_s_mem()), BIO_free_all);
    if (!bio) {
        std::string msg("Crypto Error (Serialize): Could not create BIO\n");
        throw Error::RuntimeError(msg);
    }

    int res = PEM_write_bio_RSAPrivateKey(bio.get(), private_key_,
        NULL, NULL, 0, 0, NULL);
    if (!res) {
        std::string msg("Crypto Error (Serialize): Could not write to BIO\n");
        throw Error::RuntimeError(msg);
    }
    int keylen = BIO_pending(bio.get());
    ByteArray pem_str(keylen + 1);

    res = BIO_read(bio.get(), pem_str.data(), keylen);
    if (!res) {
        std::string msg("Crypto Error (Serialize): Could not read BIO\n");
        throw Error::RuntimeError(msg);
    }
    pem_str[keylen] = '\0';
    std::string str(reinterpret_cast<char*>(pem_str.data()));

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
    char err[constants::ERR_BUF_LEN];
    int ptext_len;

    if (ciphertext.size() != (constants::RSA_KEY_SIZE >> 3)) {
        std::string msg(
            "Crypto Error (DecryptMessage): RSA ciphertext size is invalid");
        throw Error::ValueError(msg);
    }

    ByteArray ptext(RSA_size(private_key_));

    ptext_len = RSA_private_decrypt(ciphertext.size(), ciphertext.data(),
        ptext.data(), private_key_, constants::RSA_PADDING_SCHEME);

    if (ptext_len == -1) {
        std::string msg(
            "Crypto Error (DecryptMessage): RSA decryption internal error\n");
        ERR_load_crypto_strings();
        ERR_error_string(ERR_get_error(), err);
        msg += err;
        throw Error::RuntimeError(msg);
    }
    ptext.resize(ptext_len);
    return ptext;
}  // pcrypto::pkenc::PrivateKey::DecryptMessage


/**
 * Get Public encryption from PrivateKey.
 * Throws RuntimeError.
 */
pcrypto::pkenc::PublicKey pcrypto::pkenc::PrivateKey::GetPublicKey() const {
    PublicKey publicKey(*this);
    return publicKey;
}  // pcrypto::pkenc::GetPublicKey
