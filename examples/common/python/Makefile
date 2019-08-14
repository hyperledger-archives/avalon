# Copyright 2019 Intel Corporation
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
MOD_VERSION=${shell ../../../bin/get_version}

EGG_FILE=dist/tcf_examples_common-${MOD_VERSION}-py${PY_VERSION}-linux-x86_64.egg
SOURCE_DIR=$(shell pwd)


all : $(EGG_FILE)

$(EGG_FILE) : build_ext
	@echo Build Distribution
	python3 setup.py bdist_egg
	
build_ext :
	@echo Build build_ext
	python3 setup.py build_ext

build :
	mkdir $@
	cd $@ 

install:
	@echo INSTALLING EGG FILE =================
	easy_install $(EGG_FILE)

clean:
	rm -rf build deps dist *.egg-info
	rm -f crypto/crypto.py crypto/crypto_wrap.cpp
	find . -iname '*.pyc' -delete
	find . -iname '__pycache__' -delete

.phony : all
.phony : clean
.phone : install

