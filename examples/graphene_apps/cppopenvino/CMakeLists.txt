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

cmake_minimum_required(VERSION 3.5)
set(OPENVINOWL openvinowl)
project(${OPENVINOWL} CXX)

# Use this to globally use C++11 with in our project
set(CMAKE_CXX_STANDARD 11)

# Load in pkg-config support
find_package(PkgConfig)

# Find opencv package
find_package(OpenCV)
# Find openvno inference engine package
find_package(InferenceEngine)

# toml header
set(TOML_HEADERS toml/toml11)

# Include directories
include_directories(${InferenceEngine_INCLUDE_DIRS})
include_directories(openvino/inference-engine/)
include_directories(openvino/inference-engine/samples/common/)
include_directories(openvino/inference-engine/samples/common/format_reader)
include_directories(openvino/inference-engine/src/extension)
include_directories(${InferenceEngine_INCLUDE_DIRS})
include_directories(${TOML_HEADERS})

# Openvino Library directory
link_directories($ENV{OPENVINO_LIB})

# Add source files
file(GLOB SOURCE_FILES
    "*.cpp"
    "*.h"
)

add_executable(${OPENVINOWL} ${SOURCE_FILES})

# Add zmq library to our link directive
target_link_libraries(${OPENVINOWL} PRIVATE zmq)
# InferenceEngine library
target_link_libraries(${OPENVINOWL} PRIVATE ${InferenceEngine_LIBRARIES} dl)
# Format reader
target_link_libraries(${OPENVINOWL} PRIVATE format_reader) 
# Extension
target_link_libraries(${OPENVINOWL} PRIVATE cpu_extension)

