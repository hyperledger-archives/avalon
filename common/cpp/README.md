<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

Purpose of C++ Common Hyperledger Avalon Code
=============================================

The cpp directory contains C++ source code shared by untrusted and trusted
(Intel SGX Enclave) Hyperledger Avalon code.

Dependencies:
-------------
1. OpenSSL 1.1
https://www.openssl.org/

2. Intel SGX OpenSSL library built from OpenSSL 1.1
https://github.com/intel/intel-sgx-ssl

3. Intel SGX SDK
https://software.intel.com/en-us/sgx-sdk/download

Source Directories
------------------

* `.` <br />
   \*.cpp,\*.h error handling, data conversion, utilities,
   and common types
* `crypto/` <br />
   \*.cpp,\*.h for OpenSSL-based cryptographic functions.
   For more information, see
   [crypto/README.md](crypto/README.md)
* `packages/base64/` <br />
   \*.cpp,\*.h of Renee Nyffinger base64 encoding/decoding
* `packages/parson/` <br />
   \*.cpp,\*.h of Parson JSON encoding/decoding
* `tests/` <br />
  \*.cpp,\*.h of standalone unit test programs for these
   common cpp source files.
   For more information, see
   [tests/README.md](tests/README.md)

Python Wrapper
--------------
The Python SWIG wrapper exports the functions and classes defined in crypto.h,
tcf_error.h and types.h.
Several classes and functions are renamed.
Check `common/python/crypto_utils/crypto/crypto.i` for details.
