<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

Purpose of Common
------------------------
The common directory contains source code shared by untrusted and trusted (SGX Enclave) application.

Dependencies:
-------------
1. OpenSSL 1.1
https://www.openssl.org/

2. SGX OpenSSL library built from OpenSSL 1.1
https://github.com/intel/intel-sgx-ssl

3. SGX SDK
https://software.intel.com/en-us/sgx-sdk/download

Directories
-----------

Dir                           Content
----------------------------- -----------------------------------------------------------------------
  crypto/                     .cpp/.h for OpenSSL based crypto functions
  .                           .cpp/.h error handling and common types
  packages/base64/            .cpp/.h of Renee Nyffinger base64 encoding/decoding
  packages/parson/            .cpp/.h of Parson JSON  encoding/decoding
  work_order_interface/       work order interface between enclave and workloads
  tests/                      unit tests for crypto library
  tests/untrusted             test untrusted Crypto library
  tests/trusted               test trusted Crypto library
  tests/trusted/app           trusted Crypto test app
  tests/trusted/enclave       trusted Crypto test enclave

Python Wrapper
-------------------------------------------------------------------------------------------------------
The Python SWIG wrapper exports the functions and classes defined in crypto.h, tcf_error.h and types.h.
Several classes and functions are renamed. Check ../python/tcf/common/crypto.i for the details.
