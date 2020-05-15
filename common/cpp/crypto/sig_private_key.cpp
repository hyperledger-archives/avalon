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
 * Avalon ECDSA private key functions: generation, serialization, and signing.
 * Used for Secp256k1.
 */

#include <openssl/pem.h>
#include <openssl/ecdsa.h>
#include <memory>    // std::unique_ptr

#include "crypto_shared.h"
#include "error.h"
#include "hex_string.h"
#include "sig.h"
#include "sig_public_key.h"
#include "sig_private_key.h"

namespace pcrypto = tcf::crypto;
namespace constants = tcf::crypto::constants;

// Typedefs for memory management.
// Specify type and destroy function type for unique_ptr
typedef std::unique_ptr<BIO, void (*)(BIO*)> BIO_ptr;
typedef std::unique_ptr<EVP_CIPHER_CTX, void (*)(EVP_CIPHER_CTX*)> CTX_ptr;
typedef std::unique_ptr<BN_CTX, void (*)(BN_CTX*)> BN_CTX_ptr;
typedef std::unique_ptr<BIGNUM, void (*)(BIGNUM*)> BIGNUM_ptr;
typedef std::unique_ptr<EC_GROUP, void (*)(EC_GROUP*)> EC_GROUP_ptr;
typedef std::unique_ptr<EC_POINT, void (*)(EC_POINT*)> EC_POINT_ptr;
typedef std::unique_ptr<EC_KEY, void (*)(EC_KEY*)> EC_KEY_ptr;
typedef std::unique_ptr<ECDSA_SIG, void (*)(ECDSA_SIG*)> ECDSA_SIG_ptr;
// Error handling
namespace Error = tcf::error;

#if OPENSSL_API_COMPAT < 0x10100000L
extern void ECDSA_SIG_get0(const ECDSA_SIG *sig, const BIGNUM **ptr_r,
        const BIGNUM **ptr_s);
extern int ECDSA_SIG_set0(ECDSA_SIG *sig, BIGNUM *r, BIGNUM *s);
#endif


/**
 * Utility function: Deserialize ECDSA Private Key.
 * Throws RuntimeError, ValueError.
 *
 * @param encoded Serialized ECDSA private key to deserialize
 * @returns deserialized ECDSA private key
 */
EC_KEY* deserializeECDSAPrivateKey(const std::string& encoded) {
    BIO_ptr bio(BIO_new_mem_buf(encoded.c_str(), -1), BIO_free_all);
    if (!bio) {
        std::string msg(
            "Crypto Error (deserializeECDSAPrivateKey): Could not create BIO");
        throw Error::RuntimeError(msg);
    }

    EC_KEY* private_key = PEM_read_bio_ECPrivateKey(bio.get(),
        nullptr, nullptr, nullptr);
    if (!private_key) {
        std::string msg(
            "Crypto Error (deserializeECDSAPrivateKey): Could not "
            "deserialize private ECDSA key");
        throw Error::ValueError(msg);
    }
    return private_key;
}  // deserializeECDSAPrivateKey


/**
 * Constructor from encoded string.
 * Throws RuntimeError, ValueError.
 *
 * @param encoded ECDSA private key string created by Generate()
 */
pcrypto::sig::PrivateKey::PrivateKey(const std::string& encoded) {
    private_key_ = deserializeECDSAPrivateKey(encoded);
}  // pcrypto::sig::PrivateKey::PrivateKey


/**
 * Copy constructor.
 * Throws RuntimeError.
 *
 * @param privateKey ECDSA private key to copy. Created by Generate()
 */
pcrypto::sig::PrivateKey::PrivateKey(
        const pcrypto::sig::PrivateKey& privateKey) {
    private_key_ = EC_KEY_dup(privateKey.private_key_);
    if (!private_key_) {
        std::string msg("Crypto Error (sig::PrivateKey() copy): "
            "Could not copy private key");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::sig::PrivateKey::PrivateKey (copy constructor)


/**
 * Move constructor.
 * Throws RuntimeError.
 *
 * @param privateKey ECDSA private key to move. Created by Generate()
 */
pcrypto::sig::PrivateKey::PrivateKey(pcrypto::sig::PrivateKey&& privateKey) {
    private_key_ = privateKey.private_key_;
    privateKey.private_key_ = nullptr;
    if (!private_key_) {
        std::string msg("Crypto Error (sig::PrivateKey() move): "
            "Cannot move null private key");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::sig::PrivateKey::PrivateKey (move constructor)


/**
 * PrivateKey Destructor.
 */
pcrypto::sig::PrivateKey::~PrivateKey() {
    if (private_key_)
        EC_KEY_free(private_key_);
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
    if (private_key_)
        EC_KEY_free(private_key_);
    private_key_ = EC_KEY_dup(privateKey.private_key_);
    if (!private_key_) {
        std::string msg("Crypto Error (sig::PrivateKey operator =): "
            "Could not copy private key");
        throw Error::RuntimeError(msg);
    }
    return *this;
}  // pcrypto::sig::PrivateKey::operator =


/**
 * Deserialize ECDSA Private Key.
 * Implemented with deserializeECDSAPrivateKey().
 * Throws RuntimeError, ValueError.
 *
 * @param encoded Serialized ECDSA private key generated by Serialize()
 *                to deserialize
 */
void pcrypto::sig::PrivateKey::Deserialize(const std::string& encoded) {
    EC_KEY* key = deserializeECDSAPrivateKey(encoded);
    if (private_key_)
        EC_KEY_free(private_key_);
    private_key_ = key;
}  // pcrypto::sig::PrivateKey::Deserialize


/**
 * Generate ECDSA private key.
 * Throws RuntimeError.
 */
void pcrypto::sig::PrivateKey::Generate() {
    if (private_key_)
        EC_KEY_free(private_key_);

    EC_KEY_ptr private_key(EC_KEY_new(), EC_KEY_free);

    if (!private_key) {
        std::string msg(
            "Crypto Error (sig::PrivateKey()): Could not create new EC_KEY");
        throw Error::RuntimeError(msg);
    }

    EC_GROUP_ptr ec_group(EC_GROUP_new_by_curve_name(constants::CURVE),
        EC_GROUP_clear_free);
    if (!ec_group) {
        std::string msg(
            "Crypto Error (sig::PrivateKey()): Could not create EC_GROUP");
        throw Error::RuntimeError(msg);
    }

    if (!EC_KEY_set_group(private_key.get(), ec_group.get())) {
        std::string msg(
            "Crypto Error (sig::PrivateKey()): Could not set EC_GROUP");
        throw Error::RuntimeError(msg);
    }

    if (!EC_KEY_generate_key(private_key.get())) {
        std::string msg(
            "Crypto Error (sig::PrivateKey()): Could not generate EC_KEY");
        throw Error::RuntimeError(msg);
    }

    private_key_ = EC_KEY_dup(private_key.get());
    if (!private_key_) {
        std::string msg(
            "Crypto Error (sig::PrivateKey()): Could not dup private EC_KEY");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::sig::PrivateKey::Generate


/**
 * Derive Digital Signature public key from private key.
 * Throws RuntimeError.
 */
pcrypto::sig::PublicKey pcrypto::sig::PrivateKey::GetPublicKey() const {
    PublicKey publicKey(*this);
    return publicKey;
}  // pcrypto::sig::GetPublicKey()


/**
 * Serialize ECDSA PrivateKey.
 * Throws RuntimeError.
 *
 * @returns Serialized ECDSA private key as a string
 */
std::string pcrypto::sig::PrivateKey::Serialize() const {
    BIO_ptr bio(BIO_new(BIO_s_mem()), BIO_free_all);

    if (!bio) {
        std::string msg("Crypto Error (Serialize): Could not create BIO");
        throw Error::RuntimeError(msg);
    }

    PEM_write_bio_ECPrivateKey(bio.get(), private_key_,
        nullptr, nullptr, 0, 0, nullptr);

    int keylen = BIO_pending(bio.get());

    ByteArray pem_str(keylen + 1);
    if (!BIO_read(bio.get(), pem_str.data(), keylen)) {
        std::string msg("Crypto Error (Serialize): Could not read BIO");
        throw Error::RuntimeError(msg);
    }
    pem_str[keylen] = '\0';
    std::string str((char*)(pem_str.data()));

    return str;
}  // pcrypto::sig::PrivateKey::Serialize


/**
 * Signs hashMessage.data() with ECDSA privkey.
 * It's expected that caller of this function passes the
 * hash value of the original message to this function for signing.
 * Throws RuntimeError.
 *
 * @param hashMessage Data in a byte array to sign
 * @returns ByteArray containing raw binary signature data
 */
ByteArray pcrypto::sig::PrivateKey::SignMessage(
    const ByteArray& hashMessage) const {
    // Sign
    ECDSA_SIG_ptr sig(ECDSA_do_sign((const unsigned char*)hashMessage.data(),
        hashMessage.size(), private_key_),
        ECDSA_SIG_free);
    if (!sig) {
        std::string msg(
            "Crypto Error (SignMessage): Could not compute ECDSA signature");
        throw Error::RuntimeError(msg);
    }
    const BIGNUM* sc;
    const BIGNUM* rc;
    BIGNUM* r = nullptr;
    BIGNUM* s = nullptr;

    ECDSA_SIG_get0(sig.get(), &rc, &sc);

    s = BN_dup(sc);
    if (!s) {
        std::string msg(
            "Crypto Error (SignMessage): Could not dup BIGNUM for s");
        throw Error::RuntimeError(msg);
    }
    r = BN_dup(rc);
    if (!r) {
        std::string msg(
            "Crypto Error (SignMessage): Could not dup BIGNUM for r");
        throw Error::RuntimeError(msg);
    }
    BIGNUM_ptr ord(BN_new(), BN_free);
    if (!ord) {
        std::string msg(
            "Crypto Error (SignMessage): Could not create BIGNUM for ord");
        throw Error::RuntimeError(msg);
    }

    BIGNUM_ptr ordh(BN_new(), BN_free);
    if (!ordh) {
        std::string msg(
            "Crypto Error (SignMessage): Could not create BIGNUM for ordh");
        throw Error::RuntimeError(msg);
    }

    int res = EC_GROUP_get_order(EC_KEY_get0_group(private_key_), ord.get(),
        nullptr);
    if (!res) {
        std::string msg("Crypto Error (SignMessage): Could not get order");
        throw Error::RuntimeError(msg);
    }

    res = BN_rshift(ordh.get(), ord.get(), 1);

    if (!res) {
        std::string msg("Crypto Error (SignMessage): Could not shift order BN");
        throw Error::RuntimeError(msg);
    }

    if (BN_cmp(s, ordh.get()) >= 0) {
        res = BN_sub(s, ord.get(), s);
        if (!res) {
            std::string msg("Crypto Error (SignMessage): Could not sub BNs");
            throw Error::RuntimeError(msg);
        }
    }

    res = ECDSA_SIG_set0(sig.get(), r, s);
    if (!res) {
        std::string msg("Crypto Error (SignMessage): Could not set r and s");
        throw Error::RuntimeError(msg);
    }

    // The -1 here is because we canonicalize the signature as in Bitcoin
    unsigned int der_sig_size = i2d_ECDSA_SIG(sig.get(), nullptr);
    ByteArray der_SIG(der_sig_size, 0);
    unsigned char* data = der_SIG.data();
    res = i2d_ECDSA_SIG(sig.get(), &data);

    if (!res) {
        std::string msg(
            "Crypto Error (SignMessage): Could not convert signature to DER");
        throw Error::RuntimeError(msg);
    }
    return der_SIG;
}  // pcrypto::sig::PrivateKey::SignMessage
