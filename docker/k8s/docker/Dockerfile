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

FROM sammyne/hyperledger-tcf-vm:alpha 

LABEL maintainer=lixiangmin01@baidu.com

RUN apt update -y && apt install -y vim
# the sed cmd below is to decrease the 1TB LMDB cache size for local development
RUN cd /project && rm -rf TrustedComputeFramework &&\
    git clone --branch master --depth 1 https://github.com/hyperledger-labs/trusted-compute-framework.git &&\
    mv trusted-compute-framework TrustedComputeFramework &&\
    sed -i 's/^StorageSize.*/StorageSize = "4 GB"/g' TrustedComputeFramework/config/tcs_config.toml &&\
    sed -i 's/^#remote_url.*/remote_url = "http:\/\/lmdb:9090"/g' TrustedComputeFramework/config/tcs_config.toml &&\
    cd /project/TrustedComputeFramework/tools/build &&\
    echo "CLEAN BUILD..." && make clean && echo "DONE CLEAN" && make && echo "BUILD SUCCESS"

WORKDIR /project/TrustedComputeFramework
