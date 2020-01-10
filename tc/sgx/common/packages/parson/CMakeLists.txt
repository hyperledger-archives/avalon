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
find_package(PkgConfig REQUIRED)

option(UNTRUSTED_ONLY "Build only untrusted components" OFF)

################################################################################
# Common components for both trusted and untrusted parson libraries
################################################################################

FILE(GLOB PROJECT_HEADERS *.h)
FILE(GLOB PROJECT_SOURCES *.cpp)

SET(COMMON_CXX_FLAGS ${DEBUG_FLAGS} "-m64" "-fvisibility=hidden" "-fpie" "-fPIC" "-fstack-protector" "-std=c++11" "-Wall")

################################################################################
# Untrusted Parson Library
################################################################################

SET(UNTRUSTED_LIB_NAME uavalon-parson)
PROJECT(${UNTRUSTED_LIB_NAME} CXX)

ADD_LIBRARY(${UNTRUSTED_LIB_NAME} STATIC ${PROJECT_HEADERS} ${PROJECT_SOURCES})

TARGET_COMPILE_OPTIONS(${UNTRUSTED_LIB_NAME} PRIVATE ${COMMON_CXX_FLAGS})

TARGET_COMPILE_DEFINITIONS(${UNTRUSTED_LIB_NAME} PRIVATE "-D_UNTRUSTED_=1")

################################################################################
# Trusted Parson Library
################################################################################

if(NOT UNTRUSTED_ONLY)
        SET(TRUSTED_LIB_NAME tavalon-parson)
        PROJECT(${TRUSTED_LIB_NAME} CXX)

        ADD_LIBRARY(${TRUSTED_LIB_NAME} STATIC ${PROJECT_HEADERS} ${PROJECT_SOURCES})

        TARGET_INCLUDE_DIRECTORIES(${TRUSTED_LIB_NAME} PUBLIC ${SGX_SDK}/include)
        TARGET_INCLUDE_DIRECTORIES(${TRUSTED_LIB_NAME} PUBLIC ${SGX_SSL}/include)
        TARGET_INCLUDE_DIRECTORIES(${TRUSTED_LIB_NAME} PUBLIC ${SGX_SDK}/include/tlibc)
        TARGET_INCLUDE_DIRECTORIES(${TRUSTED_LIB_NAME} PUBLIC ${SGX_SDK}/include/libcxx)

        TARGET_COMPILE_OPTIONS(${TRUSTED_LIB_NAME} PRIVATE ${COMMON_CXX_FLAGS})
        TARGET_COMPILE_OPTIONS(${TRUSTED_LIB_NAME} PRIVATE -nostdinc)
        TARGET_COMPILE_OPTIONS(${TRUSTED_LIB_NAME} PRIVATE -nostdinc++)
        TARGET_COMPILE_OPTIONS(${TRUSTED_LIB_NAME} PRIVATE -fno-builtin-printf)
endif()

