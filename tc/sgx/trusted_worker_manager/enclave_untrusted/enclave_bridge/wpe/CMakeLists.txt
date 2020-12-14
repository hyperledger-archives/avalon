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

CMAKE_MINIMUM_REQUIRED(VERSION 3.2 FATAL_ERROR)

PROJECT(avalon-wpe-enclave-bridge C CXX)

LIST(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

SET(DEPS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/deps")
SET(TCF_TOP_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../../../../../")
SET(TCF_CORE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../../../")

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

if("${ATTESTATION_TYPE}" STREQUAL "epid")
    FILE(GLOB PROJECT_HEADERS *.h ../*.h ../epid/*.h)
    FILE(GLOB PROJECT_SOURCES *.cpp ../*.cpp ../epid/*.cpp)
elseif("${ATTESTATION_TYPE}" STREQUAL "dcap")
    FILE(GLOB PROJECT_HEADERS *.h ../*.h ../dcap/*.h)
    FILE(GLOB PROJECT_SOURCES *.cpp ../*.cpp ../dcap/*.cpp)
endif()
FILE(GLOB PROJECT_EDL ${TCF_CORE_DIR}/trusted_worker_manager/enclave/wpe/wpe_enclave.edl)

SOURCE_GROUP("Source" FILES ${PROJECT_HEADERS} ${PROJECT_SOURCES})
SET(EDL_PATH ${TCF_CORE_DIR}/trusted_worker_manager/enclave)

SGX_EDGE_UNTRUSTED(${PROJECT_EDL} ${EDL_PATH} PROJECT_EDGE_SOURCES)

SOURCE_GROUP("Generated" FILES ${PROJECT_EDGE_SOURCES})


# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Compile targets
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

ADD_LIBRARY(${PROJECT_NAME} SHARED ${PROJECT_HEADERS} ${PROJECT_SOURCES} ${PROJECT_EDGE_SOURCES})
LINK_ENCLAVE_BRIDGE_COMMON_LIBRARIES()

#Include common directories
INCLUDE_ENCLAVE_BRIDGE_COMMON_DIRECTORIES()
