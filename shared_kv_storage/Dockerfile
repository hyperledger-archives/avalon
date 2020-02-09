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

FROM ubuntu:bionic

# Ignore timezone prompt in apt
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y -q \
    build-essential \
    ca-certificates \
    cmake \
    make \
    pkg-config \
    cmake \
    python3-dev \
    python3-pip \
    python3-requests \
    python3-colorlog \
    python3-twisted \
    python3-toml \
    swig \
    software-properties-common \
    curl \
    wget \
    liblmdb-dev \
 && apt-get -y -q upgrade \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade setuptools

ENV TCF_HOME=/project/avalon

# Make Python3 default
RUN ln -sf /usr/bin/python3 /usr/bin/python

COPY . /project/avalon/

# Build lmdb c++ module
RUN cd /project/avalon/shared_kv_storage/db_store/packages \
   && mkdir -p build \
   && cd build \
   && cmake .. \
   && make


# Build lmdb server module next.

WORKDIR /project/avalon/shared_kv_storage/

RUN echo "Building avalon lmdb server\n" \
   && make \
   && make install

