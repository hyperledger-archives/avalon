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
find_package(PkgConfig REQUIRED)

SET(DEBUG_FLAGS "-O2")
################################################################################
# Common components for both trusted and untrusted common libraries
################################################################################

FILE(GLOB PROJECT_HEADERS $ENV{TCF_HOME}/common/cpp/*.h
$ENV{TCF_HOME}/common/cpp/packages/base64/*.h)
FILE(GLOB PROJECT_SOURCES *.cpp $ENV{TCF_HOME}/common/cpp/c11_support.cpp
$ENV{TCF_HOME}/common/cpp/packages/base64/*.cpp)

SET(COMMON_PRIVATE_INCLUDE_DIRS "." $ENV{TCF_HOME}/common/cpp
$ENV{TCF_HOME}/common/cpp/packages/base64 $ENV{TCF_HOME}/shared_kv_storage/db_store)
SET(COMMON_CXX_FLAGS ${DEBUG_FLAGS} "-m64" "-fvisibility=hidden" "-fpie" "-fPIC"
"-fstack-protector" "-std=c++11" "-Wall")

################################################################################
# Database Store Library
################################################################################

SET(DB_STORE_LIB_NAME lmdb-store)
PROJECT(${DB_STORE_LIB_NAME} CXX)

ADD_LIBRARY(${DB_STORE_LIB_NAME} STATIC ${PROJECT_HEADERS} ${PROJECT_SOURCES})

TARGET_INCLUDE_DIRECTORIES(${DB_STORE_LIB_NAME} PRIVATE ${COMMON_PRIVATE_INCLUDE_DIRS})
TARGET_INCLUDE_DIRECTORIES(${DB_STORE_LIB_NAME} PUBLIC ${SGX_SDK}/include)

TARGET_COMPILE_OPTIONS(${DB_STORE_LIB_NAME} PRIVATE ${COMMON_CXX_FLAGS} ${OPENSSL_CFLAGS})

