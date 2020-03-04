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
#   Builds the environment needed to build Avalon shell.
#
#  Configuration (build) parameters
#  - proxy configuration: https_proxy http_proxy ftp_proxy
#
# Build:
#   $ docker build docker -f docker/Dockerfile -t avalon-shell-dev
#   if behind a proxy, you might want to add also below options
#   --build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy --build-arg ftp_proxy=$ftp_proxy

# -------------=== build avalon shell image ===-------------
FROM ubuntu:bionic as base_image

# Ignore timezone prompt in apt
ENV DEBIAN_FRONTEND=noninteractive

# Add necessary packages
RUN apt-get update \
 && apt-get install -y -q \
    software-properties-common \
    python3-pip \
    python3-toml \
    python3-requests \
    python3-colorlog \
    python3-twisted \
    git \
 && apt-get -y -q upgrade \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Make Python3 default
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Installing solidity compiler
RUN add-apt-repository ppa:ethereum/ethereum \
   && apt-get update \
   && apt-get install solc

# Install py-solc-x and web3 packages using pip because
# these are not available in apt repository.
# Install nose2 for running tests.
RUN pip3 install --upgrade json-rpc web3 py-solc-x nose2

# Install specific version of solc to support versions <0.6.0
RUN python3 -m solcx.install v0.5.15

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

#Build Avalon Enclave Manager intermediate docker image
FROM base_image as build_image

RUN apt-get update \
 && apt-get install -y -q \
    build-essential \
    pkg-config \
    cmake \
    make \
    git \
    libprotobuf-dev \
    libssl-dev \
    python3-dev \
    swig \
    tar

RUN pip3 install --upgrade setuptools

# Copy openssl build artifacts from openssl_image
COPY --from=openssl_image /usr/local/ssl /usr/local/ssl
COPY --from=openssl_image /usr/local/bin /usr/local/bin
COPY --from=openssl_image /usr/local/include /usr/local/include
COPY --from=openssl_image /usr/local/lib /usr/local/lib

RUN ldconfig \
 && ln -s /etc/ssl/certs/* /usr/local/ssl/certs/

COPY VERSION /project/avalon/
COPY ./bin /project/avalon/bin
COPY ./tools/run_tests.sh /project/avalon/tools/
COPY ./config/tcs_config.toml /project/avalon/config/
COPY ./common/cpp /project/avalon/common/cpp
COPY ./common/python /project/avalon/common/python
COPY ./sdk /project/avalon/sdk
COPY ./tests /project/avalon/tests
COPY ./examples/apps /project/avalon/examples/apps

# Install fabric python sdk
RUN pip3 install virtualenv \
 && pip3 install git+https://github.com/hyperledger/fabric-sdk-py.git

WORKDIR /project/avalon/common/cpp

RUN echo "Building Avalon Common CPP\n" \
  && mkdir -p build \
  && cd build \
  && cmake .. -DUNTRUSTED_ONLY=1 \
  && make

WORKDIR /project/avalon/common/python

RUN echo "Building Avalon Common Python\n" \
  && make

WORKDIR /project/avalon/sdk

RUN echo "Building Avalon SDK\n" \
  && make

# Build Final image and install dependent modules
FROM base_image as final_image

ARG DISPLAY
ARG XAUTHORITY

#Environment setup
ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy
ENV TCF_HOME=/project/avalon
# Set display, replace value with [IP address of host]:0
ENV DISPLAY=:0

WORKDIR /project/avalon/

COPY --from=build_image /project/avalon/config/tcs_config.toml /project/avalon/config/
COPY --from=build_image /project/avalon/examples/apps/ /project/avalon/examples/apps
COPY --from=build_image /project/avalon/tests /project/avalon/tests
COPY --from=build_image /project/avalon/sdk/avalon_sdk/tcf_connector.toml /project/avalon/sdk/avalon_sdk/
COPY --from=build_image /project/avalon/sdk/avalon_sdk/ethereum/contracts /project/avalon/sdk/avalon_sdk/ethereum/contracts
COPY --from=build_image /project/avalon/sdk/avalon_sdk/fabric/methods.json /project/avalon/sdk/avalon_sdk/fabric/
COPY --from=build_image /project/avalon/tools/run_tests.sh /project/avalon/tools/

# Copy Python build artifacts
COPY --from=build_image /project/avalon/common/python/dist/*.whl dist/
COPY --from=build_image /project/avalon/sdk/dist/*.whl dist/

# Install fabric python sdk
RUN pip3 install virtualenv \
 && pip3 install git+https://github.com/hyperledger/fabric-sdk-py.git

# Installing wheel file requires python3-pip package.
# But python3-pip package will increase size of final docker image.
# So remove python3-pip package and dependencies after installing wheel file.
RUN apt-get update \
 && apt-get install -y -q python3-pip \
 && echo "Install Common Python and SDK packages\n" \
 && pip3 install dist/*.whl \
 && echo "Remove unused packages from image\n" \
 && apt-get autoremove --purge -y -q python3-pip \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
