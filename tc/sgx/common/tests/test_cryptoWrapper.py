# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import crypto.crypto as crypto
import logging
import sys
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

# TEST ECDSA
try:
    esk = crypto.SIG_PrivateKey()
    esk.Generate()
    epk = esk.GetPublicKey()
except Exception as exc:
    logger.error(
        "ERROR: Signature Private and Public keys generation test failed: ",
        exc)
    sys.exit(-1)
logger.debug("Signature Private and Public keys generation test successful!")

try:
    eskString = esk.Serialize()
    epkString = epk.Serialize()
    hepkString = epk.SerializeXYToHex()
    esk1 = crypto.SIG_PrivateKey(eskString)
    epk1 = crypto.SIG_PublicKey(epkString)
    eskString1 = esk1.Serialize()
    epkString1 = epk1.Serialize()
    esk2 = crypto.SIG_PrivateKey()
    esk2.Generate()
    epk2 = crypto.SIG_PublicKey(esk2)
    eskString = esk.Serialize()
    esk2.Deserialize(eskString1)
    epk2.Deserialize(epkString1)
    eskString2 = esk2.Serialize()
    epkString2 = epk2.Serialize()
except Exception as exc:
    logger.error(
        "ERROR: Signature Private and Public keys serialize/deserialize " +
        "test failed: ", exc)
    sys.exit(-1)
logger.debug(
    "Signature Private and Public keys serialize/deserialize test successful!")

try:
    esk1.Deserialize(epkString1)
    logger.error(
        "ERROR: Signature invalid private key deserialize test failed: " +
        "not detected.")
    sys.exit(-1)
except Exception as exc:
    if (type(exc) == ValueError):
        logger.debug(
            "Signature invalid private key deserialize test successful!")
    else:
        logger.error(
            "ERROR: Signature invalid private key deserialize test failed: ",
            exc)
        sys.exit(-1)

try:
    epk1.Deserialize(eskString1)
    logger.error(
        "ERROR: Signature invalid public key deserialize test failed: " +
        "not detected.")
    sys.exit(-1)
except Exception as exc:
    if (type(exc) == ValueError):
        logger.debug(
            "Signature invalid public key deserialize test successful!")
    else:
        logger.error(
            "ERROR: Signature invalid public key deserialize test failed: ",
            exc)
        sys.exit(-1)

try:
    msg = b'A message!'
    sig = esk.SignMessage(msg)
    res = epk.VerifySignature(msg, sig)
except Exception as exc:
    logger.error("ERROR: Signature creation and verification test failed: ",
                 exc)
    sys.exit(-1)
if (res == 1):
    logger.debug("Signature creation and verification test successful!")
else:
    logger.error("ERROR: Signature creation and verification test failed: " +
                 "signature does not verify.")
    exit(-1)

try:
    res = epk.VerifySignature(msg, bytes("invalid signature", 'ascii'))
except Exception as exc:
    logger.error("ERROR: Invalid signature detection test failed: ", exc)
    sys.exit(-1)
if (res != 1):
    logger.debug("Invalid signature detection test successful!")
else:
    logger.error("ERROR: Invalid signature detection test failed.")
    exit(-1)

# TEST RSA
try:
    rsk = crypto.PKENC_PrivateKey()
    rsk.Generate()
    rpk = crypto.PKENC_PublicKey(rsk)
except Exception as exc:
    logger.error("ERROR: Asymmetric encryption Private and Public keys " +
                 "generation test failed: ", exc)
    sys.exit(-1)
logger.debug("Asymmetric encryption Private and Public keys " +
             "generation test successful!")

try:
    rskString = rsk.Serialize()
    rpkString = rpk.Serialize()
    rsk1 = crypto.PKENC_PrivateKey(rskString)
    rpk1 = crypto.PKENC_PublicKey(rpkString)
    rskString1 = rsk1.Serialize()
    rpkString1 = rpk1.Serialize()
    rsk2 = crypto.PKENC_PrivateKey()
    rsk2.Generate()
    rpk2 = crypto.PKENC_PublicKey(rsk2)
    rsk2.Deserialize(rskString1)
    rpk2.Deserialize(rpkString1)
    rskString2 = rsk2.Serialize()
    rpkString2 = rpk2.Serialize()
except Exception as exc:
    logger.error("ERROR: Asymmetric encryption Private and Public keys " +
                 "serialize/deserialize test failed: ", exc)
    sys.exit(-1)

try:
    rsk1.Deserialize(rpkString1)
    logger.error("error: Asymmetric encryption invalid private key " +
                 "deserialize test failed: not detected.")
    sys.exit(-1)
except Exception as exc:
    if (type(exc) == ValueError):
        logger.debug("Asymmetric encryption invalid private key " +
                     "deserialize test successful!")
    else:
        logger.error("error: Asymmetric encryption invalid private key " +
                     "deserialize test failed: ", exc)
        sys.exit(-1)

try:
    rpk1.Deserialize(rskString1)
    logger.error("error: Asymmetric encryption invalid public key " +
                 "deserialize test failed: not detected.")
    sys.exit(-1)
except Exception as exc:
    if (type(exc) == ValueError):
        logger.debug("Asymmetric encryption invalid public key deserialize " +
                     "test successful!")
    else:
        logger.error("error: Asymmetric encryption invalid public key " +
                     "deserialize test failed: ", exc)
        sys.exit(-1)


try:
    ciphertext = rpk.EncryptMessage(msg)
    plaintext = rsk.DecryptMessage(ciphertext)
except Exception as exc:
    logger.error("ERROR: Asymmetric encryption/decryption test failed: ", exc)
    sys.exit(-1)

if (bytearray(plaintext) == bytearray(msg)):
    logger.debug("Asymmetric encryption/decryption test successful!")
else:
    logger.error("ERROR: Asymmetric encryption/decryption failed.")
    exit(-1)

# TEST AES-GCM
try:
    iv = crypto.SKENC_GenerateIV()
except Exception as exc:
    logger.error("ERROR: Symmetric encryption iv generation test failed: ",
                 exc)
    sys.exit(-1)

try:
    key = crypto.SKENC_GenerateKey()
except Exception as exc:
    logger.error("ERROR: Symmetric encryption key generation test failed: ",
                 exc)
    sys.exit(-1)

try:
    crypto.SKENC_EncryptMessage(iv, None, msg)
    logger.error("ERROR: Symmetric encryption invalid key detection test " +
                 "failed: not detected.")
    sys.exit(-1)
except Exception as exc:
    if (type(exc) == ValueError):
        logger.debug(
            "Symmetric encryption invalid key detection test successful!")
    else:
        logger.error("ERROR: Symmetric encryption invalid key detection " +
                     "test failed: ", exc)
        sys.exit(-1)
try:
    crypto.SKENC_EncryptMessage(None, key, msg)
    logger.error("ERROR: Symmetric encryption invalid iv detection " +
                 "test failed: not detected.")
    sys.exit(-1)
except Exception as exc:
    if (type(exc) == ValueError):
        logger.debug(
            "Symmetric encryption invalid iv detection test successful!")
    else:
        logger.error("ERROR: Symmetric encryption invalid iv detection " +
                     "test failed: ", exc)
        sys.exit(-1)

try:
    ciphertext = crypto.SKENC_EncryptMessage(key, iv, msg)
    print(len(ciphertext))
    crypto.SKENC_DecryptMessage(key, iv, ciphertext)
except Exception as exc:
    logger.error("ERROR: Symmetric encryption test failed: ", exc)
    sys.exit(-1)

if (bytearray(plaintext) == bytearray(msg)):
    logger.debug("Symmetric encryption/decryption test successful!")
else:
    logger.error("ERROR:Symmetric encryption/decryption test failed: " +
                 "decrypted text and plaintext mismatch.")
    exit(-1)

c = list(ciphertext)
c[0] = c[0] + 1
ciphertext = tuple(c)
try:
    crypto.SKENC_DecryptMessage(key, iv, ciphertext)
    logger.error("ERROR: Symmetric decryption ciphertext tampering " +
                 "detection test failed: not detected.")
    sys.exit(-1)
except Exception as exc:
    if (type(exc) == ValueError):
        logger.debug("Symmetric decryption ciphertext tampering " +
                     "detection test successful!")
    else:
        logger.error("ERROR: Symmetric decryption ciphertext tampering " +
                     "detection test failed: ", exc)
        sys.exit(-1)

try:
    crypto.SKENC_DecryptMessage(iv, iv, ciphertext)
    logger.error("ERROR: Symmetric decryption invalid key detection test " +
                 "failed: not detected.")
    sys.exit(-1)
except Exception as exc:
    if (type(exc) == ValueError):
        logger.debug(
            "Symmetric decryption invalid key detection test successful!")
    else:
        logger.error("ERROR: Symmetric decryption invalid key detection " +
                     "test failed: ", exc)
        sys.exit(-1)

try:
    crypto.SKENC_DecryptMessage(plaintext, key, ciphertext)
    logger.error("ERROR: Symmetric decryption invalid iv detection test " +
                 "failed: not detected.")
    sys.exit(-1)
except Exception as exc:
    if (type(exc) == ValueError):
        logger.debug(
            "Symmetric decryption invalid iv detection test successful!")
    else:
        logger.error(
            "ERROR: Symmetric decryption invalid iv detection test failed: ",
            exc)
        sys.exit(-1)

try:
    crypto.SKENC_EncryptMessage(None, ciphertext)
    logger.error("ERROR: Symmetric encryption invalid key detection test " +
                 "failed: not detected.")
    sys.exit(-1)
except Exception as exc:
    if (type(exc) == ValueError):
        logger.debug(
            "Symmetric encryption invalid key detection test successful!")
    else:
        logger.error("ERROR: Symmetric encryption invalid key detection " +
                     "test failed: ", exc)
        sys.exit(-1)

try:
    crypto.SKENC_EncryptMessage(None, key, ciphertext)
    logger.error("ERROR: Symmetric encryption invalid iv detection test " +
                 "failed: not detected.")
    sys.exit(-1)
except Exception as exc:
    if (type(exc) == ValueError):
        logger.debug(
            "Symmetric encryption invalid iv detection test successful!")
    else:
        logger.error("ERROR: Symmetric encryption invalid iv detection " +
                     "test failed: ", exc)
        sys.exit(-1)

# Random IV
try:
    ciphertext = crypto.SKENC_EncryptMessage(key, msg)
    crypto.SKENC_DecryptMessage(key, ciphertext)
except Exception as exc:
    logger.error("ERROR: Symmetric encryption (random IV) test failed: ", exc)
    sys.exit(-1)

if (bytearray(plaintext) == bytearray(msg)):
    logger.debug("Symmetric encryption (random IV)/decryption " +
                 "test successful!")
else:
    logger.error("ERROR:Symmetric encryption (random IV)/decryption test " +
                 "failed: decrypted text and plaintext mismatch.")
    exit(-1)

c = list(ciphertext)
c[0] = c[0] + 1
ciphertext = tuple(c)
try:
    crypto.SKENC_DecryptMessage(key, ciphertext)
    logger.error("ERROR: Symmetric decryption (random IV) " +
                 "ciphertext tampering detection test failed: not detected.")
    sys.exit(-1)
except Exception as exc:
    if (type(exc) == ValueError):
        logger.debug("Symmetric decryption (random IV) " +
                     "ciphertext tampering detection test successful!")
    else:
        logger.error("ERROR: Symmetric decryption (random IV) " +
                     "ciphertext tampering detection test failed: ", exc)
        sys.exit(-1)

try:
    crypto.SKENC_DecryptMessage(iv, ciphertext)
    logger.error("ERROR: Symmetric decryption (random IV) " +
                 "invalid key detection test failed: not detected.")
    sys.exit(-1)
except Exception as exc:
    if (type(exc) == ValueError):
        logger.debug("Symmetric decryption (random IV) " +
                     "invalid key detection test successful!")
    else:
        logger.error("ERROR: Symmetric decryption (random IV) " +
                     "invalid key detection test failed: ", exc)
        sys.exit(-1)

try:
    iv = crypto.SKENC_GenerateIV("A message")
except Exception as exc:
    logger.error("ERROR: Symmetric encryption deterministic iv generation " +
                 "test failed: ", exc)
    sys.exit(-1)
logger.debug(
    "Symmetric encryption deterministic iv generation test successful!")

try:
    rand = crypto.random_bit_string(16)
except Exception as exc:
    logger.error("ERROR: Random number generation failed: ", exc)
    sys.exit(-1)
logger.debug("Random number generation successful!")

hash = crypto.compute_message_hash(rand)
bhash = bytearray(hash)
b64hash = crypto.byte_array_to_base64(bhash)
logger.debug("Hash computed!")
crypto.base64_to_byte_array(b64hash)
logger.debug("SWIG CRYPTO_WRAPPER TEST SUCCESSFUL!")
sys.exit(0)
