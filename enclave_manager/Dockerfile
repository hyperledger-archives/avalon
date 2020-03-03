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
# ------------------------------------------------------------------------------

# Description:
#   Builds the environment needed to build Avalon SGX Enclave manager.
#
#  Configuration (build) parameters
#  - proxy configuration: https_proxy http_proxy ftp_proxy
#  - sgx mode:
#

# -------------=== build avalon Enclave Manager image ===-------------
#Build base docker image
FROM ubuntu:bionic as base_image

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y -q \
    ca-certificates \
    python3-toml \
    python3-pip \
    python3-requests \
    python3-colorlog \
    python3-twisted \
 && apt-get -y -q upgrade \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Make Python3 default
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Install setuptools packages using pip because
RUN pip3 install --upgrade json-rpc nose2

# -------------=== Build openssl_image ===-------------

#Build openssl intermediate docker image
FROM ubuntu:bionic as openssl_image

RUN apt-get update \
 && apt-get install -y -q \
    ca-certificates \
    pkg-config \
    make \
    wget \
    tar \
 && apt-get -y -q upgrade \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

# Build ("Untrusted") OpenSSL
RUN OPENSSL_VER=1.1.1d \
 && wget https://www.openssl.org/source/openssl-$OPENSSL_VER.tar.gz \
 && tar -zxf openssl-$OPENSSL_VER.tar.gz \
 && cd openssl-$OPENSSL_VER/ \
 && ./config \
 && THREADS=8 \
 && make -j$THREADS \
 && make test \
 && make install -j$THREADS

#Build Avalon Listener intermediate docker image
FROM base_image as build_image

RUN apt-get update \
 && apt-get install -y -q \
    build-essential \
    software-properties-common \
    pkg-config \
    cmake \
    make \
    git \
    libprotobuf-dev \
    python3-dev \
    swig \
    wget \
    tar \
    libprotobuf-dev \
    curl \
    dh-autoreconf \
    ocaml \
    wget \
    xxd \
    unzip \
    ocamlbuild \
 && apt-get -y -q upgrade \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Install setuptools packages using pip because
RUN pip3 install --upgrade setuptools

# SGX common library and SDK are installed in /opt/intel directory.
# Installation of SGX libsgx-common packages requires /etc/init directory. In docker image this directory doesn't exist.
# Hence creating /etc/init directory.
RUN mkdir -p /opt/intel \
 && mkdir -p /etc/init
WORKDIR /opt/intel

# Install SGX common library
RUN wget https://download.01.org/intel-sgx/sgx-linux/2.7.1/distro/ubuntu18.04-server/libsgx-enclave-common_2.7.101.3-bionic1_amd64.deb \
 && dpkg -i libsgx-enclave-common_2.7.101.3-bionic1_amd64.deb

# Install SGX SDK
RUN SGX_SDK_FILE=sgx_linux_x64_sdk_2.7.101.3.bin \
 && wget https://download.01.org/intel-sgx/sgx-linux/2.7.1/distro/ubuntu18.04-server/$SGX_SDK_FILE \
 && echo "yes" | bash ./$SGX_SDK_FILE \
 && rm $SGX_SDK_FILE \
 && echo ". /opt/intel/sgxsdk/environment" >> /etc/environment

# Copy openssl build artifacts from openssl_image
ENV OPENSSL_VER=1.1.1d
COPY --from=openssl_image /usr/local/ssl /usr/local/ssl
COPY --from=openssl_image /usr/local/bin /usr/local/bin
COPY --from=openssl_image /usr/local/include /usr/local/include
COPY --from=openssl_image /usr/local/lib /usr/local/lib
COPY --from=openssl_image /tmp/openssl-$OPENSSL_VER.tar.gz /tmp/

# Build ("trusted") SGX OpenSSL
# Note: This will compile in HW or SIM mode depending on the

# Note: This will compile in HW or SIM mode depending on the
# availability of /dev/isgx and /var/run/aesmd/aesm.socket

WORKDIR /tmp

# Using specific SGX SSL tag "lin_2.5_1.1.1d" corresponding to
# openSSL version 1.1.1d
RUN ldconfig \
 && ln -s /etc/ssl/certs/* /usr/local/ssl/certs/ \
 && git clone -b lin_2.5_1.1.1d https://github.com/intel/intel-sgx-ssl.git  \
 && . /opt/intel/sgxsdk/environment \
 && (cd intel-sgx-ssl/openssl_source; mv /tmp/openssl-$OPENSSL_VER.tar.gz . ) \
 && (cd intel-sgx-ssl/Linux; \
    if ([ -c /dev/isgx ] && [ -S /var/run/aesmd/aesm.socket ]); then SGX_MODE=HW; \
    else SGX_MODE=SIM; \
    fi; \
    make SGX_MODE=${SGX_MODE} DESTDIR=/opt/intel/sgxssl all test ) \
 && (cd intel-sgx-ssl/Linux; make install ) \
 && rm -rf /tmp/intel-sgx-ssl \
 && echo "SGX_SSL=/opt/intel/sgxssl" >> /etc/environment

COPY . /project/avalon

ARG SGX_MODE
ARG MAKECLEAN
ARG TCF_DEBUG_BUILD

# Environment setup
ENV TCF_HOME=/project/avalon
ENV SGX_SSL=/opt/intel/sgxssl
ENV SGX_SDK=/opt/intel/sgxsdk
ENV PATH=$PATH:$SGX_SDK/bin:$SGX_SDK/bin/x64
ENV PKG_CONFIG_PATH=$PKG_CONFIG_PATH:$SGX_SDK/pkgconfig
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$SGX_SDK/sdk_libs
ENV TCF_ENCLAVE_CODE_SIGN_PEM="$TCF_HOME/enclave.pem"

RUN openssl genrsa -3 -out $TCF_HOME/enclave.pem 3072

WORKDIR /project/avalon/common/sgx_workload

RUN mkdir -p build \
  && cd build \
  && cmake .. \
  && make

# apps directory contains SGX workloads which need to be build
# and linked to SGX enclave
WORKDIR /project/avalon/examples/apps

RUN mkdir -p build \
  && cd build \
  && cmake .. \
  && make

WORKDIR /project/avalon/common/cpp

RUN mkdir -p build \
  && cd build \
  && cmake .. \
  && make

WORKDIR /project/avalon/tc/sgx/trusted_worker_manager/common

RUN mkdir -p build \
  && cd build \
  && cmake .. \
  && make

WORKDIR /project/avalon/tc/sgx/trusted_worker_manager/enclave

RUN mkdir -p build \
  && cd build \
  && cmake .. \
  && make

WORKDIR /project/avalon/tc/sgx/trusted_worker_manager/enclave_untrusted/enclave_bridge

RUN mkdir -p build \
  && cd build \
  && cmake .. \
  && make

WORKDIR /project/avalon/common/python

RUN make

WORKDIR /project/avalon/common/crypto_utils

RUN make

WORKDIR /project/avalon/sdk

RUN make

WORKDIR /project/avalon/enclave_manager

RUN echo "Building avalon enclave manager" \
  && make

# Build Final image and install dependent modules
FROM base_image as final_image

ENV TCF_HOME=/project/avalon

WORKDIR /project/avalon/

COPY --from=build_image /project/avalon/config/tcs_config.toml /project/avalon/config/
COPY --from=build_image /project/avalon/tc/sgx/trusted_worker_manager/enclave/build/lib/*.so /project/avalon/tc/sgx/trusted_worker_manager/enclave/build/lib/
COPY --from=build_image /project/avalon/tc/sgx/trusted_worker_manager/enclave_untrusted/enclave_bridge/build/lib/*.so /project/avalon/tc/sgx/trusted_worker_manager/enclave_untrusted/enclave_bridge/build/lib/
# Copy sgxsdk, sgxssl to final image.
COPY --from=build_image /opt/intel/sgxsdk/bin/ /opt/intel/sgxsdk/bin
COPY --from=build_image /opt/intel/sgxsdk/lib64/ /opt/intel/sgxsdk/lib64
COPY --from=build_image /opt/intel/sgxssl/lib64/ /opt/intel/sgxssl/lib64

# Copy Python build artifacts
COPY --from=build_image /project/avalon/common/python/dist/*.whl dist/
COPY --from=build_image /project/avalon/common/crypto_utils/dist/*.whl dist/
COPY --from=build_image /project/avalon/sdk/dist/*.whl dist/
COPY --from=build_image /project/avalon/enclave_manager/dist/*.whl dist/


# Installing wheel file requires python3-pip package.
# But python3-pip package will increase size of final docker image.
# So remove python3-pip package and dependencies after installing wheel file.
RUN apt-get update \
 && apt-get install -y -q python3-pip \
 && echo "Install Common Python, SDK and Enclave Manager packages\n" \
 && pip3 install dist/*.whl \
 && echo "Remove unused packages from image\n" \
 && apt-get autoremove --purge -y -q python3-pip \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
