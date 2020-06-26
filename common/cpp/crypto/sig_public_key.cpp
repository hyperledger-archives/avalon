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
 * Avalon ECDSA signature public key serialization and verification functions.
 * Used for Secp256k1 elliptical curves.
 *
 * Lower-level functions implemented using OpenSSL.
 * See also sig_public_key_common.cpp for OpenSSL-independent code.
 */

#include <openssl/pem.h>
#include <memory>    // std::unique_ptr

#include "crypto_shared.h"
#include "error.h"
#include "hex_string.h"
#include "sig.h"
#include "sig_private_key.h"
#include "sig_public_key.h"

#ifndef CRYPTOLIB_OPENSSL
#error "CRYPTOLIB_OPENSSL must be defined to compile source with OpenSSL."
#endif

namespace pcrypto = tcf::crypto;
namespace constants = tcf::crypto::constants;

// Typedefs for memory management
// Specify type and destroy function type for unique_ptrs
typedef std::unique_ptr<BIO, void (*)(BIO*)> BIO_ptr;
typedef std::unique_ptr<EVP_CIPHER_CTX, void (*)(EVP_CIPHER_CTX*)> CTX_ptr;
typedef std::unique_ptr<BN_CTX, void (*)(BN_CTX*)> BN_CTX_ptr;
typedef std::unique_ptr<EC_KEY, void (*)(EC_KEY*)> EC_KEY_ptr;
typedef std::unique_ptr<EC_GROUP, void (*)(EC_GROUP*)> EC_GROUP_ptr;
typedef std::unique_ptr<EC_POINT, void (*)(EC_POINT*)> EC_POINT_ptr;
typedef std::unique_ptr<ECDSA_SIG, void (*)(ECDSA_SIG*)> ECDSA_SIG_ptr;

// Error handling
namespace Error = tcf::error;


/**
 * Utility function: deserialize ECDSA Public Key.
 * Throws RuntimeError, ValueError.
 *
 * @param encoded Serialized ECDSA public key to deserialize
 * @returns deserialized ECDSA public key as a EC_KEY* cast to void*
 */
void *pcrypto::sig::PublicKey::deserializeECDSAPublicKey(
        const std::string& encoded) {

    // Sanity check
    if (encoded.size() == 0) {
        std::string msg(
            "Crypto Error (sig::PublicKey::deserializeECDSAPublicKey(): "
            "ECDSA public key PEM string is empty");
        throw Error::ValueError(msg);
    }

    BIO_ptr bio(BIO_new_mem_buf(encoded.c_str(), -1), BIO_free_all);
    if (bio == nullptr) {
        std::string msg(
            "Crypto Error (sig::PublicKey::deserializeECDSAPublicKey): "
            "Could not create BIO");
        throw Error::RuntimeError(msg);
    }

    EC_KEY* public_key = PEM_read_bio_EC_PUBKEY(bio.get(),
        nullptr, nullptr, nullptr);
    if (public_key == nullptr) {
        std::string msg(
            "Crypto Error (sig::PublicKey::deserializeECDSAPublicKey): "
            "Could not deserialize public ECDSA key");
        throw Error::ValueError(msg);
    }
    return (void *)public_key;
}  // pcrypto::sig::PublicKey::deserializeECDSAPublicKey


/**
 * Constructor from PrivateKey.
 *
 * @param privateKey encoded ECDSA private key string
 *                   created by PrivateKey::Generate()
 */
pcrypto::sig::PublicKey::PublicKey(const pcrypto::sig::PrivateKey& privateKey) {
    EC_KEY_ptr public_key(EC_KEY_new(), EC_KEY_free);
    if (public_key == nullptr) {
        std::string msg("Crypto Error (sig::PublicKey()): "
            "Could not create new public EC_KEY");
        throw Error::RuntimeError(msg);
    }

    EC_GROUP_ptr ec_group(EC_GROUP_new_by_curve_name(constants::CURVE),
        EC_GROUP_clear_free);
    if (ec_group == nullptr) {
        std::string msg(
            "Crypto Error (sig::PublicKey()): Could not create EC_GROUP");
        throw Error::RuntimeError(msg);
    }
    EC_GROUP_set_point_conversion_form(ec_group.get(),
        POINT_CONVERSION_COMPRESSED);
    BN_CTX_ptr context(BN_CTX_new(), BN_CTX_free);
    if (context == nullptr) {
        std::string msg(
            "Crypto Error (sig::PublicKey()): Could not create new CTX");
        throw Error::RuntimeError(msg);
    }

    EC_POINT_ptr p(EC_POINT_new(ec_group.get()), EC_POINT_free);
    if (p == nullptr) {
        std::string msg(
            "Crypto Error (sig::PublicKey()): Could not create new EC_POINT");
        throw Error::RuntimeError(msg);
    }

    if (!EC_KEY_set_group(public_key.get(), ec_group.get())) {
        std::string msg(
            "Crypto Error (sig::PublicKey()): Could not set EC_GROUP");
        throw Error::RuntimeError(msg);
    }

    if (!EC_POINT_mul(ec_group.get(), p.get(),
            EC_KEY_get0_private_key((EC_KEY *)privateKey.private_key_),
            nullptr, nullptr, context.get())) {
        std::string msg(
            "Crypto Error (sig::PublicKey()): Could not compute EC_POINT_mul");
        throw Error::RuntimeError(msg);
    }

    if (!EC_KEY_set_public_key(public_key.get(), p.get())) {
        std::string msg(
            "Crypto Error (sig::PublicKey()): Could not set public EC_KEY");
        throw Error::RuntimeError(msg);
    }

    public_key_ = (void *)EC_KEY_dup(public_key.get());
    if (public_key_ == nullptr) {
        std::string msg("Crypto Error (sig::PublicKey()): "
            "Could not duplicate public EC_KEY");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::sig::PublicKey::PublicKey


/**
 * Copy constructor.
 * Throws RuntimeError.
 *
 * @param publicKey Public key to copy
 */
pcrypto::sig::PublicKey::PublicKey(const pcrypto::sig::PublicKey& publicKey) {
    public_key_ = (void *)EC_KEY_dup((EC_KEY *)publicKey.public_key_);
    if (public_key_ == nullptr) {
        std::string msg(
            "Crypto Error (sig::PublicKey() copy): Could not copy public key");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::sig::PublicKey::PublicKey (copy constructor)


/**
 * PublicKey Destructor.
 */
pcrypto::sig::PublicKey::~PublicKey() {
    if (public_key_ != nullptr) {
        EC_KEY_free((EC_KEY *)public_key_);
        public_key_ = nullptr;
    }
}  // pcrypto::sig::PublicKey::~PublicKey


/**
 * Assignment operator = overload.
 * Throws RuntimeError.
 *
 * @param publicKey Public key to assign
 */
pcrypto::sig::PublicKey& pcrypto::sig::PublicKey::operator=(
    const pcrypto::sig::PublicKey& publicKey) {
    if (this == &publicKey)
        return *this;

    if (public_key_ != nullptr)
        EC_KEY_free((EC_KEY *)public_key_);

    public_key_ = (void *)EC_KEY_dup((EC_KEY *)publicKey.public_key_);
    if (public_key_ == nullptr) {
        std::string msg("Crypto Error (sig::PublicKey operator =): "
            "Could not copy public key");
        throw Error::RuntimeError(msg);
    }
    return *this;
}  // pcrypto::sig::PublicKey::operator =


/**
 * Deserialize Digital Signature Public Key.
 * Implemented with deserializeECDSAPublicKey().
 *
 * For example:
 * -----BEGIN PUBLIC KEY-----
 * MIHVMIGOBgcqhkjOPQIBMIGCAgEBMCwGByqGSM49AQECIQD/////////////////
 * ///////////////////+///8LzAGBAEABAEHBCECeb5mfvncu6xVoGKVzocLBwKb
 * /NstzijZWfKBWxb4F5gCIQD////////////////////+uq7c5q9IoDu/0l6M0DZB
 * QQIBAQNCAARxy5u39/yqw2tI98mVa4+KOnR4lAMPdFQruTiAZ2UMH+JrTyzGoChm
 * P7hIrxHirYc7T0hTPbN3oVgWbfQEmXsv
 * -----END PUBLIC KEY-----
 *
 * Throws RunTime.
 *
 * @param encoded Serialized ECDSA public key to deserialize
 */
void pcrypto::sig::PublicKey::Deserialize(const std::string& encoded) {
    EC_KEY* key = (EC_KEY *)deserializeECDSAPublicKey(encoded);

    if (public_key_ != nullptr)
        EC_KEY_free((EC_KEY *)public_key_);

    public_key_ = (void *)key;
}  // pcrypto::sig::PublicKey::Deserialize


/**
 * Deserialize EC point (X,Y) hex string.
 *
 * A EC point is the public key for ECDSA.
 * A point is represented as two 256-bit integers in hex
 * with the Ethereum prefix "04" (for uncompressed public key).
 * In hex, this is a 2 hex digit prefix followed by two 64 hex digit points.
 *
 * For example (130 hex digit line broken for readability):
 * 04
 * D860F8A251ACF59E6B3F73F403F30B7742EF8F11F56103BF8F65A6E50D875F2F
 * 04D1F982D83534E5FEA9D0096468E7E7B144487BF579BAC65E7129D9D85E4013
 *
 * Throws RuntimeError, ValueError.
 *
 * @param hexXY EC point (X,Y) represented as a hex string
 */
void pcrypto::sig::PublicKey::DeserializeXYFromHex(const std::string& hexXY) {

    // Sanity check
    if (hexXY.size() != 2 * constants::EC_POINT_BYTE_LEN) {
        std::string msg("Crypto Error (sig::PublicKey::DeserializeXYFromHex()): "
            "hexadecimal point (X,Y) has incorrect length");
        throw Error::ValueError(msg);
    }

    EC_KEY_ptr public_key(EC_KEY_new(), EC_KEY_free);
    if (public_key == nullptr) {
        std::string msg("Crypto Error (sig::PublicKey::DeserializeXYFromHex): "
            "Could not create new public EC_KEY");
        throw Error::RuntimeError(msg);
    }

    EC_GROUP_ptr ec_group(EC_GROUP_new_by_curve_name(NID_secp256k1),
         EC_GROUP_clear_free);
    if (ec_group == nullptr) {
        std::string msg("Crypto Error (sig::PublicKey::DeserializeXYFromHex): "
            "Could not create EC_GROUP");
        throw Error::RuntimeError(msg);
    }
    EC_GROUP_set_point_conversion_form(ec_group.get(),
        POINT_CONVERSION_COMPRESSED);
    if (!EC_KEY_set_group(public_key.get(), ec_group.get())) {
        std::string msg(
            "Crypto Error (sig::PublicKey::DeserializeXYFromHex): "
            "Could not set EC_GROUP");
        throw Error::RuntimeError(msg);
    }

    EC_POINT_ptr p(EC_POINT_hex2point(
        ec_group.get(), hexXY.data(), nullptr, nullptr), EC_POINT_free);
    if (p == nullptr) {
        std::string msg("Crypto Error (sig::PublicKey::DeserializeXYFromHex): "
            "Could not create new EC_POINT");
        throw Error::RuntimeError(msg);
    }

    int res = EC_KEY_set_public_key(public_key.get(), p.get());
    if (res == 0) {
        std::string msg(
            "Crypto Error (DeserializeXYFromHex): Could not set EC point");
        throw Error::ValueError(msg);
    }
    if (public_key_ != nullptr)
        EC_KEY_free((EC_KEY *)public_key_);

    public_key_ = (void *)EC_KEY_dup(public_key.get());
    if (public_key_ == nullptr) {
        std::string msg("Crypto Error (DeserializeXYFromHex): "
            "Could not duplicate public EC_KEY");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::sig::DeserializeXYFromHex


/**
 * Serialize ECDSA Public Key.
 *
 * For example:
 * -----BEGIN PUBLIC KEY-----
 * MIHVMIGOBgcqhkjOPQIBMIGCAgEBMCwGByqGSM49AQECIQD/////////////////
 * ///////////////////+///8LzAGBAEABAEHBCECeb5mfvncu6xVoGKVzocLBwKb
 * /NstzijZWfKBWxb4F5gCIQD////////////////////+uq7c5q9IoDu/0l6M0DZB
 * QQIBAQNCAARxy5u39/yqw2tI98mVa4+KOnR4lAMPdFQruTiAZ2UMH+JrTyzGoChm
 * P7hIrxHirYc7T0hTPbN3oVgWbfQEmXsv
 * -----END PUBLIC KEY-----
 *
 * Throws RuntimeError.
 *
 * @returns Serialized ECDSA public key as a string
 */
std::string pcrypto::sig::PublicKey::Serialize() const {
    if (public_key_ == nullptr) {
        std::string msg("Crypto Error (sig::PublicKey::Serialize): "
            "PublicKey is not initialized");
        throw Error::RuntimeError(msg);
    }

    int res;
    std::string str("");
    int keylen = 0;

    BIO_ptr bio(BIO_new(BIO_s_mem()), BIO_free_all);
    if (bio == nullptr) {
        std::string msg("Crypto Error (sig::PublicKey::Serialize): "
            "Could not create BIO");
        throw Error::RuntimeError(msg);
    }
    res = PEM_write_bio_EC_PUBKEY(bio.get(), (EC_KEY *)public_key_);

    if (res == 0) {
        std::string msg(
            "Crypto Error (sig::PublicKey::Serialize): "
            "Could not serialize EC Public key");
        throw Error::RuntimeError(msg);
        ;
    }

    keylen = BIO_pending(bio.get());

    ByteArray pem_str(keylen + 1);
    if (!BIO_read(bio.get(), pem_str.data(), keylen)) {
        std::string msg("Crypto Error (sig::PublicKey::Serialize): "
            "Could not read BIO");
        throw Error::RuntimeError(msg);
    }
    pem_str[keylen] = '\0';
    str.assign(reinterpret_cast<char*>(pem_str.data()));

    return str;
}  // pcrypto::sig::PublicKey::Serialize


/**
 * Serialize EC point (X,Y) to a hexadecimal string.
 *
 * A EC point is the public key for ECDSA.
 * A point is represented as two 256-bit integers in hex
 * with the Ethereum prefix "04" (for uncompressed public key).
 * In hex, this is a 2 hex digit prefix followed by two 64 hex digit points.
 *
 * For example (130 hex digit line broken for readability):
 * 04
 * D860F8A251ACF59E6B3F73F403F30B7742EF8F11F56103BF8F65A6E50D875F2F
 * 04D1F982D83534E5FEA9D0096468E7E7B144487BF579BAC65E7129D9D85E4013
 *
 * Throws RuntimeError.
 *
 * @returns serialized EC point (X,Y) as a hex string
 */
std::string pcrypto::sig::PublicKey::SerializeXYToHex() const {
    if (public_key_ == nullptr) {
        std::string msg("Crypto Error (sig::PublicKey::SerializeXYToHex): "
            "PublicKey is not initialized");
        throw Error::RuntimeError(msg);
    }

    char* cstring = nullptr;

    cstring = EC_POINT_point2hex(EC_KEY_get0_group((EC_KEY *)public_key_),
        EC_KEY_get0_public_key((EC_KEY *)public_key_),
            POINT_CONVERSION_UNCOMPRESSED, nullptr);
    if (cstring == nullptr) {
        std::string msg("Crypto Error (sig::PublicKey::SerializeXYToHex): "
            "Could not serialize EC public key");
        throw Error::RuntimeError(msg);
    }

    // Convert C string to C++ string and return it
    std::string str(cstring);
    OPENSSL_free(cstring);
    return std::string(str);
}  // pcrypto::sig::PublicKey::SerializeXYToHex


/**
 * Verifies ECDSA signature of message. It's expected that the caller of
 * this function passes a hash value of the original message.
 *
 * Sample DER-encoded signature in hexadecimal (71 bytes):
 * 30450221008e6b04abffea7dab1d2c6190619096262e567fa9f94be337953aab
 * 8742158d1c022034bd23799bc27308ce645191c43c16d5fb767e6cb5ab002442
 * 7194cbba59783c
 *
 * @param hashMessage Data in a byte array to verify.
 *                    This is not the message to verify but a hash of the message
 * @param signature ByteArray containing signature data in DER format
 *                  as defined in RFC 4492
 * @returns 1 if signature is valid, 0 if signature is invalid,
 *          and -1 if there is an internal error.
 */
int pcrypto::sig::PublicKey::VerifySignature(
        const ByteArray& hashMessage, const ByteArray& signature) const {

    // Decode signature B64 -> DER -> ECDSA_SIG
    const unsigned char* der_SIG = (const unsigned char*)signature.data();
    ECDSA_SIG_ptr sig(
        d2i_ECDSA_SIG(nullptr, (const unsigned char**)(&der_SIG),
            signature.size()), ECDSA_SIG_free);
    if (sig == nullptr) {
        return -1;
    }

    // Verify
    return ECDSA_do_verify(
        (const unsigned char*)hashMessage.data(), hashMessage.size(),
        sig.get(), (EC_KEY *)public_key_);
}  // pcrypto::sig::PublicKey::VerifySignature
