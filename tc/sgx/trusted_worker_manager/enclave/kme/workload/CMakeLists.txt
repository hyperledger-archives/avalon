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

SET(SGX_MODE "$ENV{SGX_MODE}")
if("${SGX_MODE} " STREQUAL " ")
    SET(SGX_MODE "SIM")
    message(STATUS "Setting default SGX_MODE=${SGX_MODE}")
endif()
IF("${SGX_MODE}" STREQUAL "SIM")
    OPTION(SGX_USE_SIMULATOR "Use the Intel SGX simulator" TRUE)
ELSE()
    OPTION(SGX_USE_SIMULATOR "Use the Intel SGX simulator" FALSE)
ENDIF()

SET(SGX_SDK "$ENV{SGX_SDK}")
if("${SGX_SDK} " STREQUAL " ")
    SET(SGX_SDK "/opt/intel/sgxsdk")
endif()

SET(SGX_SSL "$ENV{SGX_SSL}")
if("${SGX_SSL} " STREQUAL " ")
    SET(SGX_SSL "/opt/intel/sgxssl")
endif()

SET(TCF_TOP_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../../../../../")

# Generates static library for Key Management Enclave workload
################################################################################

FILE(GLOB PROJECT_HEADERS "*.h")
FILE(GLOB PROJECT_SOURCES "*.cpp")

SET(GENERIC_CXX_FLAGS ${DEBUG_FLAGS} "-Wall" "-fPIC" "-Wno-write-strings" "-std=c++11")
SET(GENERIC_PRIVATE_INCLUDE_DIRS "." "${TCF_TOP_DIR}/common/cpp"
    "${TCF_TOP_DIR}/common/cpp/crypto"
    "${TCF_TOP_DIR}/common/cpp/packages/parson"
SET(GENERIC_PUBLIC_INCLUDE_DIRS "${SGX_SDK}/include" "${SGX_SSL_INCLUDE}")
    "${TCF_TOP_DIR}/tc/sgx/trusted_worker_manager/enclave"
    "${TCF_TOP_DIR}/tc/sgx/trusted_worker_manager/enclave/kme"
    "${TCF_TOP_DIR}/common/sgx_workload/workload")
SET(GENERIC_PUBLIC_INCLUDE_DIRS "${SGX_SDK}/include")

SET(KME_WORKLOAD_STATIC_NAME kme_workload)
PROJECT(${KME_WORKLOAD_STATIC_NAME} CXX)
IF(${SGX_USE_SIMULATOR})
   ADD_DEFINITIONS(-D SGX_SIMULATOR)
ENDIF()

ADD_LIBRARY(${KME_WORKLOAD_STATIC_NAME} STATIC ${PROJECT_HEADERS} ${PROJECT_SOURCES})

TARGET_INCLUDE_DIRECTORIES(${KME_WORKLOAD_STATIC_NAME} PRIVATE ${GENERIC_PRIVATE_INCLUDE_DIRS})
TARGET_INCLUDE_DIRECTORIES(${KME_WORKLOAD_STATIC_NAME} PUBLIC ${GENERIC_PUBLIC_INCLUDE_DIRS})
TARGET_INCLUDE_DIRECTORIES(${KME_WORKLOAD_STATIC_NAME} PUBLIC "${SGX_SDK}/include/tlibc")
TARGET_INCLUDE_DIRECTORIES(${KME_WORKLOAD_STATIC_NAME} PUBLIC "${SGX_SDK}/include/libcxx")
TARGET_INCLUDE_DIRECTORIES(${KME_WORKLOAD_STATIC_NAME} PUBLIC "${SGX_SSL}/include")

TARGET_COMPILE_OPTIONS(${KME_WORKLOAD_STATIC_NAME} PRIVATE "${GENERIC_CXX_FLAGS}")
TARGET_COMPILE_OPTIONS(${KME_WORKLOAD_STATIC_NAME} PRIVATE "-nostdinc")
TARGET_COMPILE_OPTIONS(${KME_WORKLOAD_STATIC_NAME} PRIVATE "-nostdinc++")
TARGET_COMPILE_OPTIONS(${KME_WORKLOAD_STATIC_NAME} PRIVATE "-fno-builtin-printf")

TARGET_COMPILE_DEFINITIONS(${KME_WORKLOAD_STATIC_NAME} PRIVATE "-DUSE_DL=1")

################################################################################
