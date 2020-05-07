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

FILE(GLOB PROJECT_HEADERS "*.h")
FILE(GLOB PROJECT_SOURCES "*.cpp")

SET(GENERIC_CXX_FLAGS ${DEBUG_FLAGS} "-Wall" "-fPIC" "-Wno-write-strings" "-std=c++11")

# Replace $WORKLOAD_STATIC_NAME$ below with a workload build name, e.g. hello_world
SET(WORK_ORDER_STATIC_NAME $WORKLOAD_STATIC_NAME$)
PROJECT(${WORK_ORDER_STATIC_NAME} CXX)

ADD_LIBRARY(${WORK_ORDER_STATIC_NAME} STATIC ${PROJECT_HEADERS} ${PROJECT_SOURCES})

TARGET_INCLUDE_DIRECTORIES(${WORK_ORDER_STATIC_NAME} PRIVATE ${GENERIC_PRIVATE_INCLUDE_DIRS})
TARGET_INCLUDE_DIRECTORIES(${WORK_ORDER_STATIC_NAME} PUBLIC ${GENERIC_PUBLIC_INCLUDE_DIRS})
TARGET_INCLUDE_DIRECTORIES(${WORK_ORDER_STATIC_NAME} PUBLIC "${SGX_SDK}/include/tlibc")
TARGET_INCLUDE_DIRECTORIES(${WORK_ORDER_STATIC_NAME} PUBLIC "${SGX_SDK}/include/libcxx")
#TARGET_INCLUDE_DIRECTORIES(${WORK_ORDER_STATIC_NAME} PUBLIC $ENV{TCF_HOME}/common/cpp/crypto)

TARGET_COMPILE_OPTIONS(${WORK_ORDER_STATIC_NAME} PRIVATE "${GENERIC_CXX_FLAGS}")
TARGET_COMPILE_OPTIONS(${WORK_ORDER_STATIC_NAME} PRIVATE "-nostdinc")
TARGET_COMPILE_OPTIONS(${WORK_ORDER_STATIC_NAME} PRIVATE "-nostdinc++")
TARGET_COMPILE_OPTIONS(${WORK_ORDER_STATIC_NAME} PRIVATE "-fno-builtin-printf")

TARGET_COMPILE_DEFINITIONS(${WORK_ORDER_STATIC_NAME} PRIVATE "-DUSE_DL=1")

################################################################################
