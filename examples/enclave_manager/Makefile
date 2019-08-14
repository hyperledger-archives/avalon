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
MOD_VERSION=${shell ../../bin/get_version}

ifndef SGX_MODE
$(error Incomplete configuration, SGX_MODE is not defined)
endif

EGG_FILE=dist/tcf_enclave_manager-${MOD_VERSION}-py${PY_VERSION}-linux-x86_64.egg
SOURCE_DIR=$(shell pwd)
EDL_PATH=$(SOURCE_DIR)/../../tc/sgx/trusted_worker_manager/enclave
ENCLAVE_WRAPPER=$(SOURCE_DIR)/../../tc/sgx/trusted_worker_manager/enclave_wrapper


all : $(EGG_FILE)

$(EGG_FILE) : build_ext
	@echo Build Distribution
	python3 setup.py bdist_egg

build_ext :
	$(SGX_SDK)/bin/x64/sgx_edger8r --untrusted $(EDL_PATH)/enclave.edl --search-path $(SGX_SDK)/include --search-path $(SGX_SSL)/include/ --search-path $(EDL_PATH)
	
	@echo Moving generated edge files	
	mv enclave_u.h $(ENCLAVE_WRAPPER)
	mv enclave_u.c $(ENCLAVE_WRAPPER)
	
	@echo Build build_ext
	python3 setup.py build_ext

build :
	mkdir $@

install:
	@echo INSTALLING EGG FILE =================
	easy_install $(EGG_FILE)

clean:
	rm -f $(addprefix $(ENCLAVE_WRAPPER), /enclave_u.c /enclave_u.h)
	rm -f tcf_enclave_manager/tcf_enclave.py tcf_enclave_manager/tcf_enclave_wrap.cpp
	rm -rf build deps dist *.egg-info
	find . -iname '*.pyc' -delete
	find . -iname '__pycache__' -delete

print_enclave_files:
	@echo $(ENCLAVE_FILES)

.phony : all
.phony : clean
.phone : install
