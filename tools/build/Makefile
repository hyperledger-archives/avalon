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

# SRCDIR defaults to the current directory
# DSTDIR defaults to _dev under the current directory
# Both can be overridden with environment variables
SRCDIR?=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))
DSTDIR?=$(abspath $(SRCDIR)/_dev)

PKGGEN=$(abspath $(SRCDIR)/../rebuild.sh)

PY_VERSION=${shell python3 --version | sed 's/Python \(3\.[0-9]\).*/\1/'}
PYTHON_DIR=$(DSTDIR)/lib/python$(PY_VERSION)/site-packages/

all: template enclavekey packages

clean :
	$(abspath $(SRCDIR)/../clean.sh)

packages :
	$(PKGGEN)

enclavekey :
	openssl genrsa -3 -out $(SRCDIR)/../../enclave.pem 3072

template :
	mkdir -p $(DSTDIR)/opt/tcf/logs

lint:
	cd ../..; ./bin/run_lint

.PHONY : packages template
