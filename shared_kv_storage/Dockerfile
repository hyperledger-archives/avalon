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

ARG IMAGE
FROM $IMAGE as base_image
ARG DISTRO
COPY ./scripts/install_packages /project/avalon/scripts/

RUN packages="curl wget"; \
    pip_packages=""; \
    if [ "$DISTRO" = "bionic" ] ; then \
      # Ignore timezone prompt in apt
      DEBIAN_FRONTEND=noninteractive \
      packages="ca-certificates $packages python3-requests python3-colorlog python3-twisted python3-toml liblmdb-dev"; \
    elif [ "$DISTRO" = "centos" ] ; then \
      packages="$packages python3 lmdb-devel" \
      pip_packages="$pip_packages toml colorlog twisted requests"; \
      /project/avalon/scripts/install_packages -c install -q "epel-release"; \
    fi; \
    /project/avalon/scripts/install_packages -c install -q "$packages" -p "$pip_packages"

# Make Python3 default
RUN ln -sf /usr/bin/python3 /usr/bin/python

#------------------------------------------------------------------------------
# Build Shared KV intermediate docker image.
FROM base_image as build_image
ARG DISTRO
COPY ./scripts/install_packages /project/avalon/scripts/

RUN packages="pkg-config cmake make python3-pip swig"; \
    pip_packages="setuptools"; \
    if [ "$DISTRO" = "bionic" ] ; then \
      packages="$packages build-essential software-properties-common python3-dev"; \
    elif [ "$DISTRO" = "centos" ] ; then \
      packages="$packages python3-devel gcc gcc-c++" \
      pip_packages="$pip_packages wheel"; \
    fi; \
    /project/avalon/scripts/install_packages -c install -q "$packages" -p "$pip_packages"

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
ARG DISTRO
COPY ./scripts/install_packages /project/avalon/scripts/

ENV TCF_HOME=/project/avalon

WORKDIR /project/avalon/shared_kv_storage/

# Copy required build artifacts from build_image.
COPY --from=build_image /project/avalon/shared_kv_storage/dist/*.whl dist/
COPY --from=build_image /project/avalon/shared_kv_storage/lmdb_config.toml \
     lmdb_config.toml

# Installing wheel file requires python3-pip package.
# But python3-pip package will increase size of final docker image.
# So remove python3-pip package and dependencies after installing wheel file.
RUN packages=""; \
    pip_packages="coverage"; \
    if [ "$DISTRO" = "bionic" ] ; then \
      packages="$packages python3-pip"; \
    fi; \
    /project/avalon/scripts/install_packages -c install -q "$packages" -p "$pip_packages" \
    && echo "Install Shared KV package\n" \
    && pip3 install dist/*.whl \
    && if [ "$DISTRO" = "bionic" ] ; then \
         echo "Remove unused packages from image\n" \
         /project/avalon/scripts/install_packages -c uninstall -q "$packages"; \
       fi
