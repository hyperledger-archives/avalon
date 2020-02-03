<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

Purpose of Common
-----------------
The common directory contains source code shared by untrusted and trusted (SGX Enclave) code.

Dependencies:
-------------
1. OpenSSL 1.1
https://www.openssl.org/

2. SGX OpenSSL library built from OpenSSL 1.1
https://github.com/intel/intel-sgx-ssl

3. SGX SDK
https://software.intel.com/en-us/sgx-sdk/download

Source Directories
------------------

Dir                     Content
---------------------   ------------------------------------------------------
`crypto/`               \*.cpp,\*.h for OpenSSL based crypto functions.
                        For more information, see
                        [crypto/README.md](crypto/README.md)

`.`                     \*.cpp,\*.h error handling and common types

`packages/base64/`      \*.cpp,\*.h of Renee Nyffinger base64 encoding/decoding

`packages/parson/`      \*.cpp,\*.h of Parson JSON  encoding/decoding

Python Wrapper
--------------
The Python SWIG wrapper exports the functions and classes defined in crypto.h,
tcf_error.h and types.h.
Several classes and functions are renamed.
Check `common/python/crypto_utils/crypto/crypto.i` for details.
