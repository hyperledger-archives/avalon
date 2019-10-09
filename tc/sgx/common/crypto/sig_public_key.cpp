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
#include "sig_public_key.h"
#include <openssl/err.h>
#include <openssl/pem.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <algorithm>
#include <memory>
#include <vector>
#include "base64.h"  // simple base64 enc/dec routines
#include "crypto_shared.h"
#include "error.h"
#include "hex_string.h"
#include "sig.h"
#include "sig_private_key.h"
/***Conditional compile untrusted/trusted***/
#if _UNTRUSTED_
#include <openssl/crypto.h>
#include <stdio.h>
#else
#include "tSgxSSL_api.h"
#endif
/***END Conditional compile untrusted/trusted***/

namespace pcrypto = tcf::crypto;
namespace constants = tcf::crypto::constants;

// Typedefs for memory management
// Specify type and destroy function type for unique_ptrs
typedef std::unique_ptr<BIO, void (*)(BIO*)> BIO_ptr;
typedef std::unique_ptr<EVP_CIPHER_CTX, void (*)(EVP_CIPHER_CTX*)> CTX_ptr;
typedef std::unique_ptr<BN_CTX, void (*)(BN_CTX*)> BN_CTX_ptr;
typedef std::unique_ptr<BIGNUM, void (*)(BIGNUM*)> BIGNUM_ptr;
typedef std::unique_ptr<EC_KEY, void (*)(EC_KEY*)> EC_KEY_ptr;
typedef std::unique_ptr<EC_GROUP, void (*)(EC_GROUP*)> EC_GROUP_ptr;
typedef std::unique_ptr<EC_POINT, void (*)(EC_POINT*)> EC_POINT_ptr;
typedef std::unique_ptr<ECDSA_SIG, void (*)(ECDSA_SIG*)> ECDSA_SIG_ptr;

// Error handling
namespace Error = tcf::error;

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Utility function: deserialize ECDSA Public Key
// throws RuntimeError, ValueError
EC_KEY* deserializeECDSAPublicKey(const std::string& encoded) {
    BIO_ptr bio(BIO_new_mem_buf(encoded.c_str(), -1), BIO_free_all);
    if (!bio) {
        std::string msg("Crypto Error (deserializeECDSAPublicKey): Could not create BIO");
        throw Error::RuntimeError(msg);
    }

    EC_KEY* public_key = PEM_read_bio_EC_PUBKEY(bio.get(), NULL, NULL, NULL);
    if (!public_key) {
        std::string msg(
            "Crypto Error (deserializeECDSAPublicKey): Could not "
            "deserialize public ECDSA key");
        throw Error::ValueError(msg);
    }
    return public_key;
}  // deserializeECDSAPublicKey

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// constructor
pcrypto::sig::PublicKey::PublicKey() {
    public_key_ = nullptr;
}  // pcrypto::sig::PublicKey::PublicKey

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Constructor from PrivateKey
pcrypto::sig::PublicKey::PublicKey(const pcrypto::sig::PrivateKey& privateKey) {
    EC_KEY_ptr public_key(EC_KEY_new(), EC_KEY_free);
    if (!public_key) {
        std::string msg("Crypto Error (sig::PublicKey()): Could not create new public EC_KEY");
        throw Error::RuntimeError(msg);
    }

    EC_GROUP_ptr ec_group(EC_GROUP_new_by_curve_name(constants::CURVE), EC_GROUP_clear_free);
    if (!ec_group) {
        std::string msg("Crypto Error (sig::PublicKey()()): Could not create EC_GROUP");
        throw Error::RuntimeError(msg);
    }
    EC_GROUP_set_point_conversion_form(ec_group.get(), POINT_CONVERSION_COMPRESSED);
    BN_CTX_ptr context(BN_CTX_new(), BN_CTX_free);
    if (!context) {
        std::string msg("Crypto Error (sig::PublicKey()): Could not create new CTX");
        throw Error::RuntimeError(msg);
    }

    EC_POINT_ptr p(EC_POINT_new(ec_group.get()), EC_POINT_free);
    if (!p) {
        std::string msg("Crypto Error (sig::PublicKey()): Could not create new EC_POINT");
        throw Error::RuntimeError(msg);
    }

    if (!EC_KEY_set_group(public_key.get(), ec_group.get())) {
        std::string msg("Crypto Error (sig::PublicKey()): Could not set EC_GROUP");
        throw Error::RuntimeError(msg);
    }

    if (!EC_POINT_mul(ec_group.get(), p.get(), EC_KEY_get0_private_key(privateKey.private_key_),
            NULL, NULL, context.get())) {
        std::string msg("Crypto Error (sig::PublicKey()): Could not compute EC_POINT_mul");
        throw Error::RuntimeError(msg);
    }

    if (!EC_KEY_set_public_key(public_key.get(), p.get())) {
        std::string msg("Crypto Error (sig::PublicKey()): Could not set public EC_KEY");
        throw Error::RuntimeError(msg);
    }

    public_key_ = EC_KEY_dup(public_key.get());

    if (!public_key_) {
        std::string msg("Crypto Error (sig::PublicKey()): Could not dup public EC_KEY");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::sig::PublicKey::PublicKey

// Constructor from encoded string
// throws RuntimeError, ValueError
pcrypto::sig::PublicKey::PublicKey(const std::string& encoded) {
    public_key_ = deserializeECDSAPublicKey(encoded);
}  // pcrypto::sig::PublicKey::PublicKey

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Copy constructor
// throws RuntimeError
pcrypto::sig::PublicKey::PublicKey(const pcrypto::sig::PublicKey& publicKey) {
    public_key_ = EC_KEY_dup(publicKey.public_key_);
    if (!public_key_) {
        std::string msg("Crypto Error (sig::PublicKey() copy): Could not copy public key");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::sig::PublicKey::PublicKey (copy constructor)

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Move constructor
// throws RuntimeError
pcrypto::sig::PublicKey::PublicKey(pcrypto::sig::PublicKey&& publicKey) {
    public_key_ = publicKey.public_key_;
    publicKey.public_key_ = nullptr;
    if (!public_key_) {
        std::string msg("Crypto Error (sig::PublicKey() move): Cannot move null public key");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::sig::PublicKey::PublicKey (move constructor)

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Destructor
pcrypto::sig::PublicKey::~PublicKey() {
    if (public_key_)
        EC_KEY_free(public_key_);
}  // pcrypto::sig::PublicKey::~PublicKey

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// assignment operator overload
// throws RuntimeError
pcrypto::sig::PublicKey& pcrypto::sig::PublicKey::operator=(
    const pcrypto::sig::PublicKey& publicKey) {
    if (this == &publicKey)
        return *this;
    if (public_key_)
        EC_KEY_free(public_key_);
    public_key_ = EC_KEY_dup(publicKey.public_key_);
    if (!public_key_) {
        std::string msg("Crypto Error (sig::PublicKey operator =): Could not copy public key");
        throw Error::RuntimeError(msg);
    }
    return *this;
}  // pcrypto::sig::PublicKey::operator =

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Deserialize Digital Signature Public Key
// throws RunTime
void pcrypto::sig::PublicKey::Deserialize(const std::string& encoded) {
    EC_KEY* key = deserializeECDSAPublicKey(encoded);
    if (public_key_)
        EC_KEY_free(public_key_);
    public_key_ = key;
}  // pcrypto::sig::PublicKey::Deserialize

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Deserialize EC point (X,Y) hex string
// throws RuntimeError, ValueError
void pcrypto::sig::PublicKey::DeserializeXYFromHex(const std::string& hexXY) {
    EC_KEY_ptr public_key(EC_KEY_new(), EC_KEY_free);
    if (!public_key) {
        std::string msg(
            "Crypto Error (sig::DeserializeXYFromHex): Could not create new public EC_KEY");
        throw Error::RuntimeError(msg);
    }

    EC_GROUP_ptr ec_group(EC_GROUP_new_by_curve_name(constants::CURVE), EC_GROUP_clear_free);
    if (!ec_group) {
        std::string msg("Crypto Error (sig::DeserializeXYFromHex): Could not create EC_GROUP");
        throw Error::RuntimeError(msg);
    }
    EC_GROUP_set_point_conversion_form(ec_group.get(), POINT_CONVERSION_COMPRESSED);
    if (!EC_KEY_set_group(public_key.get(), ec_group.get())) {
        std::string msg("Crypto Error (sig::DeserializeXYFromHex): Could not set EC_GROUP");
        throw Error::RuntimeError(msg);
    }

    EC_POINT_ptr p(EC_POINT_hex2point(ec_group.get(), hexXY.data(), NULL, NULL), EC_POINT_free);
    if (!p) {
        std::string msg("Crypto Error (sig::DeserializeXYFromHex): Could not create new EC_POINT");
        throw Error::RuntimeError(msg);
    }

    int res = EC_KEY_set_public_key(public_key.get(), p.get());
    if (!res) {
        std::string msg("Crypto Error (DeserializeXYFromHex): Could not set EC point");
        throw Error::ValueError(msg);
    }
    if (public_key_)
        EC_KEY_free(public_key_);
    public_key_ = EC_KEY_dup(public_key.get());

    if (!public_key_) {
        std::string msg("Crypto Error (DeserializeXYFromHex): Could not dup public EC_KEY");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::sig::DeserializeXYFromHex

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Serialize Digital Signature Public Key
// throws RuntimeError
std::string pcrypto::sig::PublicKey::Serialize() const {
    if (public_key_ == nullptr) {
        std::string msg("Crypto Error (Serialize): PublicKey is not initialized");
        throw Error::RuntimeError(msg);
    }

    int res;
    std::string str("");
    int keylen = 0;

    BIO_ptr bio(BIO_new(BIO_s_mem()), BIO_free_all);
    if (!bio) {
        std::string msg("Crypto Error (Serialize): Could not create BIO");
        throw Error::RuntimeError(msg);
    }
    res = PEM_write_bio_EC_PUBKEY(bio.get(), public_key_);

    if (!res) {
        std::string msg("Crypto Error (Serialize): Could not serialize EC Public key");
        throw Error::RuntimeError(msg);
        ;
    }

    keylen = BIO_pending(bio.get());

    ByteArray pem_str(keylen + 1);
    if (!BIO_read(bio.get(), pem_str.data(), keylen)) {
        std::string msg("Crypto Error (Serialize): Could not read BIO");
        throw Error::RuntimeError(msg);
    }
    pem_str[keylen] = '\0';
    str.assign(reinterpret_cast<char*>(pem_str.data()));

    return str;
}  // pcrypto::sig::PublicKey::Serialize
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// throws RuntimeError
// Serialize EC point (X,Y) to hex string
std::string pcrypto::sig::PublicKey::SerializeXYToHex() const {
    if (public_key_ == nullptr) {
        std::string msg("Crypto Error (SerializeXYToHex): PublicKey is not initialized");
        throw Error::RuntimeError(msg);
    }

    char* cstring = nullptr;

    cstring = EC_POINT_point2hex(EC_KEY_get0_group(public_key_),
        EC_KEY_get0_public_key(public_key_), POINT_CONVERSION_UNCOMPRESSED, NULL);
    if (!cstring) {
        std::string msg("Crypto Error (SerializeXYToHex): Could not serialize EC public key");
        throw Error::RuntimeError(msg);
    }
    std::string str(cstring);
    OPENSSL_free(cstring);
    return std::string(str);
}  // SerializeXYToHex

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Verifies ECDSA signature of message. It's expected that caller of
// this function passes hash value of the original message.
// input signature ByteArray contains raw binary data
// returns 1 if signature is valid, 0 if signature is invalid and -1 if there is
// an internal error
int pcrypto::sig::PublicKey::VerifySignature(
    const ByteArray& hashMessage, const ByteArray& signature) const {
    // Decode signature B64 -> DER -> ECDSA_SIG
    const unsigned char* der_SIG = (const unsigned char*)signature.data();
    ECDSA_SIG_ptr sig(
        d2i_ECDSA_SIG(NULL, (const unsigned char**)(&der_SIG), signature.size()), ECDSA_SIG_free);
    if (!sig) {
        return -1;
    }
    // Verify
    return ECDSA_do_verify(
        (const unsigned char*)hashMessage.data(), hashMessage.size(),
        sig.get(), public_key_);
}  // pcrypto::sig::PublicKey::VerifySignature
