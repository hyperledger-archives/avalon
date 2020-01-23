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
    pkg-config \
    python3-toml \
    python3-requests \
    python3-colorlog \
    python3-twisted \
 && apt-get -y -q upgrade \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Make Python3 default
RUN ln -sf /usr/bin/python3 /usr/bin/python

#Build Avalon Listener intermediate docker image
FROM base_image as build_image

RUN apt-get update \
 && apt-get install -y -q \
    cmake \
    make \
    libprotobuf-dev \
    python3-dev \
    python3-pip \
    swig \
    software-properties-common \
    wget \
    tar


# Install setuptools packages using pip because
# these are not available in apt repository.
RUN pip3 install --upgrade setuptools json-rpc

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
COPY ./config/tcs_config.toml /project/avalon/config/
COPY ./common/cpp /project/avalon/common/cpp
COPY ./common/python /project/avalon/common/python
COPY ./sdk /project/avalon/sdk
COPY ./listener /project/avalon/listener

WORKDIR /project/avalon/common/cpp

RUN mkdir -p build \
  && cd build \
  && cmake .. -DUNTRUSTED_ONLY=1 \
  && make

WORKDIR /project/avalon/common/python

RUN echo "Building Avalon Common Python\n" \
 && make \ 
 && echo "Installing Avalon Common Python" \
 && make install

WORKDIR /project/avalon/sdk
#install Avalon SDK  package.
RUN echo "Building Avalon SDK\n" \
 && make \
 && echo "Installing Avalon SDK\n" \
 && make install

# Build Avalon Listener module next.

WORKDIR /project/avalon/listener/

RUN echo "Building avalon listener\n" \
  && make \
  && echo "Installing Avalon Listener" \
  && make install

# Build final image and install modules
FROM base_image as final_image

ENV TCF_HOME=/project/avalon

WORKDIR /project/avalon/listener

COPY --from=build_image /usr/local/ /usr/local
COPY --from=build_image /project/avalon/listener/listener_config.toml /project/avalon/listener/listener_config.toml
COPY --from=build_image /project/avalon/config/tcs_config.toml /project/avalon/config/
