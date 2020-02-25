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

FROM ubuntu:bionic as base_image

# Ignore timezone prompt in apt
ENV DEBIAN_FRONTEND=noninteractive

# Add necessary packages
RUN apt-get update \
 && apt-get install -y -q \
    build-essential \
    ca-certificates \
    pkg-config \
    protobuf-compiler \
    libprotobuf-dev \
    python3-dev \
    python3-pip \
    python3-toml \
    python3-requests \
    python3-colorlog \
    python3-twisted \
    software-properties-common \
    dh-autoreconf \
    ocaml \
    xxd \
    ocamlbuild \
 && apt-get -y -q upgrade \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Make Python3 default
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Build Avalon blockchain connector intermediate docker image
FROM base_image as build_image
# Add necessary packages to build
RUN apt-get update \
 && apt-get install -y -q \
    cmake \
    make \
    git \
    wget \
    tar \
    unzip \
    swig \
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
 && make install -j$THREADS \
 && ldconfig \
 && ln -s /etc/ssl/certs/* /usr/local/ssl/certs/ \
 && cd .. \
 && rm -rf openssl-$OPENSSL_VER

ENV TCF_HOME=/project/avalon

COPY VERSION /project/avalon/
COPY ./bin /project/avalon/bin
COPY ./common/cpp /project/avalon/common/cpp
COPY ./common/python /project/avalon/common/python
COPY ./sdk /project/avalon/sdk
COPY ./blockchain_connector /project/avalon/blockchain_connector

WORKDIR /project/avalon/common/cpp

RUN mkdir -p build \
  && cd build \
  && cmake .. -DUNTRUSTED_ONLY=1 \
  && make

#install avalon common module
WORKDIR /project/avalon/common/python

RUN echo "Building Avalon Common Python\n" \
 && make \ 
 && echo "Installing Avalon Common Python" \
 && make install

#install avalon-client sdk python package.
RUN echo "Building Avalon SDK\n" \
   && cd /project/avalon/sdk \
   && python setup.py bdist_wheel \
   && pip3 install dist/*.whl

# Install fabric python sdk
RUN pip3 install virtualenv \
   && pip3 install git+https://github.com/hyperledger/fabric-sdk-py.git

# Installing web3 for ethereum
RUN pip3 install --upgrade setuptools json-rpc web3 py-solc-x nose2 eth-abi

# Install specific version of solc to support versions <0.6.0
RUN python3 -m solcx.install v0.5.15

RUN pip3 install nest_asyncio

# install blockchain connector module
RUN cd /project/avalon/blockchain_connector \
   && python setup.py bdist_wheel \
   && pip3 install dist/*.whl

# Build final image and install modules
FROM base_image as final_image

ENV TCF_HOME=/project/avalon

WORKDIR /project/avalon/blockchain_connector

COPY --from=build_image /usr/local/ /usr/local
COPY --from=build_image /root/.solcx /root/.solcx

# Environment setup

RUN echo "TCF_HOME=/project/avalon/" >> /etc/environment \
 && if [ ! -z "$http_proxy"  ]; then \
        echo 'Acquire::http::Proxy "'$http_proxy'";' \
             >> /etc/apt/apt.conf.d/00proxy; \
        echo "http_proxy=$http_proxy" >> /etc/wgetrc; \
        echo "http_proxy=$http_proxy" >> /etc/environment; \
        echo "HTTP_PROXY=$(echo $http_proxy | sed 's,[a-zA-Z]*://,,')" \
                  >> /etc/environment; \
    fi \
 && if [ ! -z "$ftp_proxy"  ];  then \
        echo 'Acquire::ftp::Proxy "'$ftp_proxy'";' \
             >> /etc/apt/apt.conf.d/00proxy; \
        echo "ftp_proxy=$ftp_proxy" >> /etc/wgetrc; \
        echo "ftp_proxy=$ftp_proxy" >> /etc/environment; \
    fi \
 && if [ ! -z "$https_proxy" ]; then \
        echo 'Acquire::https::Proxy "'$https_proxy'";' \
              >> /etc/apt/apt.conf.d/00proxy; \
        echo "https_proxy=$https_proxy" >> /etc/wgetrc; \
        echo "https_proxy=$https_proxy" >> /etc/environment; \
        echo "HTTPS_PROXY=$(echo $https_proxy | sed 's,[a-zA-Z]*://,,')" \
             >> /etc/environment; \
    fi

ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy
