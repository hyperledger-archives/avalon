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

LIST(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

SET (EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR}/bin)
SET (LIBRARY_OUTPUT_PATH ${CMAKE_BINARY_DIR}/lib)

SET(DEPS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/deps")
SET(TCF_TOP_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../../../")
SET(TCF_CORE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../")

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Configure Environment
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

SET(TCF_ENCLAVE_CODE_SIGN_PEM "$ENV{TCF_ENCLAVE_CODE_SIGN_PEM}")
if("${TCF_ENCLAVE_CODE_SIGN_PEM} " STREQUAL " ")
    message(FATAL_ERROR "TCF_ENCLAVE_CODE_SIGN_PEM environment variable not defined!")
endif()

SET(SGX_MODE "$ENV{SGX_MODE}")
if("${SGX_MODE} " STREQUAL " ")
    SET(SGX_MODE "SIM")
    message(STATUS "Setting default SGX_MODE=${SGX_MODE}")
endif()
IF("${SGX_MODE}" STREQUAL "SIM")
    OPTION(SGX_USE_SIMULATOR "Use the sgx simulator" TRUE)
ELSE()
    OPTION(SGX_USE_SIMULATOR "Use the sgx simulator" FALSE)
ENDIF()

SET(SGX_SDK "$ENV{SGX_SDK}")
if("${SGX_SDK} " STREQUAL " ")
    message(FATAL_ERROR "SGX_SDK environment variable not defined!")
endif()
SET(SGX_SSL "$ENV{SGX_SSL}")
if("${SGX_SSL} " STREQUAL " ")
    SET(SGX_SSL "/opt/intel/sgxssl")
    message(STATUS "Setting default SGX_SSL=${SGX_SSL}")
endif()

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# ADDITIONAL LIBRARIES
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# sgx edger is a utility that generates edl artifacts
SET(SGX_EDGER "${SGX_SDK}/bin/x64/sgx_edger8r")
SET(SGX_SIGN "${SGX_SDK}/bin/x64/sgx_sign")

SET(SGX_INCLUDE "${SGX_SDK}/include")
SET(SGX_SSL_INCLUDE "${SGX_SSL}/include")
SET(SGX_ENCLAVE_INCLUDE "${SGX_SDK}/include"
                        "${SGX_SDK}/include/tlibc"
                        "${SGX_SDK}/include/libcxx")

SET(SGX_LIBS_TRUSTED_NAMES sgx_tstdc sgx_tstdcxx sgx_tcrypto)
SET(SGX_LIBS_UNTRUSTED_NAMES )

SET(SGX_LIBS_UNTRUSTED_NAMES ${SGX_LIBS_UNTRUSTED_NAMES} pthread )

IF(${SGX_USE_SIMULATOR})
    ADD_DEFINITIONS(-D SGX_SIMULATOR)
    SET(SGX_LIBS_TRUSTED_NAMES sgx_trts_sim sgx_tservice_sim ${SGX_LIBS_TRUSTED_NAMES})
    SET(SGX_LIBS_UNTRUSTED_NAMES sgx_urts_sim sgx_uae_service_sim ${SGX_LIBS_UNTRUSTED_NAMES})
    SET(TRTS_LIBRARY_NAME "sgx_trts_sim")
    SET(SERVICE_LIBRARY_NAME "sgx_tservice_sim")
ELSE()
    SET(SGX_LIBS_TRUSTED_NAMES sgx_trts sgx_tservice ${SGX_LIBS_TRUSTED_NAMES})
    SET(SGX_LIBS_UNTRUSTED_NAMES sgx_urts sgx_uae_service ${SGX_LIBS_UNTRUSTED_NAMES})
    SET(TRTS_LIBRARY_NAME "sgx_trts")
    SET(SERVICE_LIBRARY_NAME "sgx_tservice")
ENDIF()

FOREACH(lib ${SGX_LIBS_TRUSTED_NAMES} ${SGX_LIBS_UNTRUSTED_NAMES})
    SET(${lib} ${lib})
ENDFOREACH(lib)

FOREACH(lib ${SGX_LIBS_TRUSTED_NAMES})
    SET(SGX_LIBS_TRUSTED ${SGX_LIBS_TRUSTED} ${${lib}})
ENDFOREACH(lib)

FOREACH(lib ${SGX_LIBS_UNTRUSTED_NAMES})
    SET(SGX_LIBS_UNTRUSTED ${SGX_LIBS_UNTRUSTED} ${${lib}})
ENDFOREACH(lib)

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
FUNCTION(SGX_EDGE_TRUSTED EDL EDGE_FILES)
    GET_FILENAME_COMPONENT(EDL_BASE_NAME ${EDL} NAME_WE)
    GET_FILENAME_COMPONENT(EDL_DIR_NAME ${EDL} DIRECTORY)
    INCLUDE_DIRECTORIES(${CMAKE_CURRENT_BINARY_DIR})

    SET (EDGE_FILES_LIST "${CMAKE_CURRENT_BINARY_DIR}/${EDL_BASE_NAME}_t.h" "${CMAKE_CURRENT_BINARY_DIR}/${EDL_BASE_NAME}_t.c")
    SET (${EDGE_FILES} ${EDGE_FILES_LIST} PARENT_SCOPE)
    ADD_CUSTOM_COMMAND( OUTPUT ${EDGE_FILES_LIST}
        COMMAND "${SGX_EDGER}" --trusted ${EDL} --search-path ${SGX_INCLUDE} --search-path ${SGX_SSL_INCLUDE} --search-path ${EDL_DIR_NAME}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        DEPENDS ${EDL}
    )
ENDFUNCTION()

FUNCTION(SGX_SIGN_ENCLAVE TARGET KEY_FILE CONFIG)
    SET (ENCLAVE $<TARGET_FILE:${TARGET}>)

    SET (SIGNED_ENCLAVE ${LIBRARY_OUTPUT_PATH}/${CMAKE_CFG_INTDIR}/${TARGET}.signed${CMAKE_SHARED_LIBRARY_SUFFIX})
    SET (SIGNED_ENCLAVE ${SIGNED_ENCLAVE} PARENT_SCOPE)
    SET (SIGNED_ENCLAVE_METADATA ${SIGNED_ENCLAVE}".meta")
    ADD_CUSTOM_COMMAND( TARGET ${TARGET}
        POST_BUILD
        COMMAND "${SGX_SIGN}" sign -key "${KEY_FILE}" -enclave "${ENCLAVE}" -out "${SIGNED_ENCLAVE}" -dumpfile "${SIGNED_ENCLAVE_METADATA}" -config "${CONFIG}"
    )
ENDFUNCTION()

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

FILE(GLOB PROJECT_HEADERS *.h)
FILE(GLOB PROJECT_SOURCES *.cpp *.c)
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

# These compiler and linker flags for g++/gcc were derived from the make
# files provided with the SGX sample enclave
# To generate a proper enclave, it is recommended to follow below guideline
# to link the trusted libraries:
#    1. Link sgx_trts with the `--whole-archive' and `--no-whole-archive'
#       options, so that the whole content of trts is included in the
#       enclave.
#    2. For other libraries, you just need to pull the required symbols.
#       Use `--start-group' and `--end-group' to link these libraries.
# Do NOT move the libraries linked with `--start-group' and `--end-group'
# within `--whole-archive' and `--no-whole-archive' options.  Otherwise,
# you may get some undesirable errors.

SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -m64")
IF(DEFINED ENV{TCF_DEBUG_BUILD} AND "$ENV{TCF_DEBUG_BUILD}" STREQUAL "1")
  SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g")
  SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Og")
  ADD_DEFINITIONS(-DTCF_DEBUG_BUILD=1)
ELSE()
  SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2")
  REMOVE_DEFINITIONS(-DTCF_DEBUG_BUILD)
ENDIF()

SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -nostdinc")
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fvisibility=hidden")
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fpie")
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fstack-protector")
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -nostdinc++")

SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -m64")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -O2")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,--no-undefined")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -nostdlib")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -nodefaultlibs")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -nostartfiles")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-Bstatic")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-Bsymbolic")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,--no-undefined")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-pie,-eenclave_entry")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,--export-dynamic")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,--defsym,__ImageBase=0")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,--version-script=${CMAKE_CURRENT_SOURCE_DIR}/tcf_enclave.lds")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-L,$ENV{SGX_SDK}/lib64")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-L,$ENV{SGX_SSL}/lib64")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-L,$ENV{SGX_SSL}/lib64/release")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-L,${TCF_TOP_DIR}/common/cpp/build")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-L,${TCF_CORE_DIR}/trusted_worker_manager/common/build")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-L,${TCF_TOP_DIR}/common/sgx_workload/build/workload")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-L,${TCF_TOP_DIR}/common/sgx_workload/build/iohandler")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-L,${TCF_TOP_DIR}/examples/apps/build/echo/workload")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-L,${TCF_TOP_DIR}/examples/apps/build/heart_disease_eval/workload")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-L,${TCF_TOP_DIR}/examples/apps/build/inside_out_demo/workload")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-L,${TCF_TOP_DIR}/examples/apps/build/simple_wallet/workload")
SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-L,$ENV{SGX_SSL}/lib64")
# Remove all the default windows libraries (kernel32, etc)
SET(CMAKE_C_STANDARD_LIBRARIES_INIT "")
SET(CMAKE_C_STANDARD_LIBRARIES "")
SET(CMAKE_CXX_STANDARD_LIBRARIES "")

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

