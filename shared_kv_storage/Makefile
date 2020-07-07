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

SUBDIRS = db_store
PY_VERSION=${shell python3 --version | sed 's/Python \(3\.[0-9]\).*/\1/' | tr -d .}
MOD_VERSION=${shell ../bin/get_version}
WHEEL_FILE=dist/kv_storage-${MOD_VERSION}-cp${PY_VERSION}-cp${PY_VERSION}m-linux_x86_64.whl

all : subdirs $(WHEEL_FILE)

subdirs:
	for dir in $(SUBDIRS) ; do $(MAKE) -C $$dir ; done

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

clean: clean-subdirs
	if pip3 uninstall --yes $(WHEEL_FILE); then echo UNINSTALLED $(WHEEL_FILE) WHEEL FILE ; fi
	rm -r kv_storage/remote_lmdb/db_store.py
	rm -r kv_storage/remote_lmdb/db_store_wrap.cpp
	rm -r kv_storage/remote_lmdb/db_store_csv.py
	rm -r kv_storage/remote_lmdb/db_store_csv_wrap.cpp
	rm -rf build deps dist *.egg-info
	find . -iname '*.pyc' -delete
	find . -iname '__pycache__' -delete

clean-subdirs:
	for dir in $(SUBDIRS) ; do $(MAKE) -C $$dir clean ; done

.PHONY : all
.PHONY : clean
.PHONY : install
.PHONY : build_shared_kv
.PHONY : subdirs
.PHONY : clean-subdirs
