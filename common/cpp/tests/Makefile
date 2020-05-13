# Copyright 2020 Intel Corporation
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

CPPFLAGS= -D_UNTRUSTED_ -DCRYPTOLIB_OPENSSL
CPPFLAGS+= -I..  -I../crypto -I../packages/base64
LDFLAGS=-lcrypto

# To use Mbed TLS instead of the default OpenSSL, define CRYPTOLIB_MBEDTLS=1
# For example: CRYPTOLIB_MBEDTLS=1 make
ifdef CRYPTOLIB_MBEDTLS
	CPPFLAGS+= -DCRYPTOLIB_MBEDTLS
	LDFLAGS+=-lmbedcrypto
endif

UTILTESTOBJS= build/crypto_utils.o build/crypto_utils_encrypt.o \
		build/skenc.o build/types.o \
		build/hex_string.o build/utils.o build/base64.o

build/%: build/%.o
	g++ -o $@ $^ $(LDFLAGS)

build/%.o: %.cpp
	g++ -o $@ $(CPPFLAGS) -c $^

build/%.o: ../%.cpp
	g++ -o $@ $(CPPFLAGS) -c $^

build/%.o: ../crypto/%.cpp
	g++ -o $@ $(CPPFLAGS) -c $^

build/%.o: ../packages/base64/%.cpp
	g++ -o $@ $(CPPFLAGS) -c $^


all: build build/b64test build/certtest build/secrettest \
	build/signtest build/verifytest build/pktest build/utiltest

build:
	mkdir -p $@

build/b64test: build/b64test.o build/base64.o build/utils.o
	g++ -o $@ $@.o         build/base64.o build/utils.o $(LDFLAGS)

build/certtest: build/certtest.o build/verify_certificate.o
	g++ -o $@ $@.o           build/verify_certificate.o $(LDFLAGS)

build/pktest: build/pktest.o build/pkenc_private_key.o build/pkenc_public_key.o
	g++ -o $@ $@.o build/pkenc_private_key.o build/pkenc_public_key.o \
 		$(LDFLAGS)

build/signtest: build/signtest.o build/sig_private_key.o build/sig_public_key.o
	g++ -o $@ $@.o build/sig_private_key.o build/sig_public_key.o \
		$(LDFLAGS)

build/secrettest: build/secrettest.o $(UTILTESTOBJS)
	g++ -o $@ $@.o $(UTILTESTOBJS) $(LDFLAGS)

build/verifytest: build/verifytest.o build/verify_signature.o
	g++ -o $@ $@.o build/verify_signature.o $(LDFLAGS)

build/utiltest: build/utiltest.o $(UTILTESTOBJS)
	g++ -o $@ $@.o $(UTILTESTOBJS) $(LDFLAGS)

test:
	cd build; ./b64test
	cd build; ./certtest
	cd build; ./pktest
	cd build; ./signtest
	cd build; ./secrettest
	cd build; ./verifytest
	cd build; ./utiltest

clean:
	$(RM) -rf build

.PHONY: all test clean
