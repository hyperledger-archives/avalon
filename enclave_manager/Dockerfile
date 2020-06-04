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
#   Builds the environment needed to build Avalon Intel SGX Enclave manager.
#
#  Configuration (build) parameters
#  - proxy configuration: https_proxy http_proxy ftp_proxy
#  - sgx_mode:
#

# -------------=== build avalon Enclave Manager image ===-------------
#Build base docker image
FROM ubuntu:bionic as base_image

# Ignore timezone prompt in apt
ENV DEBIAN_FRONTEND=noninteractive

# Add necessary packages
RUN apt-get update \
 && apt-get install -y -q \
    ca-certificates \
    python3-toml \
    python3-requests \
    python3-colorlog \
    python3-twisted \
 && apt-get clean

# Make Python3 default
RUN ln -sf /usr/bin/python3 /usr/bin/python



# -------------=== python build ===-------------

#Build python intermediate docker image
FROM ubuntu:bionic as python_image


# Add necessary packages
RUN apt-get update \
 && apt-get install -y -q \
    ca-certificates \
    pkg-config \
    python3-pip \
    python3-dev \
    make \
 && apt-get clean

# Install setuptools packages using pip because
# these are not available in apt repository.
RUN pip3 install setuptools


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
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

# Build ("Untrusted") OpenSSL
RUN OPENSSL_VER=1.1.1d \
 && wget https://www.openssl.org/source/old/1.1.1/openssl-$OPENSSL_VER.tar.gz \
 && tar -zxf openssl-$OPENSSL_VER.tar.gz \
 && cd openssl-$OPENSSL_VER/ \
 && ./config \
 && THREADS=8 \
 && make -j$THREADS \
 && make test \
 && make install -j$THREADS



# -------------=== common/python build ===-------------

#Build common/python intermediate docker image
FROM python_image as common_python_image

COPY VERSION /project/avalon/
COPY ./bin /project/avalon/bin

ENV TCF_HOME=/project/avalon

COPY ./common/python /project/avalon/common/python

WORKDIR /project/avalon/common/python

RUN echo "Building Avalon Common Python\n" \
 && make



# -------------=== Avalon SDK build ===-------------

#Build Avalon SDK intermediate docker image
FROM python_image as avalon_sdk_image

COPY VERSION /project/avalon/
COPY ./bin /project/avalon/bin
COPY ./sdk /project/avalon/sdk

ENV TCF_HOME=/project/avalon

WORKDIR /project/avalon/sdk

#install Avalon SDK  package.
RUN echo "Building Avalon SDK\n" \
 && make



#Build Avalon Enclave Manager docker image
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
    python3-twisted \
    python3-pip \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Install setuptools packages using pip because
RUN pip3 install setuptools

# Intel SGX common library and SDK are installed in /opt/intel directory.
# Installation of Intel SGX libsgx-common packages requires
# /etc/init directory. In the Docker image this directory doesn't exist.
# Hence creating /etc/init directory.
RUN mkdir -p /opt/intel \
 && mkdir -p /etc/init
WORKDIR /opt/intel

# Install Intel SGX common library
RUN wget https://download.01.org/intel-sgx/sgx-linux/2.7.1/distro/ubuntu18.04-server/libsgx-enclave-common_2.7.101.3-bionic1_amd64.deb \
 && dpkg -i libsgx-enclave-common_2.7.101.3-bionic1_amd64.deb

# Install Intel SGX SDK
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

# Build ("trusted") Intel SGX OpenSSL
# Note: This will compile in HW or SIM mode depending on the

# Note: This will compile in HW or SIM mode depending on the
# availability of /dev/isgx and /var/run/aesmd/aesm.socket

WORKDIR /tmp

# Using specific Intel SGX SSL tag "lin_2.5_1.1.1d" corresponding to
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

# Copy Python build artifacts
COPY --from=common_python_image /project/avalon/common/python/dist/*.whl dist/
COPY --from=avalon_sdk_image /project/avalon/sdk/dist/*.whl dist/

RUN echo "Install common/python and sdk packages\n" \
 && pip3 install dist/*.whl json-rpc pyzmq coverage


ARG SGX_MODE
ARG MAKECLEAN
ARG TCF_DEBUG_BUILD
ARG ENCLAVE_TYPE

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

# Directory apps contains Intel SGX workloads which need to be built
# and linked to the Intel SGX enclave
WORKDIR /project/avalon/examples/apps
RUN mkdir -p build \
  && cd build \
  && cmake .. \
  && make

# Build Key Management Enclave workload which will be
# linked to enclave shared library
WORKDIR /project/avalon/tc/sgx/trusted_worker_manager/enclave/kme_workload
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

WORKDIR /project/avalon/common/crypto_utils

RUN make && make install

WORKDIR /project/avalon/enclave_manager

RUN echo "Build and Install avalon enclave manager" \
  && make && make install

