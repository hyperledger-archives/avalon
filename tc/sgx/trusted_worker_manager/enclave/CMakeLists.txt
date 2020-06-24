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

INCLUDE(CMakeVariables.txt)
# set enclave build environment variables
CONFIG_ENCLAVE_COMMON_ENVIRONMENT()

IF(${ENCLAVE_TYPE} STREQUAL "singleton")
    ADD_DEFINITIONS(-DBUILD_SINGLETON=1)
    ADD_SUBDIRECTORY(singleton)
ELSEIF(${ENCLAVE_TYPE} STREQUAL "kme")
    ADD_DEFINITIONS(-DBUILD_KME=1)
    ADD_SUBDIRECTORY(kme)
ELSEIF(${ENCLAVE_TYPE} STREQUAL "wpe")
    ADD_DEFINITIONS(-DBUILD_WPE=1)
    ADD_SUBDIRECTORY(wpe)
ELSE()
    MESSAGE(FATAL_ERROR, "Unknown enclave build argument")
ENDIF()
