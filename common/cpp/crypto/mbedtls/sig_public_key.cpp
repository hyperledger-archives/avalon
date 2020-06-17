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

/**
 * @file
 * Avalon ECDSA signature public key serialization and verification functions.
 * Used for Secp256k1 elliptical curves.
 *
 * Lower-level functions implemented using Mbed TLS.
 * See also sig_public_key_common.cpp for Mbed TLS-independent code.
 */

#include <stdlib.h>           // malloc(), free()
#include <mbedtls/pk.h>
#include <mbedtls/md.h>       // MBEDTLS_MD_SHA256
#include <mbedtls/ecp.h>
#include <mbedtls/ecdsa.h>

#include "crypto_shared.h"
#include "error.h"
#include "hex_string.h"       // BinaryToHexString(), HexStringToBinary()
#include "sig.h"
#include "sig_private_key.h"
#include "sig_public_key.h"

#ifndef CRYPTOLIB_MBEDTLS
#error "CRYPTOLIB_MBEDTLS must be defined to compile source with Mbed TLS."
#endif

namespace pcrypto = tcf::crypto;
namespace constants = tcf::crypto::constants;
namespace Error = tcf::error; // Error handling


/**
 * Utility function: copy ECDSA public key context.
 * The context is the keypair components (group G, point Q).
 * Bignum d is private and not a part of a public key.
 *
 * @param src The destination to copy the public key context.
 *            Must be previously initialized by mbedtls_ecdsa_init()
 * @param dst The public key context to copy
 * @returns 0 on success, Mbed TLS error code on error
 */
static int copy_ecdsa_public_key_context(
        mbedtls_ecdsa_context *dst, const mbedtls_ecdsa_context *src) {
    int rc;

    // Copy ECDSA context with keypair components (G, Q)
    // Bignum d is private and not a part of a public key.
    rc = mbedtls_ecp_group_copy(&dst->grp, &src->grp);
    if (rc != 0) {
        return rc;
    }
    rc = mbedtls_ecp_copy(&dst->Q, &src->Q);
    if (rc != 0) {
        return rc;
    }
}   // copy_ecdsa_public_key_context()


/**
 * Utility function: allocate and copy ECDSA public key context.
 * The public key context is the keypair components (group G, point Q)
 * Bignum d is private and not a part of a public key.
 *
 * Throws RuntimeError.
 *
 * @param ecdsa_ctx The private key context to copy
 * @returns An allocated copy of ecdsa_ctx.
 *          Must be ecdsa_free()'ed and free()ed.
 */
static mbedtls_ecdsa_context* duplicate_ecdsa_public_key_context(
        const mbedtls_ecdsa_context *ecdsa_ctx) {
    int rc;

    // Allocate ECDSA context
    mbedtls_ecdsa_context *new_ecdsa_ctx =
        (mbedtls_ecdsa_context *)malloc(sizeof (mbedtls_ecdsa_context));
    if (new_ecdsa_ctx == nullptr) {
        std::string msg(
            "Crypto Error (duplicate_ecdsa_public_key_context(): "
            "Could not allocate memory for ECDSA key context");
        throw Error::RuntimeError(msg);
    }
    mbedtls_ecdsa_init(new_ecdsa_ctx);

    // Copy ECDSA context with keypair components (G, Q)
    // Bignum d is private and not a part of a public key.
    rc = copy_ecdsa_public_key_context(new_ecdsa_ctx, ecdsa_ctx);
    if (rc != 0) {
        mbedtls_ecdsa_free(new_ecdsa_ctx);
        free(new_ecdsa_ctx);
        std::string msg(
            "Crypto Error (duplicate_ecdsa_public_key_context(): "
            "Could not copy ECDSA key context");
        throw Error::RuntimeError(msg);
    }

    return new_ecdsa_ctx;
}   // duplicate_ecdsa_public_key_context()


/**
 * Utility function: deserialize ECDSA Public Key.
 * Throws RuntimeError, ValueError.
 *
 * @param encoded Serialized ECDSA public key to deserialize
 * @returns deserialized ECDSA public key as a mbedtls_ecdsa_context* cast to void*
 */
void *pcrypto::sig::PublicKey::deserializeECDSAPublicKey(
        const std::string& encoded) {
    mbedtls_pk_context pk_ctx;
    int rc;

    // Sanity check
    if (encoded.size() == 0) {
        std::string msg(
            "Crypto Error (sig::PublicKey::deserializeECDSAPublicKey(): "
            "ECDSA public key PEM string is empty");
        throw Error::ValueError(msg);
    }

    mbedtls_pk_init(&pk_ctx);

    // Parse PEM string containing public key
    rc =  mbedtls_pk_parse_public_key(&pk_ctx, (const unsigned char *)encoded.c_str(),
        encoded.size() + 1);
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (sig::PublicKey::deserializeECDSAPublicKey(): "
            "Cannot parse ECDSA public key PEM string for serialization");
        throw Error::ValueError(msg);
    }

    // Sanity check public key
    if (mbedtls_pk_get_type(&pk_ctx) != MBEDTLS_PK_ECKEY) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (sig::PublicKey::deserializeECDSAPublicKey(): "
            "Public key in PEM string is not ECDSA");
        throw Error::ValueError(msg);
    }
    mbedtls_ecp_keypair *ec_keypair = mbedtls_pk_ec(pk_ctx);
    rc = mbedtls_ecp_check_pubkey(&ec_keypair->grp, &ec_keypair->Q);
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (sig::PublicKey::deserializeECDSAPublicKey(): "
            "Invalid ECDSA public key in PEM string");
        throw Error::ValueError(msg);
    }

    // Allocate and copy ECDSA context
    mbedtls_ecdsa_context *ecdsa_ctx =
        duplicate_ecdsa_public_key_context(ec_keypair);
    if (ecdsa_ctx == nullptr) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (sig::PublicKey::deserializeECDSAPublicKey()): "
            "Could not copy public key");
        throw Error::RuntimeError(msg);
    }

    mbedtls_pk_free(&pk_ctx);

    return (void *)ecdsa_ctx;
}  // pcrypto::sig::PublicKey::deserializeECDSAPublicKey


/**
 * Constructor from PrivateKey.
 *
 * @param privateKey encoded ECDSA private key string
 *                   created by PrivateKey::Generate()
 */
pcrypto::sig::PublicKey::PublicKey(const pcrypto::sig::PrivateKey& privateKey) {
    // Allocate and copy ECDSA context (copy public key parts from private key)
    public_key_ = (void *)duplicate_ecdsa_public_key_context(
        (mbedtls_ecdsa_context *)privateKey.private_key_);
    if (public_key_ == nullptr) {
        std::string msg("Crypto Error (sig::PublicKey(privateKey): "
            "Could not copy private key to public key");
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
    // Allocate and copy ECDSA context
    public_key_ = (void *)duplicate_ecdsa_public_key_context(
        (mbedtls_ecdsa_context *)publicKey.public_key_);
    if (public_key_ == nullptr) {
        std::string msg("Crypto Error (sig::PublicKey copy constructor): "
            "Could not copy public key");
        throw Error::RuntimeError(msg);
    }
}  // pcrypto::sig::PublicKey::PublicKey (copy constructor)


/**
 * PublicKey Destructor.
 */
pcrypto::sig::PublicKey::~PublicKey() {
    if (public_key_ != nullptr) {
        mbedtls_ecdsa_free((mbedtls_ecdsa_context *)public_key_);
        free(public_key_);
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

    if (public_key_ != nullptr) {
        mbedtls_ecdsa_free((mbedtls_ecdsa_context *)public_key_);
        free(public_key_);
        public_key_ = nullptr;
    }

    // Allocate and copy ECDSA context
    public_key_ = (void *)duplicate_ecdsa_public_key_context(
        (mbedtls_ecdsa_context *)publicKey.public_key_);
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
    mbedtls_ecdsa_context *key =
        (mbedtls_ecdsa_context *)deserializeECDSAPublicKey(encoded);

    if (public_key_ != nullptr) {
        mbedtls_ecdsa_free((mbedtls_ecdsa_context *)public_key_);
        free(public_key_);
        public_key_ = nullptr;
    }

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
    unsigned char binary_xy[constants::EC_POINT_BYTE_LEN];
    int rc;

    // Sanity check
    if (hexXY.size() != 2 * constants::EC_POINT_BYTE_LEN) {
        std::string msg("Crypto Error (sig::PublicKey::DeserializeXYFromHex()): "
            "hexadecimal point (X,Y) has incorrect length");
        throw Error::ValueError(msg);
    }

    // Allocate ECDSA context
    mbedtls_ecdsa_context *new_ecdsa_ctx =
        (mbedtls_ecdsa_context *)malloc(sizeof (mbedtls_ecdsa_context));
    if (new_ecdsa_ctx == nullptr) {
        std::string msg(
            "Crypto Error (sig::PublicKey::DeserializeXYFromHex(): "
            "Could not allocate memory for ECDSA key context");
        throw Error::RuntimeError(msg);
    }
    mbedtls_ecdsa_init(new_ecdsa_ctx);

    // Set group with elliptic curve
    rc = mbedtls_ecp_group_load(&new_ecdsa_ctx->grp, MBEDTLS_ECP_DP_SECP256K1);
    if (rc != 0) {
        std::string msg("Crypto Error (sig::PublicKey::DeserializeXYFromHex()): "
            "cannot set curve secp256k1 in group");
        throw Error::RuntimeError(msg);
    }

    // Convert point (X,Y) from hex to binary
    HexStringToBinary(binary_xy, sizeof (binary_xy), hexXY);

    // Read point (X,Y) into context
    rc = mbedtls_ecp_point_read_binary(&new_ecdsa_ctx->grp, &new_ecdsa_ctx->Q,
        binary_xy, sizeof (binary_xy));
    if (rc != 0) {
        std::string msg("Crypto Error (sig::PublicKey::DeserializeXYFromHex): "
            "Could not read EC point (X,Y) from hex string");
        throw Error::ValueError(msg);
    }

    // Set public key with new point
    if (public_key_ != nullptr) {
        mbedtls_ecdsa_free((mbedtls_ecdsa_context *)public_key_);
        free(public_key_);
    }

    public_key_ = (void *)new_ecdsa_ctx;
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

    unsigned char pem_str[constants::MAX_PEM_LEN];
    mbedtls_pk_context pk_ctx;
    int rc;

    if (public_key_ == nullptr) {
        std::string msg(
            "Crypto Error (Serialize): PublicKey is not initialized");
        throw Error::RuntimeError(msg);
    }

    // Create PK context from the ECDSA context (public_key_)
    mbedtls_pk_init(&pk_ctx);
    rc = mbedtls_pk_setup(&pk_ctx, mbedtls_pk_info_from_type(MBEDTLS_PK_ECKEY));
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg(
            "Crypto Error (sig::PublicKey::Serialize): "
            "mbedtls_pk_setup() failed");
        throw Error::RuntimeError(msg);
    }

    rc = copy_ecdsa_public_key_context(mbedtls_pk_ec(pk_ctx),
        (mbedtls_ecdsa_context *)public_key_);
    if (rc != 0) {
        std::string msg(
            "Crypto Error (sig::PublicKey::Serialize(): "
            "Could not copy ECDSA key context");
        throw Error::RuntimeError(msg);
    }

    // Write NUL-terminated ECDSA public key PEM string
    // of the form "BEGIN PUBLIC KEY"
    rc = mbedtls_pk_write_pubkey_pem(&pk_ctx, pem_str, constants::MAX_PEM_LEN);
    if (rc != 0) {
        mbedtls_pk_free(&pk_ctx);
        std::string msg("Crypto Error (sig::PublicKey::Serialize): "
            "Could not write key PEM string\n");
        throw Error::RuntimeError(msg);
    }

    // Cleanup and create return string
    mbedtls_pk_free(&pk_ctx);

    std::string str((char *)pem_str);
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
    unsigned char obuf[constants::EC_POINT_BYTE_LEN];
    size_t olen;
    int rc;

    if (public_key_ == nullptr) {
        std::string msg("Crypto Error (sig::PublicKey::SerializeXYToHex): "
            "PublicKey is not initialized");
        throw Error::RuntimeError(msg);
    }

    rc = mbedtls_ecp_point_write_binary(
        &((mbedtls_ecdsa_context *)public_key_)->grp,
        &((mbedtls_ecdsa_context *)public_key_)->Q,
        MBEDTLS_ECP_PF_UNCOMPRESSED, &olen, obuf, sizeof (obuf));
    if (rc != 0) {
        std::string msg("Crypto Error (sig::PublicKey::SerializeXYToHex): "
            "Could not write EC point (X,Y) as a hex string");
        throw Error::ValueError(msg);
    }

    std::string hex_string = BinaryToHexString(obuf, olen);
    return hex_string;
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
    int rc;

    // Verify signature against hash and key
    rc = mbedtls_ecdsa_read_signature((mbedtls_ecdsa_context *)public_key_,
        (const unsigned char *)hashMessage.data(), hashMessage.size(),
        (unsigned char *)signature.data(), signature.size());
    switch (rc) {
    case 0:
        return 1; // valid signature
    case MBEDTLS_ERR_ECP_VERIFY_FAILED:
        return 0; // invalid signature
    default:
        return -1; // internal error
    }
}  // pcrypto::sig::PublicKey::VerifySignature
