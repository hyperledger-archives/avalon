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

#include "skenc.h"
#include <openssl/err.h>
#include <openssl/pem.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <algorithm>
#include <memory>
#include <vector>
#include "base64.h"  // simple base64 enc/dec routines
#include "crypto_shared.h"
#include "crypto_utils.h"
#include "error.h"
#include "hex_string.h"

/***Conditional compile untrusted/trusted***/

#if _UNTRUSTED_

#include <openssl/crypto.h>
#include <stdio.h>
#else
#include "tSgxSSL_api.h"
#endif

namespace pcrypto = tcf::crypto;

/***END Conditional compile untrusted/trusted***/

// Typedefs for memory management
// Specify type and destroy function type for unique_ptrs
typedef std::unique_ptr<BIO, void (*)(BIO*)> BIO_ptr;
typedef std::unique_ptr<EVP_CIPHER_CTX, void (*)(EVP_CIPHER_CTX*)> CTX_ptr;
typedef std::unique_ptr<BN_CTX, void (*)(BN_CTX*)> BN_CTX_ptr;
typedef std::unique_ptr<BIGNUM, void (*)(BIGNUM*)> BIGNUM_ptr;

// Error handling
namespace Error = tcf::error;

namespace constants = tcf::crypto::constants;

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Generate symmetric authenticated encryption key
// throws RuntimeError
ByteArray pcrypto::skenc::GenerateKey() {
    return pcrypto::RandomBitString(constants::SYM_KEY_LEN);
}  // pcrypto::skenc::GenerateKey

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Generate symmetric authenticated encryption IV
// throws RuntimeError
ByteArray pcrypto::skenc::GenerateIV(const std::string& IVstring) {
    // generate random IV if no input
    if (IVstring.compare("") == 0)
        return pcrypto::RandomBitString(constants::IV_LEN);
    // else use IVstring
    ByteArray hash(SHA256_DIGEST_LENGTH);
    SHA256((const unsigned char*)IVstring.data(), IVstring.size(), hash.data());
    hash.resize(constants::IV_LEN);
    return hash;
}  // pcrypto::skenc::GenerateIV

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Encrypt message.data() using authenticated encryption
// throws RuntimeError, ValueError
ByteArray pcrypto::skenc::EncryptMessage(
    const ByteArray& key, const ByteArray& iv, const ByteArray& message) {
    unsigned char tag[constants::TAG_LEN];
    int len;
    int ct_len;
    int pt_len = message.size();
    unsigned char* pt = (unsigned char*)message.data();
    int ct_buf_len = pt_len + EVP_MAX_BLOCK_LENGTH;

    ByteArray ct(ct_buf_len);

    if (key.size() != constants::SYM_KEY_LEN) {
        std::string msg("Crypto Error (EncryptMessage): Wrong AES-GCM key length");
        throw Error::ValueError(msg);
    }

    if (iv.size() != constants::IV_LEN) {
        std::string msg("Crypto Error (EncryptMessage): Wrong AES-GCM IV length");
        throw Error::ValueError(msg);
    }

    if (message.size() == 0) {
        std::string msg("Crypto Error (EncryptMessage): Cannot encrypt the empty message");
        throw Error::ValueError(msg);
    }

    CTX_ptr context(EVP_CIPHER_CTX_new(), EVP_CIPHER_CTX_free);
    if (!context) {
        std::string msg(
            "Crypto Error (EncryptMessage): OpenSSL could not create "
            "new EVP_CIPHER_CTX");
        throw Error::RuntimeError(msg);
    }

    if (EVP_EncryptInit_ex(context.get(), EVP_aes_256_gcm(), NULL, NULL, NULL) != 1) {
        std::string msg(
            "Crypto Error (EncryptMessage): OpenSSL could not "
            "initialize EVP_CIPHER_CTX with "
            "AES-GCM");
        throw Error::RuntimeError(msg);
    }

    if (EVP_EncryptInit_ex(context.get(), NULL, NULL, (const unsigned char*)key.data(),
            (const unsigned char*)iv.data()) != 1) {
        std::string msg(
            "Crypto Error (EncryptMessage): OpenSSL could not "
            "initialize AES-GCM key and IV");
        throw Error::RuntimeError(msg);
    }

    if (EVP_EncryptUpdate(context.get(), ct.data(), &len, pt, pt_len) != 1) {
        std::string msg(
            "Crypto Error (EncryptMessage): OpenSSL could not update "
            "AES-GCM encryption");
        throw Error::RuntimeError(msg);
    }
    ct_len = len;
    if (EVP_EncryptFinal_ex(context.get(), ct.data() + len, &len) != 1) {
        std::string msg(
            "Crypto Error (EncryptMessage): OpenSSL could not finalize "
            "AES-GCM encryption");
        throw Error::RuntimeError(msg);
    }
    ct_len += len;

    if (EVP_CIPHER_CTX_ctrl(context.get(), EVP_CTRL_GCM_GET_TAG, constants::TAG_LEN, tag) != 1) {
        std::string msg("Crypto Error (EncryptMessage): OpenSSL could not get AES-GCM TAG");
        throw Error::RuntimeError(msg);
    }
    ct.resize(ct_len);
    ByteArray out;
    // build output string - Add cipter text and append tag.
    out.insert(out.end(), ct.begin(), ct.end());
    out.insert(out.end(), tag, tag + constants::TAG_LEN);

    return out;
}  // pcrypto::skenc::EncryptMessage

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Encrypt message.data() using authenticated encryption with random IV
// prepended to ciphertext
// throws RuntimeError, ValueError
ByteArray pcrypto::skenc::EncryptMessage(const ByteArray& key, const ByteArray& message) {
    if (message.size() == 0) {
        std::string msg("Crypto Error (EncryptMessage): Cannot encrypt the empty message");
        throw Error::ValueError(msg);
    }

    if (key.size() != constants::SYM_KEY_LEN) {
        std::string msg("Crypto Error (EncryptMessage): Wrong AES-GCM key length");
        throw Error::ValueError(msg);
    }

    ByteArray iv = pcrypto::skenc::GenerateIV();
    ByteArray ct = pcrypto::skenc::EncryptMessage(key, iv, message);
    ct.insert(ct.begin(), iv.begin(), iv.end());
    return ct;
}  // pcrypto::skenc::EncryptMessage

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Decrypt message.data() using authenticated decryption.
// throws RuntimeError, ValueError, CryptoError
ByteArray pcrypto::skenc::DecryptMessage(
    const ByteArray& key, const ByteArray& iv, const ByteArray& message) {
    int res;
    unsigned char* ct = (unsigned char*)message.data();
    int len;
    int ct_len = message.size();
    int pt_len = ct_len - constants::TAG_LEN;
    int pt_buf_len = ct_len;
    ByteArray pt(pt_buf_len);
    if (key.size() != constants::SYM_KEY_LEN) {
        std::string msg("Crypto Error (DecryptMessage): Wrong AES-GCM key length");
        throw Error::ValueError(msg);
    }

    if (iv.size() != constants::IV_LEN) {
        std::string msg("Crypto Error (DecryptMessage): Wrong AES-GCM IV length");
        throw Error::ValueError(msg);
    }

    if (message.size() < constants::TAG_LEN) {
        std::string msg(
            "Crypto Error (DecryptMessage): AES-GCM message smaller "
            "than minimum length (TAG "
            "length)");
        throw Error::ValueError(msg);
    }

    CTX_ptr context(EVP_CIPHER_CTX_new(), EVP_CIPHER_CTX_free);
    if (!context) {
        std::string msg(
            "Crypto Error (DecryptMessage): OpenSSL could not create "
            "new EVP_CIPHER_CTX");
        throw Error::RuntimeError(msg);
    }

    if (!EVP_DecryptInit_ex(context.get(), EVP_aes_256_gcm(), NULL, NULL, NULL)) {
        std::string msg(
            "Crypto Error (DecryptMessage): OpenSSL could not "
            "initialize EVP_CIPHER_CTX with "
            "AES-GCM");
        throw Error::RuntimeError(msg);
    }

    if (!EVP_DecryptInit_ex(context.get(), NULL, NULL, (const unsigned char*)key.data(),
            (const unsigned char*)iv.data())) {
        std::string msg(
            "Crypto Error (DecryptMessage): OpenSSL could not "
            "initialize AES-GCM key and IV");
        throw Error::RuntimeError(msg);
    }

    if (!EVP_DecryptUpdate(
            context.get(), pt.data(), &len, ct, ct_len - constants::TAG_LEN)) {
        std::string msg(
            "Crypto Error (DecryptMessage): OpenSSL could not decrypt "
            "with AES-GCM");
        throw Error::RuntimeError(msg);
    }
    pt_len = len;

    if (!EVP_CIPHER_CTX_ctrl(context.get(), EVP_CTRL_GCM_SET_TAG, constants::TAG_LEN,
                  ct + ct_len - constants::TAG_LEN)) {
        std::string msg("Crypto Error (DecryptMessage): OpenSSL could not get AES-GCM TAG");
        throw Error::RuntimeError(msg);
    }

    res = EVP_DecryptFinal_ex(context.get(), pt.data() + len, &len);
    if (res < 1) {
        std::string msg(
            "Crypto Error (DecryptMessage): AES_GCM authentication "
            "failed, plaintext is not "
            "trustworthy");
        throw Error::CryptoError(msg);
    } else {
        pt_len += len;
        // build output string
    }
    pt.resize(pt_len);
    return pt;
}  // pcrypto::skenc::DecryptMessage

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Decrypt message.data() using authenticated encryption
// expects IV prepended to message ciphertext and authentication tag
// appended to cipther text.
// message = IV + ciphertext + authentication tag
// throws RuntimeError, ValueError
ByteArray pcrypto::skenc::DecryptMessage(const ByteArray& key, const ByteArray& message) {
    int res;
    unsigned char* ct = (unsigned char*)message.data();
    int len;
    int ct_len = message.size();
    int pt_len = ct_len - constants::TAG_LEN;
    int pt_buf_len = ct_len;
    ByteArray pt(pt_buf_len);

    if (key.size() != constants::SYM_KEY_LEN) {
        std::string msg("Crypto Error (DecryptMessage): Wrong AES-GCM key length");
        throw Error::ValueError(msg);
    }

    if (message.size() < constants::IV_LEN + constants::TAG_LEN) {
        std::string msg(
            "Crypto Error (DecryptMessage): AES-GCM message smaller "
            "than minimum length (IV length + TAG "
            "length)");
        throw Error::ValueError(msg);
    }

    CTX_ptr context(EVP_CIPHER_CTX_new(), EVP_CIPHER_CTX_free);
    if (!context) {
        std::string msg(
            "Crypto Error (DecryptMessage): OpenSSL could not create "
            "new EVP_CIPHER_CTX");
        throw Error::RuntimeError(msg);
    }

    if (!EVP_DecryptInit_ex(context.get(), EVP_aes_256_gcm(), NULL, NULL, NULL)) {
        std::string msg(
            "Crypto Error (DecryptMessage): OpenSSL could not "
            "initialize EVP_CIPHER_CTX with "
            "AES-GCM");
        throw Error::RuntimeError(msg);
    }

    if (!EVP_DecryptInit_ex(context.get(), NULL, NULL, (const unsigned char*)key.data(),
            (const unsigned char*)message.data())) {
        std::string msg(
            "Crypto Error (DecryptMessage): OpenSSL could not "
            "initialize AES-GCM key and IV");
        throw Error::RuntimeError(msg);
    }

    if (!EVP_DecryptUpdate(context.get(), pt.data(), &len,
            ct + constants::IV_LEN,
            ct_len - constants::IV_LEN - constants::TAG_LEN)) {
        std::string msg(
            "Crypto Error (DecryptMessage): OpenSSL could not decrypt "
            "with AES-GCM");
        throw Error::RuntimeError(msg);
    }
    pt_len = len;

    if (!EVP_CIPHER_CTX_ctrl(
            context.get(), EVP_CTRL_GCM_SET_TAG, constants::TAG_LEN,
            ct + ct_len - constants::TAG_LEN)) {
        std::string msg("Crypto Error (DecryptMessage): OpenSSL could not get AES-GCM TAG");
        throw Error::RuntimeError(msg);
    }

    res = EVP_DecryptFinal_ex(context.get(), pt.data() + len, &len);
    if (res < 1) {
        std::string msg(
            "Crypto Error (DecryptMessage): AES_GCM authentication "
            "failed, plaintext is not "
            "trustworthy");
        throw Error::CryptoError(msg);
    } else {
        pt_len += len;
        // build output string
    }
    pt.resize(pt_len);
    return pt;
}  // pcrypto::skenc::EncryptMessage
