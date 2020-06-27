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

FROM ubuntu:bionic

RUN apt update \
 && apt install -y -q python3 python3-pip \
 && apt-get clean

WORKDIR /project

COPY --from=avalon-listener-dev:latest /project/avalon/listener/dist/*.whl dist/
COPY --from=avalon-enclave-manager-dev:latest /project/avalon/enclave_manager/dist/*.whl dist/
COPY --from=avalon-lmdb-dev:latest /project/avalon/shared_kv_storage/dist/*.whl dist/

RUN pip3 install dist/*.whl
