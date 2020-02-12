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

FROM ubuntu:bionic as base_image

# Ignore timezone prompt in apt
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y -q \
    ca-certificates \
    python3-requests \
    python3-colorlog \
    python3-twisted \
    python3-toml \
    curl \
    wget \
    liblmdb-dev \
 && apt-get -y -q upgrade \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Make Python3 default
RUN ln -sf /usr/bin/python3 /usr/bin/python

#------------------------------------------------------------------------------
# Build Shared KV intermediate docker image.
FROM base_image as build_image

RUN apt-get update \
 && apt-get install -y -q \
    build-essential \
    software-properties-common \
    pkg-config \
    cmake \
    make \
    python3-dev \
    python3-pip \
    swig

RUN pip3 install --upgrade setuptools

ENV TCF_HOME=/project/avalon

# Copy only required files for building shared KV build image.
COPY VERSION /project/avalon/
COPY ./bin /project/avalon/bin
COPY ./common/cpp /project/avalon/common/cpp
COPY ./shared_kv_storage /project/avalon/shared_kv_storage

# Build lmdb c++ module
RUN cd /project/avalon/shared_kv_storage/db_store/packages \
   && mkdir -p build \
   && cd build \
   && cmake .. \
   && make

# Build shared KV module.
WORKDIR /project/avalon/shared_kv_storage/
RUN echo "Building avalon Shared KV" \
   && make 

#------------------------------------------------------------------------------
# Build final image and install Shared KV module.
FROM base_image as final_image

ENV TCF_HOME=/project/avalon

WORKDIR /project/avalon/shared_kv_storage/

# Copy required build artifacts from build_image.
COPY --from=build_image /project/avalon/shared_kv_storage/dist/*.whl dist/
COPY --from=build_image /project/avalon/shared_kv_storage/lmdb_config.toml \
     lmdb_config.toml

# Installing wheel file requires python3-pip package.
# But python3-pip package will increase size of final docker image.
# So remove python3-pip package and dependencies after installing wheel file.
RUN apt-get update \
 && apt-get install -y -q python3-pip \
 && echo "Install Shared KV package\n" \
 && pip3 install dist/*.whl \
 && echo "Remove unused packages from image\n" \
 && apt-get autoremove --purge -y -q python3-pip \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

