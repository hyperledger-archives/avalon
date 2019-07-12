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

################################################################################
# Common components for both trusted and untrusted variants
################################################################################
if(NOT UNTRUSTED_ONLY) 
FILE(GLOB PROJECT_HEADERS *.h)
FILE(GLOB PROJECT_SOURCES *.cpp)

PROJECT(tcf_work_order_interface CXX)

ADD_LIBRARY(${PROJECT_NAME} STATIC ${PROJECT_HEADERS} ${PROJECT_SOURCES})

TARGET_COMPILE_OPTIONS(${PROJECT_NAME} PRIVATE -fpic -Wno-write-strings -std=c++11)
TARGET_COMPILE_OPTIONS(${PROJECT_NAME} PRIVATE "-nostdinc")
TARGET_COMPILE_OPTIONS(${PROJECT_NAME} PRIVATE "-nostdinc++")
TARGET_COMPILE_OPTIONS(${PROJECT_NAME} PRIVATE "-fno-builtin-printf")


TARGET_INCLUDE_DIRECTORIES(${PROJECT_NAME} PUBLIC "${SGX_SDK}/include")
TARGET_INCLUDE_DIRECTORIES(${PROJECT_NAME} PUBLIC "${SGX_SDK}/include/tlibc")
TARGET_INCLUDE_DIRECTORIES(${PROJECT_NAME} PUBLIC "${SGX_SDK}/include/libcxx")
TARGET_INCLUDE_DIRECTORIES(${PROJECT_NAME} PUBLIC "${SGX_SSL}/include")
TARGET_INCLUDE_DIRECTORIES(${PROJECT_NAME} PUBLIC "../")
TARGET_INCLUDE_DIRECTORIES(${PROJECT_NAME} PRIVATE ${TCF_CORE_DIR}/common/packages/parson)
endif()
