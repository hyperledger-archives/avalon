<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->


Common Crypto library documentation
===================================

Software components required
----------------------------

OpenSSL 1.1 library and SGX OpenSSL library built from OpenSSL 1.1:

https://www.openssl.org/

https://github.com/intel/intel-sgx-ssl

List of cryptographic primitives used
-------------------------------------

Primitive                 Algorithm             Keysize                     Comments
------------------------- ------------------    --------------------------- ----------------
Digital signature         ECDSA NISTP256        256                         Not PQ resistant
Asymmetric key encryption PKCS1 OAEP PADDING    2048 (3072 recommended)     Not PQ resistant
Authenticated encryption  AES-GCM               128 (256 for PQ resistance)
Cryptographic hash        SHA256                256                         Not PQ resistant
Crypto random bitstring   OpenSSL IMPL

Implementation of elements: cryptographic keys, signature, ciphertexts, plaintexts, hashes and random bitstrings
-------------------------------------------------------------------------------------------------------------

Element                   Implementation       Representation    Serialize/Deserialize function?
----------------------    --------------       --------------    ------------------------------------------------
ECDSA public key          C++ class            Custom object     Yes, PEM encoding and 65 byte Bitcoin Hex format
ECDSA private key         C++ class            Custom object     Yes, PEM encoding
ECDSA signature           C++ string           DER binary        No, user defined
RSA public key            C++ class            Custom object     Yes, PEM encoding
RSA private key           C++ class            Custom object     Yes, PEM encoding
RSA ciphertext            C++ string           raw binary        No, user defined
RSA plaintext             C++ string           raw binary        No, user defined
AES-GCM key               C++ string           raw binary        No, user defined
AES-GCM iv                C++ string           raw binary        No, user defined
AES-GCM ciphertext+tag    C++ string           raw binary        No, user defined
AES-GCM plaintext         C++ string           raw binary        No, user defined
SHA256 hash               C++ string           raw binary        No, user defined
Crypto random bitstring   C++ string           raw binary        No, user defined

Security notes
--------------
When using of AES-GCM inside SGX enclaves to preserve confidentiality and integrity of data to be stored
outside of the SGX enclaves a different unique or random 12-byte IV must be used for each encrypted message.
At most 2^32 distinct IVs can be used until the key needs to be regenerated for security. This limitation can possibly be mitigated in the future by using alternatives to AES-GCM like
AES-GCM SIV.
