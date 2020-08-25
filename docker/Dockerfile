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
ARG IMAGE
FROM $IMAGE as base_image
ARG DISTRO

COPY ./scripts/install_packages /project/avalon/scripts/

RUN packages=""; \
    pip_packages=""; \
    if [ "$DISTRO" = "bionic" ] ; then \
      DEBIAN_FRONTEND=noninteractive \
      packages="$packages software-properties-common python3-toml python3-colorlog python3-twisted python3-requests"; \
    elif [ "$DISTRO" = "centos" ] ; then \
      packages="$packages python3-pip" \
      pip_packages="$pip_packages toml colorlog twisted requests"; \
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
RUN packages="ca-certificates pkg-config python3-pip make" \
    pip_packages="setuptools"; \
    if [ "$DISTRO" = "bionic" ] ; then \
      packages="$packages python3-dev"; \
    elif [ "$DISTRO" = "centos" ] ; then \
      packages="$packages python3-devel" \
      pip_packages="$pip_packages wheel"; \
    fi; \
    /project/avalon/scripts/install_packages -c install -q "$packages" -p "$pip_packages"

# -------------=== Build openssl_image ===-------------

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

# -------------=== common/cpp build ===-------------

#Build common/cpp intermediate docker image
FROM $IMAGE as common_cpp_image
ARG DISTRO
COPY ./scripts/install_packages /project/avalon/scripts/

RUN packages="pkg-config make cmake "; \
    if [ "$DISTRO" = "centos" ] ; then \
      packages="$packages gcc gcc-c++"; \
    fi; \
    /project/avalon/scripts/install_packages -c install -q "$packages"

# Copy openssl build artifacts from openssl_image
COPY --from=openssl_image /usr/local/ssl /usr/local/ssl
COPY --from=openssl_image /usr/local/bin /usr/local/bin
COPY --from=openssl_image /usr/local/include /usr/local/include
COPY --from=openssl_image /usr/local/lib /usr/local/lib
# In case of openssl, artifacts are installed at /usr/local/lib64
COPY --from=openssl_image /usr/local/lib64 /usr/local/lib64

RUN ldconfig \
 && ln -s /etc/ssl/certs/* /usr/local/ssl/certs/

ENV TCF_HOME=/project/avalon

# For centos, /usr/local/lib64/pkgconfig/ path be included in PKG_CONFIG_PATH
ENV PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/usr/local/lib64/pkgconfig/

COPY ./common/cpp /project/avalon/common/cpp

WORKDIR /project/avalon/common/cpp

RUN mkdir -p build \
  && cd build \
  && cmake .. -DUNTRUSTED_ONLY=1 \
  && make


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


# -------------=== common/crypto_utils build ===-------------

#Build common/crypto_utils intermediate docker image
FROM python_image as common_crypto_utils_image
ARG DISTRO
COPY ./scripts/install_packages /project/avalon/scripts/

RUN packages="swig"; \
    if [ "$DISTRO" = "centos" ] ; then \
      packages="$packages make gcc gcc-c++"; \
    fi; \
    /project/avalon/scripts/install_packages -c install -q "$packages"

# Copy openssl build artifacts from openssl_image
COPY --from=openssl_image /usr/local/ssl /usr/local/ssl
COPY --from=openssl_image /usr/local/bin /usr/local/bin
COPY --from=openssl_image /usr/local/include /usr/local/include
COPY --from=openssl_image /usr/local/lib /usr/local/lib
# In case of openssl, artifacts are installed at /usr/local/lib64
COPY --from=openssl_image /usr/local/lib64 /usr/local/lib64

RUN ldconfig \
 && ln -s /etc/ssl/certs/* /usr/local/ssl/certs/

COPY --from=common_cpp_image /project/avalon/common/cpp/build /project/avalon/common/cpp/build
COPY VERSION /project/avalon/
COPY ./bin /project/avalon/bin
COPY ./common/cpp /project/avalon/common/cpp

ENV TCF_HOME=/project/avalon

# For centos, /usr/local/lib64/pkgconfig/ path be included in PKG_CONFIG_PATH
ENV PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/usr/local/lib64/pkgconfig/

COPY ./common/crypto_utils /project/avalon/common/crypto_utils

WORKDIR /project/avalon/common/crypto_utils

RUN echo "Building Avalon Common Crypto Python\n" \
 && make

COPY ./common/verify_report_utils /project/avalon/common/verify_report_utils

WORKDIR /project/avalon/common/verify_report_utils

RUN echo "Building Avalon Verify Report Utils\n" \
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



# Build Final image and install dependent modules
FROM base_image as final_image
ARG DISTRO
COPY ./scripts/install_packages /project/avalon/scripts/

RUN if [ "$DISTRO" = "centos" ] ; then \
      dnf remove -y python3-pip; \
      packages="openssl-devel wget make gcc"; \
      /project/avalon/scripts/install_packages -c install -q "$packages"; \
      cd /tmp \
      && wget https://www.python.org/ftp/python/3.6.9/Python-3.6.9.tgz \
      && tar -xvzf Python-3.6.9.tgz \
      && cd Python-3.6.9 \
      && ./configure \
      && make \
      && make install; \
    fi

RUN packages="git"; \
    pip_packages="json-rpc web3 py-solc-x nose2 virtualenv fastapi==0.27.* grpcio-tools==1.21.* uvicorn==0.7.* git+https://github.com/hyperledger/fabric-sdk-py.git nest_asyncio"; \
    if [ "$DISTRO" = "bionic" ] ; then \
      packages="python3-pip $packages"; \
    elif [ "$DISTRO" = "centos" ] ; then \
      packages="$packages gcc-c++ which"; \
    fi; \
    /project/avalon/scripts/install_packages -c install -q "$packages" -p "$pip_packages"; \
    if [ "$DISTRO" = "bionic" ] ; then \
      /project/avalon/scripts/install_packages -c uninstall -q "python3-pip"; \
    fi
      
RUN python3 -m solcx.install v0.5.15

ARG DISPLAY
ARG XAUTHORITY

#Environment setup
ENV TCF_HOME=/project/avalon
# Set display, replace value with [IP address of host]:0
ENV DISPLAY=:0

WORKDIR /project/avalon/

COPY ./tools/run_tests.sh /project/avalon/tools/
COPY ./tools/run_proxy_model_tests.sh /project/avalon/tools/
COPY ./docker/k8s/propose_requests.sh /project/avalon/docker/k8s/
COPY ./config/tcs_config.toml /project/avalon/config/
COPY ./tests /project/avalon/tests
COPY ./sdk/avalon_sdk/tcf_connector.toml /project/avalon/sdk/avalon_sdk/
COPY ./examples/apps/ /project/avalon/examples/apps
COPY ./sdk/avalon_sdk/connector/blockchains/ethereum/contracts /project/avalon/sdk/avalon_sdk/connector/blockchains/ethereum/contracts

# Copy Python build artifacts
COPY --from=common_python_image /project/avalon/common/python/dist/*.whl dist/
COPY --from=common_crypto_utils_image /project/avalon/common/crypto_utils/dist/*.whl dist/
COPY --from=common_crypto_utils_image /project/avalon/common/verify_report_utils/dist/*.whl dist/
COPY --from=avalon_sdk_image /project/avalon/sdk/dist/*.whl dist/

# Installing wheel file requires python3-pip package.
# But python3-pip package will increase size of final docker image.
# So remove python3-pip package and dependencies after installing wheel file.
RUN packages=""; \
    pip_packages="pycryptodomex ecdsa"; \
    if [ "$DISTRO" = "bionic" ] ; then \
      packages="$packages python3-pip"; \
   fi; \
    /project/avalon/scripts/install_packages -c install -q "$packages" -p "$pip_packages" \
    && echo "Install Common Python and SDK packages\n" \
    && pip3 install dist/*.whl \
    && if [ "$DISTRO" = "bionic" ] ; then \
         echo "Remove unused packages from image\n" \
         /project/avalon/scripts/install_packages -c uninstall -q "$packages"; \
       fi
 
