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

ARG IMAGE
FROM $IMAGE as base_image
ARG DISTRO
COPY ./scripts/install_packages /project/avalon/scripts/
RUN packages=""; \
    pip_packages=""; \
    if [ "$DISTRO" = "bionic" ] ; then \
      DEBIAN_FRONTEND=noninteractive \
      packages="$packages ca-certificates python3-requests python3-toml python3-colorlog python3-twisted"; \
    elif [ "$DISTRO" = "centos" ] ; then \
      packages="$packages python3" \
      pip_packages="$pip_packages toml colorlog twisted requests"; \
      /project/avalon/scripts/install_packages -c install -q "epel-release"; \
    fi; \
    /project/avalon/scripts/install_packages -c install -q "$packages" -p "$pip_packages"

# Make Python3 default
RUN ln -sf /usr/bin/python3 /usr/bin/python

# -------------=== python build ===-------------

#Build python intermediate docker image
FROM $IMAGE as python_image
ARG DISTRO

COPY ./scripts/install_packages /project/avalon/scripts/

# Add necessary packages
RUN packages="pkg-config python3-pip make" \
    pip_packages="setuptools"; \
    if [ "$DISTRO" = "bionic" ] ; then \
      packages="ca-certificates $packages python3-dev"; \
    elif [ "$DISTRO" = "centos" ] ; then \
      packages="$packages python3-devel" \
      pip_packages="$pip_packages wheel"; \
    fi; \
    /project/avalon/scripts/install_packages -c install -q "$packages" -p "$pip_packages"


# -------------=== Build openssl_image ===-------------

#Build openssl intermediate docker image
FROM $IMAGE as openssl_image
ARG DISTRO

COPY ./scripts/install_packages /project/avalon/scripts/

RUN packages="ca-certificates pkg-config make wget tar"; \
    if [ "$DISTRO" = "centos" ] ; then \
      packages="$packages perl gcc"; \
    fi; \
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
ARG DISTRO

COPY ./scripts/install_packages /project/avalon/scripts/

RUN packages="pkg-config cmake make git swig wget tar curl unzip" \
    && pip_packages="setuptools jsonschema"; \
    if [ "$DISTRO" = "bionic" ] ; then \
      packages="$packages ca-certificates build-essential software-properties-common python3-pip libprotobuf-dev dh-autoreconf ocaml xxd ocamlbuild"; \
    elif [ "$DISTRO" = "centos" ] ; then \
      packages="$packages perl gcc python3-devel libcurl-devel python3-wheel"; \
    fi; \
    /project/avalon/scripts/install_packages -c install -q "$packages" -p "$pip_packages"

RUN if [ "$DISTRO" = "centos" ] ; then \
      dnf -y --enablerepo=PowerTools install protobuf-devel yum-utils ocaml ocaml-ocamlbuild dh-autoreconf \
      && yum groupinstall 'Development Tools' -y \
      && alternatives --set python /usr/bin/python3; \
    fi


# Intel SGX common library and SDK are installed in /opt/intel directory.
# Installation of Intel SGX libsgx-common packages requires
# /etc/init directory. In the Docker image this directory doesn't exist.
# Hence creating /etc/init directory.
RUN mkdir -p /opt/intel \
 && mkdir -p /etc/init
WORKDIR /opt/intel

RUN if [ "$DISTRO" = "bionic" ] ; then \
      # Add Intel SGX repo to apt sources and install Intel SGX PSW packages
      echo 'deb [arch=amd64] https://download.01.org/intel-sgx/sgx_repo/ubuntu bionic main' | tee /etc/apt/sources.list.d/intel-sgx.list \
      && wget -qO - https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key | apt-key add \
      && apt-get update \
      && apt-get install -y -q \
         libsgx-enclave-common \
         libsgx-launch \
         libsgx-urts \
         libsgx-epid \
         libsgx-quote-ex \
      && apt-get clean \
      && rm -rf /var/lib/apt/lists/* \
     
      && SGX_SDK_FILE=sgx_linux_x64_sdk_2.10.100.2.bin \
      && wget https://download.01.org/intel-sgx/sgx-linux/2.10/distro/ubuntu18.04-server/$SGX_SDK_FILE \
      && echo "yes" | bash ./$SGX_SDK_FILE \
      && rm $SGX_SDK_FILE \
      && echo ". /opt/intel/sgxsdk/environment" >> /etc/environment; \

    elif [ "$DISTRO" = "centos" ] ; then \
      wget https://download.01.org/intel-sgx/sgx-linux/2.10/distro/centos8.1-server/sgx_rpm_local_repo.tgz \
      && tar -xvf sgx_rpm_local_repo.tgz \
      && yum-config-manager --add-repo file:///opt/intel/sgx_rpm_local_repo \
      && yum --nogpgcheck install -y \
         libsgx-launch \
         libsgx-epid \
         libsgx-quote-ex \
         libsgx-urts; \
      cd /opt/intel \
      && wget https://download.01.org/intel-sgx/sgx-linux/2.10/distro/centos8.1-server/sgx_linux_x64_sdk_2.10.100.2.bin \
      && chmod +x sgx_linux_x64_sdk_2.10.100.2.bin \
      && echo "yes" | bash ./sgx_linux_x64_sdk_2.10.100.2.bin \
      && echo ". /opt/intel/sgxsdk/environment" >> /etc/environment; \
    fi
     
     
# Copy openssl build artifacts from openssl_image
ENV OPENSSL_VER=1.1.1g

COPY --from=openssl_image /usr/local/ssl /usr/local/ssl
COPY --from=openssl_image /usr/local/bin /usr/local/bin
COPY --from=openssl_image /usr/local/include /usr/local/include
COPY --from=openssl_image /usr/local/lib /usr/local/lib
# In case of openssl, artifacts are installed at /usr/local/lib64
COPY --from=openssl_image /usr/local/lib64 /usr/local/lib64
COPY --from=openssl_image /tmp/openssl-$OPENSSL_VER.tar.gz /tmp/

# Build ("trusted") Intel SGX OpenSSL
# Note: This will compile in HW or SIM mode depending on the

# Note: This will compile in HW or SIM mode depending on the
# availability of /dev/isgx and /var/run/aesmd/aesm.socket

WORKDIR /tmp

# Using specific Intel SGX SSL tag "lin_2.10_1.1.1g" corresponding to
# openSSL version 1.1.1g
# Intel SGX SSL is compiled with mitigation tools to address vulnerabilities
# found in earlier versions of SGX as documented in SGX SDK install guide
# https://github.com/intel/linux-sgx
# Mitigations tool tar ball is downloaded, extracted and copied to /usr/local/bin

RUN platform=""; \
    if [ "$DISTRO" = "bionic" ] ; then \
      platform="ubuntu18.04"; \
    elif [ "$DISTRO" = "centos" ] ; then \
      platform="centos8.1"; \
    fi; \
    ldconfig \
    && ln -s /etc/ssl/certs/* /usr/local/ssl/certs/ \
    && MITIGATION_TOOLS=as.ld.objdump.gold.r2.tar.gz \
    && wget https://download.01.org/intel-sgx/sgx-linux/2.10/$MITIGATION_TOOLS \
    && tar -xvf $MITIGATION_TOOLS \
    && cp external/toolset/$platform/* /usr/local/bin/ \
    && rm $MITIGATION_TOOLS \
    && git clone -b lin_2.10_1.1.1g https://github.com/intel/intel-sgx-ssl.git  \
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
# Docker build won't progress if host _dev folder not removed
RUN rm -rf /project/avalon/tools/build/_dev

# Copy Python build artifacts
COPY --from=common_python_image /project/avalon/common/python/dist/*.whl dist/
COPY --from=avalon_sdk_image /project/avalon/sdk/dist/*.whl dist/

RUN echo "Install common/python and sdk packages\n" \
 && pip3 install dist/*.whl json-rpc pyzmq coverage pycryptodomex ecdsa


ARG SGX_MODE
ARG MAKECLEAN
ARG TCF_DEBUG_BUILD
ARG ENCLAVE_TYPE
ARG WORKLOADS

# Environment setup
ENV TCF_HOME=/project/avalon
ENV SGX_SSL=/opt/intel/sgxssl
ENV SGX_SDK=/opt/intel/sgxsdk
ENV PATH=$PATH:$SGX_SDK/bin:$SGX_SDK/bin/x64
ENV PKG_CONFIG_PATH=$PKG_CONFIG_PATH:$SGX_SDK/pkgconfig
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$SGX_SDK/sdk_libs
ENV TCF_ENCLAVE_CODE_SIGN_PEM="$TCF_HOME/enclave.pem"
# For centos, /usr/local/lib64/pkgconfig/ path be included in PKG_CONFIG_PATH
ENV PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/usr/local/lib64/pkgconfig/

RUN openssl genrsa -3 -out $TCF_HOME/enclave.pem 3072

WORKDIR /project/avalon/common/sgx_workload

RUN mkdir -p build \
  && cd build \
  && cmake .. \
  && make

# Directory apps contains Intel SGX workloads which need to be built
# and linked to the Intel SGX enclave
RUN if [ "$ENCLAVE_TYPE" != "kme" ] ; then \
        cd /project/avalon/examples/apps; \
        mkdir -p build; \
        cd build; \
        cmake ..; \
        make; \
    fi

# Build Key Management Enclave workload which will be
# linked to enclave shared library
RUN if [ "$ENCLAVE_TYPE" = "kme" ] ; then \
        cd /project/avalon/tc/sgx/trusted_worker_manager/enclave/kme/workload; \
	mkdir -p build; \
        cd build; \
        cmake ..; \
        make; \
    fi

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

WORKDIR /project/avalon/common/verify_report_utils

RUN make && make install

WORKDIR /project/avalon/enclave_manager

RUN echo "Build and Install avalon enclave manager" \
  && make && make install

