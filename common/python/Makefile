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

# Get python version
PY_VERSION=${shell python3 --version | sed 's/Python \(3\.[0-9]\).*/\1/' | cut -b 1}
MOD_VERSION=${shell ../../bin/get_version}

# Format of wheel package is <pkg_name>-{python-tag}-{abi-tag}-{platform}
WHEEL_FILE=dist/avalon_common-${MOD_VERSION}-py${PY_VERSION}-none-any.whl
SOURCE_DIR=$(shell pwd)


all : $(WHEEL_FILE)

$(WHEEL_FILE) :
	@echo Build Distribution
	python3 setup.py bdist_wheel
	
build :
	mkdir $@

install:
	@echo INSTALLING WHEEL FILE =================
	pip3 install $(WHEEL_FILE)

clean:
	if pip3 uninstall --yes $(WHEEL_FILE); then echo UNINSTALLED $(WHEEL_FILE) WHEEL FILE ; fi
	rm -rf build deps dist *.egg-info
	find . -iname '*.pyc' -delete
	find . -iname '__pycache__' -delete

.PHONY : all
.PHONY : clean
.PHONY : install

