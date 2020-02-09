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

# Set SGX_MODE default (which can be overridden with an environment variable):

PY_VERSION=${shell python3 --version | sed 's/Python \(3\.[0-9]\).*/\1/' | tr -d .}
MOD_VERSION=${shell ../bin/get_version}

WHEEL_FILE=dist/kv_storage-${MOD_VERSION}-cp${PY_VERSION}-cp${PY_VERSION}m-linux_x86_64.whl

all : $(WHEEL_FILE)

$(WHEEL_FILE) : build_shared_kv
	@echo Build Distribution
	python3 setup.py bdist_wheel

build_shared_kv :
	@echo Build build_ext
	python3 setup.py build_ext

build :
	mkdir $@

install:
	@echo INSTALLING WHEEL FILE =================
	pip3 install $(WHEEL_FILE)

clean:
	pip3 uninstall --yes $(WHEEL_FILE)
	rm -rf kv_storage/remote_lmdb/db_store.py db_store/db_store_wrap.cpp
	rm -rf build deps dist *.egg-info
	find . -iname '*.pyc' -delete
	find . -iname '__pycache__' -delete


.phony : all
.phony : clean
.phone : install
