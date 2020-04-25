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

# Building documentation with Doxygen requires these packages:
# - make
# - doxygen (for doxygen)
# - texlive-full (for pdflatex and float.sty, used by PDF generation)
# - graphviz (for dot, used to generate dependency graphs)

TARGET=refman
PDF_TARGET=$(TARGET)/latex/refman.pdf
REPO=https://github.com/hyperledger/avalon/blob/master/
REPO_DOCS=$(REPO)docs/
VERSION=$$(../bin/get_version)
# List source directories and files to be documented by Doxygen here.
# Doxyfile's RECURSIVE=YES makes it also use subdirectories.
INPUT=	refman/README.md \
	../common/cpp \
	../common/crypto_utils \
	../common/sgx_workload \
	../common/crypto_utils \
	../common/cpp/crypto \
	../sdk
EXCLUDE= test \
	tests \
	unit_tests \
	__init__.py

all: $(TARGET) $(PDF_TARGET)

Doxyfile: Doxyfile.in
	sed 's|@INPUT@|$(INPUT)|' <$@.in | \
	sed 's|@EXCLUDE@|$(EXCLUDE)|' | \
		sed 's|@VERSION@|'$(VERSION)'|' >$@

# README.md file must be modified for use with Doxygen.
# Doxygen bug: .md links must be obscured to .m%64 or Doxygen will not link it
$(TARGET): README.md Doxyfile
	mkdir -p $(TARGET)
	sed 's|\.\./|$(REPO)|g' <README.md | \
		sed 's|\.md|.m%64|g' | \
		sed 's|\./|$(REPO_DOCS)/|g' >$(TARGET)/README.md
	doxygen Doxyfile

$(PDF_TARGET): $(TARGET)
	make -C $(TARGET)/latex
	if [ -f $(PDF_TARGET) ] ; then ln -f $(PDF_TARGET) $(TARGET) ; fi

clean:
	rm -rf Doxyfile $(TARGET) $(PDF_TARGET)

.PHONY: all
.PHONY: clean
