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
  && apt-get install -y -q curl \
     ca-certificates \
     gnupg \
     gnupg2 \
     gnupg1 \
     make \
     gcc \
     g++ \
     systemd

# Insall Nodejs for pm2
RUN curl -s -S -o /tmp/setup-node.sh https://deb.nodesource.com/setup_14.x \
  && chmod 755 /tmp/setup-node.sh \
  && /tmp/setup-node.sh \
  && apt-get install nodejs -y -q \
  && rm /tmp/setup-node.sh \
  && apt-get -y -q upgrade

# Install pccs
RUN curl https://download.01.org/intel-sgx/sgx-dcap/1.8/linux/distro/ubuntu18.04-server/debian_pkgs/web/sgx-dcap-pccs/sgx-dcap-pccs_1.8.100.2-bionic1_amd64.deb -o /tmp/sgx-dcap-pccs_1.8.100.2-bionic1_amd64.deb \
 && dpkg -i /tmp/sgx-dcap-pccs_1.8.100.2-bionic1_amd64.deb

# Copy the config files from docker/pccs/config/
COPY docker/pccs/config/ /opt/intel/sgx-dcap-pccs/
WORKDIR /opt/intel/sgx-dcap-pccs

RUN (printf "\n\nY\n\nN\n\n\nintel123\nintel123\navalon123\navalon123\nY\n\n\n\n\n\n\n\n\n\n" && cat) | ./install.sh

RUN pm2 update \
 && pm2 save \
 && pm2 startup systemd 

CMD pm2 start pccs_server.config.js \
 && pm2 status \
 && tail -f /dev/null
