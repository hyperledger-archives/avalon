# Copyright 2018 Intel Corporation
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
PROJECT(libtcf-enclave  CXX)

INCLUDE(CMakeVariables.txt)

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# ADDITIONAL LIBRARIES
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

SET(TCF_TOP_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../../../")
SET(TCF_CORE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../")

SET(SINGLETON_PATH ${CMAKE_CURRENT_SOURCE_DIR}/singleton)
SET(KME_PATH ${CMAKE_CURRENT_SOURCE_DIR}/kme)
SET(WPE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/wpe)

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

FILE(GLOB PROJECT_HEADERS *.h)
FILE(GLOB PROJECT_SOURCES *.cpp *.c singleton/*.cpp singleton/*.c
     kme/*.cpp kme/*.c wpe/*.cpp wpe/*.c)
FILE(GLOB PROJECT_EDL enclave.edl)
FILE(GLOB PROJECT_CONFIG *.xml)
SOURCE_GROUP("Source" FILES ${PROJECT_HEADERS} ${PROJECT_SOURCES} ${PROJECT_EDL})

SET (LIBTCF_ENCLAVE_EDL ${PROJECT_EDL})
SET (LIBTCF_ENCLAVE_INCLUDE ${CMAKE_CURRENT_SOURCE_DIR})

INCLUDE_DIRECTORIES(${SGX_INCLUDE})
INCLUDE_DIRECTORIES(/opt/intel/sgxsdk/include /opt/intel/sgxssl/include)
INCLUDE_DIRECTORIES(${TCF_TOP_DIR}/common/cpp)
INCLUDE_DIRECTORIES(${TCF_CORE_DIR}/trusted_worker_manager/common)
INCLUDE_DIRECTORIES(${TCF_TOP_DIR}/common/cpp/crypto)
INCLUDE_DIRECTORIES(${TCF_TOP_DIR}/common/cpp/verify_ias_report)
INCLUDE_DIRECTORIES(${TCF_TOP_DIR}/common/cpp/packages/base64)
INCLUDE_DIRECTORIES(${TCF_TOP_DIR}/common/cpp/packages/parson)
INCLUDE_DIRECTORIES(${TCF_TOP_DIR}/common/sgx_workload/workload)
LINK_DIRECTORIES()

SGX_EDGE_TRUSTED(${PROJECT_EDL} PROJECT_EDGE_SOURCES)

SOURCE_GROUP("Generated" FILES ${PROJECT_EDGE_SOURCES})


# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Compile targets
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# CMake likes to prepend "lib" to project name when creating library...since we
# already have lib in the project name, liblibtcf-enclave is stupid.  Stop
# CMake from doing it.
SET(CMAKE_SHARED_LIBRARY_PREFIX "")
PROJECT(libtcf-enclave C CXX)

ADD_LIBRARY(${PROJECT_NAME} SHARED  ${PROJECT_HEADERS} ${PROJECT_SOURCES} ${PROJECT_EDGE_SOURCES} ${PROJECT_EDL})
SGX_SIGN_ENCLAVE(${PROJECT_NAME} ${TCF_ENCLAVE_CODE_SIGN_PEM} ${PROJECT_CONFIG})

TARGET_LINK_LIBRARIES(${PROJECT_NAME} -Wl,--whole-archive -lsgx_tsgxssl -Wl,--no-whole-archive)
TARGET_LINK_LIBRARIES(${PROJECT_NAME} -Wl,--whole-archive -l${TRTS_LIBRARY_NAME} -Wl,--no-whole-archive)

TARGET_LINK_LIBRARIES(${PROJECT_NAME} -Wl,--whole-archive -lcommon_sgx_workload -lcommon_sgx_iohandler -Wl,--no-whole-archive)

# Add KME workload
TARGET_LINK_LIBRARIES(${PROJECT_NAME} -Wl,--whole-archive -lkme_workload -Wl,--no-whole-archive)
# Add echo workload
TARGET_LINK_LIBRARIES(${PROJECT_NAME} -Wl,--whole-archive -lecho_wo -Wl,--no-whole-archive)
# Add heart disease eval workload
TARGET_LINK_LIBRARIES(${PROJECT_NAME} -Wl,--whole-archive -lheart_disease_eval -Wl,--no-whole-archive)
# Add example inside out workload
TARGET_LINK_LIBRARIES(${PROJECT_NAME} -Wl,--whole-archive -linside_out_eval -Wl,--no-whole-archive)
# Add simple wallet workload
TARGET_LINK_LIBRARIES(${PROJECT_NAME} -Wl,--whole-archive -lsimple_wallet -Wl,--no-whole-archive)

TARGET_LINK_LIBRARIES(${PROJECT_NAME} -Wl,--start-group  -ltavalon-common -ltavalon-base64 -ltavalon-parson -ltavalon-crypto -ltavalon-verify-ias-report -ltavalon-sgx-common -lsgx_tsgxssl_crypto -lsgx_tstdc -lsgx_tcxx -lsgx_tcrypto  -l${SERVICE_LIBRARY_NAME} -Wl,--end-group)

TARGET_INCLUDE_DIRECTORIES( ${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR} ${SGX_ENCLAVE_INCLUDE} ${SGX_INCLUDE})
TARGET_INCLUDE_DIRECTORIES(${PROJECT_NAME} PRIVATE ${TCF_TOP_DIR}/examples/apps)

ADD_CUSTOM_COMMAND(
    TARGET ${PROJECT_NAME}
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory "${DEPS_DIR}/bin"
    COMMAND ${CMAKE_COMMAND} -E copy "${SIGNED_ENCLAVE}" "${DEPS_DIR}/bin"
)

# To add a new workload, uncomment the following lines and change
# $WORKLOAD_STATIC_NAME$ to the appropriate name (such as hello_world):
#SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-L,${TCF_TOP_DIR}/examples/apps/build/$WORKLOAD_STATIC_NAME$/workload")
#TARGET_LINK_LIBRARIES(${PROJECT_NAME} -Wl,--whole-archive -l$WORKLOAD_STATIC_NAME$ -Wl,--no-whole-archive)
