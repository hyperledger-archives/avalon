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

FROM node:13.10.1-slim

RUN npm install -g --unsafe-perm truffle@5.1.16

RUN mkdir -p my_project

WORKDIR my_project

# Initialize a truffle project in my_project/
RUN truffle init

# Copy contracts to the newly created truffle project
COPY ./sdk/avalon_sdk/connector/blockchains/ethereum/contracts/*sol contracts/

# Copy the config file which has Avalon specific networks/configs defined
COPY ./sdk/avalon_sdk/connector/blockchains/ethereum/truffle_artifacts/truffle-config.js ./

# Copy the migration script
COPY ./sdk/avalon_sdk/connector/blockchains/ethereum/truffle_artifacts/2_deploy_contracts.js migrations/
