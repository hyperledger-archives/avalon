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

CMAKE_MINIMUM_REQUIRED(VERSION 3.2 FATAL_ERROR)

FILE(GLOB PROJECT_HEADERS "*.h")
FILE(GLOB PROJECT_SOURCES "*.cpp")

SET(GENERIC_CXX_FLAGS ${DEBUG_FLAGS} "-Wall" "-fPIC" "-Wno-write-strings" "-std=c++11")

SET(SGX_SSL "$ENV{SGX_SSL}")
if("${SGX_SSL} " STREQUAL " ")
    SET(SGX_SSL "/opt/intel/sgxssl")
    message(STATUS "Setting default SGX_SSL=${SGX_SSL}")
endif()

SET(DATA_OWNER_STATIC_NAME data_owner)
PROJECT(${DATA_OWNER_STATIC_NAME} C CXX)

ADD_LIBRARY(${DATA_OWNER_STATIC_NAME} STATIC ${PROJECT_HEADERS} ${PROJECT_SOURCES})

TARGET_INCLUDE_DIRECTORIES(${DATA_OWNER_STATIC_NAME} PRIVATE ${TCF_TOP_DIR}/tc/sgx/trusted_worker_manager/enclave)
TARGET_INCLUDE_DIRECTORIES(${DATA_OWNER_STATIC_NAME} PRIVATE ${TCF_TOP_DIR}/tc/sgx/trusted_worker_manager/common)
TARGET_INCLUDE_DIRECTORIES(${DATA_OWNER_STATIC_NAME} PRIVATE ${TCF_TOP_DIR}/common/cpp/crypto)
TARGET_INCLUDE_DIRECTORIES(${DATA_OWNER_STATIC_NAME} PRIVATE ${TCF_TOP_DIR}/common/cpp/verify_ias_report)
TARGET_INCLUDE_DIRECTORIES(${DATA_OWNER_STATIC_NAME} PRIVATE ${TCF_TOP_DIR}/common/cpp/packages/parson)
TARGET_INCLUDE_DIRECTORIES(${DATA_OWNER_STATIC_NAME} PRIVATE ${GENERIC_PRIVATE_INCLUDE_DIRS})
TARGET_INCLUDE_DIRECTORIES(${DATA_OWNER_STATIC_NAME} PUBLIC ${GENERIC_PUBLIC_INCLUDE_DIRS})
TARGET_INCLUDE_DIRECTORIES(${DATA_OWNER_STATIC_NAME} PUBLIC "${SGX_SDK}/include/tlibc")
TARGET_INCLUDE_DIRECTORIES(${DATA_OWNER_STATIC_NAME} PUBLIC "${SGX_SDK}/include/libcxx")
TARGET_INCLUDE_DIRECTORIES(${DATA_OWNER_STATIC_NAME} PUBLIC "${SGX_SSL}/include")

TARGET_COMPILE_OPTIONS(${DATA_OWNER_STATIC_NAME} PRIVATE "${GENERIC_CXX_FLAGS}")
TARGET_COMPILE_OPTIONS(${DATA_OWNER_STATIC_NAME} PRIVATE "-nostdinc")
TARGET_COMPILE_OPTIONS(${DATA_OWNER_STATIC_NAME} PRIVATE "-nostdinc++")
TARGET_COMPILE_OPTIONS(${DATA_OWNER_STATIC_NAME} PRIVATE "-fno-builtin-printf")

TARGET_COMPILE_DEFINITIONS(${DATA_OWNER_STATIC_NAME} PRIVATE "-DUSE_DL=1")

################################################################################
