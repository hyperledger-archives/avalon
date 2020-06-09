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
 *
 * Lower-level functions implemented using OpenSSL.
 * See also sig_private_key_common.cpp for OpenSSL-independent code.
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
typedef std::unique_ptr<BIGNUM, void (*)(BIGNUM*)> BIGNUM_ptr;
typedef std::unique_ptr<EC_GROUP, void (*)(EC_GROUP*)> EC_GROUP_ptr;
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
 * Throws RuntimeError, ValueError.
 *
 * @param encoded Serialized ECDSA private key to deserialize
 * @returns deserialized ECDSA private key as a EC_KEY* cast to void*
 */
void* pcrypto::sig::PrivateKey::deserializeECDSAPrivateKey(
        const std::string& encoded) {
    BIO_ptr bio(BIO_new_mem_buf(encoded.c_str(), -1), BIO_free_all);
    if (!bio) {
        std::string msg(
            "Crypto Error (sig::PrivateKey::deserializeECDSAPrivateKey): "
            "Could not create BIO");
        throw Error::RuntimeError(msg);
    }

    EC_KEY* private_key = PEM_read_bio_ECPrivateKey(bio.get(),
        nullptr, nullptr, nullptr);
    if (!private_key) {
        std::string msg(
            "Crypto Error (sig::PrivateKey::deserializeECDSAPrivateKey): "
            "Could not deserialize private ECDSA key");
        throw Error::ValueError(msg);
    }
    return (void *)private_key;
}  // pcrypto::sig::PrivateKey::deserializeECDSAPrivateKey


/**
 * Copy constructor.
 * Throws RuntimeError.
 *
 * @param privateKey ECDSA private key to copy. Created by Generate()
 */
pcrypto::sig::PrivateKey::PrivateKey(
        const pcrypto::sig::PrivateKey& privateKey) {
    private_key_ = (void *)EC_KEY_dup((EC_KEY *)privateKey.private_key_);
    if (private_key_ == nullptr) {
        std::string msg("Crypto Error (sig::PrivateKey() copy): "
            "Could not copy private key");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::sig::PrivateKey::PrivateKey (copy constructor)


/**
 * PrivateKey Destructor.
 */
pcrypto::sig::PrivateKey::~PrivateKey() {
    if (private_key_ != nullptr) {
        EC_KEY_free((EC_KEY *)private_key_);
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

    if (private_key_ != nullptr)
        EC_KEY_free((EC_KEY *)private_key_);

    private_key_ = (void *)EC_KEY_dup((EC_KEY *)privateKey.private_key_);
    if (private_key_ == nullptr) {
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
    EC_KEY* key = (EC_KEY *)deserializeECDSAPrivateKey(encoded);
    if (private_key_ != nullptr)
        EC_KEY_free((EC_KEY *)private_key_);

    private_key_ = (void *)key;
}  // pcrypto::sig::PrivateKey::Deserialize


/**
 * Generate ECDSA private key.
 * Throws RuntimeError.
 */
void pcrypto::sig::PrivateKey::Generate() {
    if (private_key_ != nullptr) {
        EC_KEY_free((EC_KEY *)private_key_);
        private_key_ = nullptr;
    }

    EC_KEY_ptr private_key(EC_KEY_new(), EC_KEY_free);

    if (private_key == nullptr) {
        std::string msg("Crypto Error (sig::PrivateKey::Generate()): "
            "Could not create new EC_KEY");
        throw Error::RuntimeError(msg);
    }

    EC_GROUP_ptr ec_group(EC_GROUP_new_by_curve_name(constants::CURVE),
        EC_GROUP_clear_free);
    if (ec_group == nullptr) {
        std::string msg("Crypto Error (sig::PrivateKey::Generate()): "
            "Could not create EC_GROUP");
        throw Error::RuntimeError(msg);
    }

    if (!EC_KEY_set_group(private_key.get(), ec_group.get())) {
        std::string msg("Crypto Error (sig::PrivateKey::Generate()): "
            "Could not set EC_GROUP");
        throw Error::RuntimeError(msg);
    }

    if (!EC_KEY_generate_key(private_key.get())) {
        std::string msg("Crypto Error (sig::PrivateKey::Generater()): "
                "Could not generate EC_KEY");
        throw Error::RuntimeError(msg);
    }

    private_key_ = (void *)EC_KEY_dup(private_key.get());
    if (private_key_ == nullptr) {
        std::string msg("Crypto Error (sig::PrivateKey::Generater()): "
                "Could not dup private EC_KEY");
        throw Error::RuntimeError(msg);
    }
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
    BIO_ptr bio(BIO_new(BIO_s_mem()), BIO_free_all);

    if (!bio) {
        std::string msg("Crypto Error (sig::PrivateKey::Serialize): "
            "Could not create BIO");
        throw Error::RuntimeError(msg);
    }

    PEM_write_bio_ECPrivateKey(bio.get(), (EC_KEY *)private_key_,
        nullptr, nullptr, 0, 0, nullptr);

    int keylen = BIO_pending(bio.get());

    ByteArray pem_str(keylen + 1);
    if (!BIO_read(bio.get(), pem_str.data(), keylen)) {
        std::string msg("Crypto Error (sig::PrivateKey::Serialize): "
            "Could not read BIO");
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
        hashMessage.size(), (EC_KEY *)private_key_),
        ECDSA_SIG_free);
    if (sig == nullptr) {
        std::string msg(
            "Crypto Error (sig::PrivateKey::SignMessage): "
            "Could not compute ECDSA signature");
        throw Error::RuntimeError(msg);
    }

    const BIGNUM* sc;
    const BIGNUM* rc;
    BIGNUM* r = nullptr;
    BIGNUM* s = nullptr;

    ECDSA_SIG_get0(sig.get(), &rc, &sc);

    s = BN_dup(sc);
    if (!s) {
        std::string msg("Crypto Error (sig::PrivateKey:SignMessage): "
            "Could not dup BIGNUM for s");
        throw Error::RuntimeError(msg);
    }
    r = BN_dup(rc);
    if (!r) {
        std::string msg("Crypto Error (sig::PrivateKey:SignMessage): "
            "Could not dup BIGNUM for r");
        throw Error::RuntimeError(msg);
    }

    BIGNUM_ptr ord(BN_new(), BN_free);
    if (!ord) {
        std::string msg(
            "Crypto Error (sig::PrivateKey::SignMessage): "
            "Could not create BIGNUM for ord");
        throw Error::RuntimeError(msg);
    }

    BIGNUM_ptr ordh(BN_new(), BN_free);
    if (!ordh) {
        std::string msg(
            "Crypto Error (sig::PrivateKey::SignMessage): "
            "Could not create BIGNUM for ordh");
        throw Error::RuntimeError(msg);
    }

    int res = EC_GROUP_get_order(EC_KEY_get0_group((EC_KEY *)private_key_),
        ord.get(), nullptr);
    if (!res) {
        std::string msg("Crypto Error (sig::PrivateKey::SignMessage): "
            "Could not get order");
        throw Error::RuntimeError(msg);
    }

    res = BN_rshift(ordh.get(), ord.get(), 1);

    if (!res) {
        std::string msg("Crypto Error (sig::PrivateKey::SignMessage): "
            "Could not shift order BN");
        throw Error::RuntimeError(msg);
    }

    if (BN_cmp(s, ordh.get()) >= 0) {
        res = BN_sub(s, ord.get(), s);
        if (!res) {
            std::string msg("Crypto Error (sig::PrivateKey::SignMessage): "
            "Could not subtract BNs");
            throw Error::RuntimeError(msg);
        }
    }

    res = ECDSA_SIG_set0(sig.get(), r, s);
    if (!res) {
        std::string msg("Crypto Error (sig::PrivateKey::SignMessage): "
            "Could not set r and s");
        throw Error::RuntimeError(msg);
    }

    // The -1 here is because we canonicalize the signature as in Bitcoin
    unsigned int der_sig_size = i2d_ECDSA_SIG(sig.get(), nullptr);
    ByteArray der_SIG(der_sig_size, 0);
    unsigned char* data = der_SIG.data();
    res = i2d_ECDSA_SIG(sig.get(), &data);

    if (!res) {
        std::string msg(
            "Crypto Error (sig::PrivateKey::SignMessage): "
            "Could not convert signature to DER");
        throw Error::RuntimeError(msg);
    }
    return der_SIG;
}  // pcrypto::sig::PrivateKey::SignMessage
