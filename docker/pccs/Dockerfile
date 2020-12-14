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
#   Builds the environment needed to DCAP PCCS server.
#
#  Configuration (build) parameters
#  - proxy configuration: https_proxy http_proxy ftp_proxy
#  - sgx_mode:
#

#Build base docker image
FROM ubuntu:bionic as base_image

# Ignore timezone prompt in apt
ENV DEBIAN_FRONTEND=noninteractive

# Add necessary packages
RUN apt-get update \
  && apt-get install -y -q curl \
     ca-certificates \
     gnupg \
     gnupg2 \
     gnupg1 \
     make \
     gcc \
     g++ \
     systemd \
     wget \
     tar

ARG DISTRO
ARG API_KEY

COPY ./scripts/install_packages /project/avalon/scripts/

RUN echo "distro = $DISTRO"
RUN packages="ca-certificates pkg-config make wget tar"; \
#    if [ "$DISTRO" = "centos" ] ; then \
#      packages="$packages perl gcc"; \
#    fi; \
  /project/avalon/scripts/install_packages -c install -q "$packages"

WORKDIR /tmp

# Build ("Untrusted") OpenSSL
RUN OPENSSL_VER=1.1.1g \
 && wget https://www.openssl.org/source/openssl-$OPENSSL_VER.tar.gz \
 && tar -zxf openssl-$OPENSSL_VER.tar.gz \
 && cd openssl-$OPENSSL_VER/ \
 && ./config \
 && THREADS=8 \
 && make -j$THREADS \
 && make test \
 && make install -j$THREADS

# Created an empty /usr/local/lib64 dir for bionic, because in case of centos
# we need to COPY /usr/local/lib64 for openssl artifacts which will fail for bionic
# as bionic doesn't have this directory.
RUN if [ "$DISTRO" = "bionic" ] ; then \
      mkdir /usr/local/lib64; \
    fi

RUN mkdir -p /opt/intel \
 && mkdir -p /etc/init

# Insall Nodejs for pm2
RUN curl -s -S -o /tmp/setup-node.sh https://deb.nodesource.com/setup_14.x \
  && chmod 755 /tmp/setup-node.sh \
  && /tmp/setup-node.sh \
  && apt-get install nodejs -y -q \
  && rm /tmp/setup-node.sh \
  && apt-get -y -q upgrade

# Install pccs
RUN curl  https://download.01.org/intel-sgx/sgx-dcap/1.9/linux/distro/ubuntu18.04-server/debian_pkgs/web/sgx-dcap-pccs/sgx-dcap-pccs_1.9.100.3-bionic1_amd64.deb -o /tmp/sgx-dcap-pccs_1.9.100.3-bionic1_amd64.deb \
 && dpkg -i /tmp/sgx-dcap-pccs_1.9.100.3-bionic1_amd64.deb

WORKDIR /opt/intel/sgx-dcap-pccs

# Configure QPL to use self-signed cert for local PCCS
COPY docker/pccs/sgx_default_qcnl.conf /etc/sgx_default_qcnl.conf

RUN echo "qcnl file copied content >>>>>>>>>>." \
 && sed -i 's/avalon-pccs/localhost/g' /etc/sgx_default_qcnl.conf \
 && cat /etc/sgx_default_qcnl.conf

RUN (printf "\n\nY\n\nN\n$API_KEY\n\nintel123\nintel123\navalon123\navalon123\nY\nIN\nKA\nBNG\nIntel\nESI\nPCCS Server\n.\n\n\n" ) | ./install.sh
