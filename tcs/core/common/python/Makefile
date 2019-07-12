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

PY_VERSION=${shell python3 --version | sed 's/Python \(3\.[0-9]\).*/\1/'}
MOD_VERSION=${shell ../../../../bin/get_version}

ifndef SGX_MODE
$(error Incomplete configuration, SGX_MODE is not defined)
endif

EGG_FILE=dist/tcf_eservice-${MOD_VERSION}-py${PY_VERSION}-linux-x86_64.egg
SOURCE_DIR=$(shell pwd)
ENCLAVE_LIB=$(SOURCE_DIR)/../../tcs_trusted_worker_manager/enclave/deps/bin/libtcf-enclave.signed.so
EDL_PATH=$(SOURCE_DIR)/../../tcs_trusted_worker_manager/enclave
ENCLAVE_WRAPPER=$(SOURCE_DIR)/../../tcs_trusted_worker_manager/enclave_wrapper

SWIG_FILES = \
	$(ENCLAVE_WRAPPER)/tcf_enclave_internal.i \
	crypto/crypto.i

SWIG_TARGET = $(ENCLAVE_WRAPPER)/tcf_enclave_internal.py

all : $(EGG_FILE)

$(EGG_FILE) : $(SWIG_TARGET)
	@echo Build Distribution
	python3 setup.py bdist_egg

$(SWIG_TARGET) : $(SWIG_FILES) $(ENCLAVE_LIB)
	
	$(SGX_SDK)/bin/x64/sgx_edger8r --untrusted $(EDL_PATH)/enclave.edl --search-path $(SGX_SDK)/include --search-path $(SGX_SSL)/include/ --search-path $(EDL_PATH)
	
	@echo Moving generated edge files	
	mv enclave_u.h $(ENCLAVE_WRAPPER)
	mv enclave_u.c $(ENCLAVE_WRAPPER)
	
	@echo Build build_ext
	python3 setup.py build_ext

build :
	mkdir $@
	cd $@ ; cmake .. -G "Unix Makefiles"

install: $(EGG_FILE)
	@echo INSTALLING EGG FILE =================
	easy_install $<

test: install
	(cd tests; python3 test-secrets.py)
	(cd tests; python3 test-request.py)

clean:
	rm -f $(addprefix $(ENCLAVE_WRAPPER), /tcf_enclave_internal.py /tcf_enclave_internal_wrap.cpp /enclave_u.c /enclave_u.h)
	rm -f common/crypto.py common/crypto_wrap.cpp
	rm -rf build deps dist *.egg-info
	find . -iname '*.pyc' -delete
	find . -iname '__pycache__' -delete

print_enclave_files:
	@echo $(ENCLAVE_FILES)

.phony : all
.phony : clean
.phony : enclave
.phone : install
.phony : test
.phony : print_enclave_files
.phony : info
