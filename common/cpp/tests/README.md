<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

Unit Tests
----------
This tst directory contains self-contained tests for C++ source files in
`common/cpp/`, which are mostly cryptographic functions implemented with
OpenSSL.

Dependencies:
-------------
These tests are standalone and depend only on libcrypto from OpenSSL.
Programs are tested in "untrusted" mode ("trusted" mode is for in-enclave
execution).

Test Build and Execution
------------------------

To build the tests type `make` .
This builds several independent test programs, one per common
set or class of functions in the `build/` subdirectory.

To execute the tests type `make test` .
This executes each test program.
Each test prints an error message and exits with a 0 on success or
non-0 on failure.

To remove generated binaries type `make clean` .

Example
-------
```
 $ make
mkdir -p build
g++ -o build/b64test.o -D_UNTRUSTED_ -I..  -I../crypto -I../packages/base64 -c b64test.cpp
. . .
g++ -o build/utiltest build/utiltest.o build/crypto_utils.o build/skenc.o build/types.o build/hex_string.o build/utils.o build/base64.o -lcrypto
$ make test
cd build; ./b64test
/home/dano/git/avalon/common/cpp/tests/build
EVP_DecodeBlock PASSED: SHlwZXJsZWRnZXIgQXZhbG9u --> Hyperledger Avalon
base64_decode   PASSED: SHlwZXJsZWRnZXIgQXZhbG9u, length 24 --> len 18
base64_encode   PASSED: length 18 --> len 24
. . .
Test key generation: CreateHexEncodedEncryptionKey()
Key is: 8068670903649550CC4E2E6EA6B78345197E66F98B6D02DC5EE578BF811626E6
PASSED: CreateHexEncodedEncryptionKey()
Test encryption: EncryptData()/DecryptData()
PASSED: EncryptData()/DecryptData()
Crypto utility tests PASSED
$ make clean
rm -f -rf build
```
