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

# Put test artifacts under /tests subdirectory
set(TESTS_OUTPUT_DIR ${CMAKE_BINARY_DIR}/tests)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${TESTS_OUTPUT_DIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${TESTS_OUTPUT_DIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${TESTS_OUTPUT_DIR})

################################################################################
# Untrusted Test Application
################################################################################

SET(UNTRUSTED_TEST_NAME utest)
PROJECT(${UNTRUSTED_TEST_NAME} CXX)

ADD_EXECUTABLE(${UNTRUSTED_TEST_NAME} untrusted/TestUntrusted.cpp testCrypto.cpp)

# Same compile options as untrusted library
TARGET_INCLUDE_DIRECTORIES(${UNTRUSTED_TEST_NAME} PUBLIC ${SGX_SDK}/include)
TARGET_INCLUDE_DIRECTORIES(${UNTRUSTED_TEST_NAME} PRIVATE ${TCF_CORE_DIR}/common)
TARGET_INCLUDE_DIRECTORIES(${UNTRUSTED_TEST_NAME} PRIVATE ${TCF_CORE_DIR}/common/tests)
TARGET_INCLUDE_DIRECTORIES(${UNTRUSTED_TEST_NAME} PRIVATE ${TCF_CORE_DIR}/common/crypto)
TARGET_INCLUDE_DIRECTORIES(${UNTRUSTED_TEST_NAME} PRIVATE ${TCF_CORE_DIR}/common/packages/base64)

TARGET_COMPILE_OPTIONS(${UNTRUSTED_TEST_NAME} PRIVATE ${COMMON_CXX_FLAGS})

TARGET_COMPILE_DEFINITIONS(${UNTRUSTED_TEST_NAME} PRIVATE "-D_UNTRUSTED_=1")

# Link the untrusted test application against the untrusted library and openssl
TARGET_LINK_LIBRARIES(${UNTRUSTED_TEST_NAME} ${UNTRUSTED_LIB_NAME} ${OPENSSL_LDFLAGS})

# Register this application as a test
add_test(
	NAME ${UNTRUSTED_TEST_NAME}
	COMMAND env LD_LIBRARY_PATH=${OPENSSL_LIBRARY_DIRS}:${LD_LIBRARY_PATH} ./${UNTRUSTED_TEST_NAME}
	WORKING_DIRECTORY ${TESTS_OUTPUT_DIR}
)


################################################################################
# Trusted Test Application
################################################################################

ADD_SUBDIRECTORY(trusted/enclave)

SET(TRUSTED_TEST_NAME ttest)
PROJECT(${TRUSTED_TEST_NAME} C CXX)

# ENCLAVE_EDL is defined in the enclave subdirectory
SGX_EDGE_UNTRUSTED(${ENCLAVE_EDL} ENCLAVE_EDGE_SOURCES)

ADD_EXECUTABLE(${TRUSTED_TEST_NAME} trusted/app/TestApp.cpp ${TCF_CORE_DIR}/common/c11_support.cpp ${ENCLAVE_EDGE_SOURCES})

# Make sure the enclave builds before the test app that links it
ADD_DEPENDENCIES(${TRUSTED_TEST_NAME} TestEnclave)

TARGET_INCLUDE_DIRECTORIES(${TRUSTED_TEST_NAME} PUBLIC ${SGX_SDK}/include)
TARGET_INCLUDE_DIRECTORIES(${TRUSTED_TEST_NAME} PRIVATE ${TCF_CORE_DIR}/common)

TARGET_COMPILE_OPTIONS(${TRUSTED_TEST_NAME} PRIVATE ${COMMON_CXX_FLAGS})

TARGET_LINK_LIBRARIES(${TRUSTED_TEST_NAME} -Wl,-L,${SGX_SDK}/lib64)
TARGET_LINK_LIBRARIES(${TRUSTED_TEST_NAME} -Wl,-L,${SGX_SSL}/lib64)
TARGET_LINK_LIBRARIES(${TRUSTED_TEST_NAME} -Wl,-L,${SGX_SSL}/lib64/release)
TARGET_LINK_LIBRARIES(${TRUSTED_TEST_NAME} ${URTS_LIBRARY_NAME} sgx_usgxssl)
TARGET_LINK_LIBRARIES(${TRUSTED_TEST_NAME} pthread)

# Register this application as a test
add_test(
	NAME ${TRUSTED_TEST_NAME}
	COMMAND ./${TRUSTED_TEST_NAME}
	WORKING_DIRECTORY ${TESTS_OUTPUT_DIR}
)


################################################################################
# Run the tests automatically after building
################################################################################

SET(TEST_TARGET TestAfterBuild)
ADD_CUSTOM_TARGET(${TEST_TARGET} ALL COMMAND ctest --output-on-failure)
ADD_DEPENDENCIES(${TEST_TARGET} ${UNTRUSTED_TEST_NAME})
ADD_DEPENDENCIES(${TEST_TARGET} ${TRUSTED_TEST_NAME})

