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

# -------------=== listener build ===-------------

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
 && apt-get -y -q upgrade \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Make Python3 default
RUN ln -sf /usr/bin/python3 /usr/bin/python

# -------------=== openssl build ===-------------

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
    pkg-config \
    cmake \
    make \
    libprotobuf-dev \
    python3-dev \
    python3-pip \
    swig \
    software-properties-common


# Copy openssl build artifacts from openssl_image
COPY --from=openssl_image /usr/local/ssl /usr/local/ssl
COPY --from=openssl_image /usr/local/bin /usr/local/bin
COPY --from=openssl_image /usr/local/include /usr/local/include
COPY --from=openssl_image /usr/local/lib /usr/local/lib

RUN ldconfig \
 && ln -s /etc/ssl/certs/* /usr/local/ssl/certs/

# Install setuptools packages using pip because
# these are not available in apt repository.
RUN pip3 install --upgrade setuptools

ENV TCF_HOME=/project/avalon

COPY VERSION /project/avalon/
COPY ./bin /project/avalon/bin
COPY ./config/tcs_config.toml /project/avalon/config/
COPY ./common/cpp /project/avalon/common/cpp
COPY ./common/python /project/avalon/common/python
COPY ./common/crypto_utils /project/avalon/common/crypto_utils
COPY ./sdk /project/avalon/sdk
COPY ./listener /project/avalon/listener

WORKDIR /project/avalon/common/cpp

RUN mkdir -p build \
  && cd build \
  && cmake .. -DUNTRUSTED_ONLY=1 \
  && make

WORKDIR /project/avalon/common/python

RUN echo "Building Avalon Common Python\n" \
 && make 

WORKDIR /project/avalon/common/crypto_utils

RUN echo "Building Avalon Common Crypto Python\n" \
 && make

WORKDIR /project/avalon/sdk
#install Avalon SDK  package.
RUN echo "Building Avalon SDK\n" \
 && make 

# Build Avalon Listener module next.

WORKDIR /project/avalon/listener/

RUN echo "Building avalon listener\n" \
  && make

# Build final image and install modules
FROM base_image as final_image

ENV TCF_HOME=/project/avalon

WORKDIR /project/avalon/listener

COPY --from=build_image /project/avalon/listener/listener_config.toml /project/avalon/listener/listener_config.toml
COPY --from=build_image /project/avalon/config/tcs_config.toml /project/avalon/config/
# Copy Python build artifacts
COPY --from=build_image /project/avalon/common/python/dist/*.whl dist/
COPY --from=build_image /project/avalon/common/crypto_utils/dist/*.whl dist/
COPY --from=build_image /project/avalon/sdk/dist/*.whl dist/
COPY --from=build_image /project/avalon/listener/dist/*.whl dist/

# Installing wheel file requires python3-pip package.
# But python3-pip package will increase size of final docker image.
# So remove python3-pip package and dependencies after installing wheel file.
RUN apt-get update \
 && apt-get install -y -q python3-pip \
 && pip3 install --upgrade json-rpc \
 && echo "Install Common Python, Crypto, Listener and SDK packages\n" \
 && pip3 install dist/*.whl \
 && echo "Remove unused packages from image\n" \
 && apt-get autoremove --purge -y -q python3-pip \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
