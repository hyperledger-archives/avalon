<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

Common Crypto library documentation
===================================

This `common/cpp/crypto/` directory contains cryptographic code used by untrusted and
trusted (SGX Enclave) code.

This code is written in C++, but a Python wrapper is also available (see [../README.md](../README.md))

Avalon applications are free to use third-party cryptographic implementations (such as what a
programming language binding may provide) or the cryptographic interfaces provided here.


Software Components Required
----------------------------

OpenSSL 1.1 library and SGX OpenSSL library built from OpenSSL 1.1:

* https://www.openssl.org/
* https://github.com/intel/intel-sgx-ssl


Cryptographic Primitives Used
-----------------------------

| Primitive | Algorithm | Keysize | Comments |
| --------- | --------- | ------- | -------- |
| Digital signature | ECDSA-SECP256K1 | 256 | (1) (2) |
| Asymmetric encryption | RSA-OAEP | 3072 | (1) |
| Authenticated encryption | AES-GCM | 256 | 96b IV, 128b tag |
| Digest | SHA-256 | 256 | (2) |
| Digest | KECCACK | 256 | (2) Differs from SHA-3 |

(1) Not PQ resistant

(2) Blockchain legacy algorithm


Cryptographic Primitive Usage
-----------------------------

* **SHA-256** Computing digests of the work order request and response
* **KECCAK-256** Computing digests of the work order request and response or Ethereum raw transactions Packet bytes
* **AES-GCM-256** Encrypts data items within work order request and response. It also used to encrypt a request digest and custom data encryption keys
* **RSA-OAEP-3072** Encrypt symmetric data encryption keys
* **ECSDA-SECP256K1** Signs work order response digest and worker’s encryption RSA-OAEP public key


Implementation of Cryptographic Elements
----------------------------------------

Cryptographic elements include cryptographic keys, signature, ciphertexts, plaintexts, hashes, and random bitstrings.

| Element | Implementation | Representation | Serialize/Deserialize function? |
| ------- | -------------- | -------------- | ------------------------------- |
| ECDSA public key | C++ class | Custom object | Yes, PEM encoding and 65-byte Bitcoin Hex format |
| ECDSA private key      | C++ class  | Custom object | Yes, PEM encoding     |
| ECDSA signature        | C++ string | DER binary    | No, user defined      |
| RSA public key         | C++ class  | Custom object | Yes, PEM encoding     |
| RSA private key        | C++ class  | Custom object | Yes, PEM encoding     |
| RSA ciphertext         | C++ string | raw binary    | No, user defined      |
| RSA plaintext          | C++ string | raw binary    | No, user defined      |
| AES-GCM key            | C++ string | raw binary    | No, user defined      |
| AES-GCM iv             | C++ string | raw binary    | No, user defined      |
| AES-GCM ciphertext+tag | C++ string | raw binary    | No, user defined      |
| AES-GCM plaintext      | C++ string | raw binary    | No, user defined      |
| SHA-256 digest         | C++ string | raw binary    | No, user defined      |
| Random bitstring       | C++ string | raw binary    | No, user defined      |

Security notes
--------------

* **AES-GCM** When using of AES-GCM inside SGX enclaves to preserve confidentiality
and integrity of data to be stored outside of the SGX enclaves a different unique
or random 12-byte IV must be used for each encrypted message.
At most 2^32 distinct IVs can be used until the key needs to be regenerated for
security. This limitation can possibly be mitigated in the future by using
alternatives to AES-GCM like AES-GCM SIV.
