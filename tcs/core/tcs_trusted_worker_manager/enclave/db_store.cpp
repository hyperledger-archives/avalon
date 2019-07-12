/* Copyright 2018 Intel Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/*
 * Within the enclave, the database store API is a wrapper around making
 * ocall's to retrieve state from the client
 */

#include <string.h>
#include "error.h"
#include "hex_string.h"
#include "tcf_error.h"
#include "types.h"

#include "db_store.h"

#include "enclave_t.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t tcf::db_store::db_store_get_value_size(
    const std::string& table,
    const uint8_t* inId,
    const size_t inIdSize,
    bool* outIsPresent,
    size_t* outValueSize) {
    tcf_err_t ret;
    int sgx_ret = ocall_db_store_get_value_size(&ret, table.c_str(), inId, inIdSize, outIsPresent, outValueSize);
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        sgx_ret != 0, "sgx failed during head request on the database store");
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        ret != 0, "head request failed on the database store");

    return TCF_SUCCESS;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t tcf::db_store::db_store_get(
    const std::string& table,
    const uint8_t* inId,
    const size_t inIdSize,
    uint8_t* outValue,
    const size_t inValueSize) {
    tcf_err_t ret;
    int sgx_ret = ocall_db_store_get(&ret, table.c_str(), inId, inIdSize, outValue, inValueSize);
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        sgx_ret != 0, "sgx failed during get request on the database store");
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        ret != 0, "get request failed on the database store");

    return TCF_SUCCESS;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t tcf::db_store::db_store_put(
    const std::string& table,
    const uint8_t* inId,
    const size_t inIdSize,
    const uint8_t* inValue,
    const size_t inValueSize) {
    tcf_err_t ret;
    int sgx_ret = ocall_db_store_put(&ret, table.c_str(), inId, inIdSize, inValue, inValueSize);
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        sgx_ret != 0, "sgx failed during put to the database store");
    tcf::error::ThrowIf<tcf::error::RuntimeError>(ret != 0, "failed to put to the database store");

    return TCF_SUCCESS;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t tcf::db_store::db_store_get_value_size(
    const std::string& table,
    const ByteArray& inId,
    bool* outIsPresent,
    size_t* outValueSize) {
    return db_store_get_value_size(table, inId.data(), inId.size(), outIsPresent, outValueSize);
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t tcf::db_store::db_store_get(
    const std::string& table,
    const ByteArray& inId,
    ByteArray& outValue) {
    tcf_err_t result = TCF_SUCCESS;

    // Get the size of the state database
    bool isPresent;
    size_t value_size;
    result = db_store_get_value_size(table, inId.data(), inId.size(), &isPresent, &value_size);
    if (result != TCF_SUCCESS) {
        return result;
    } else if (!isPresent) {
        return TCF_ERR_VALUE;
    }

    // Resize the output array
    outValue.resize(value_size);

    // Fetch the state from the database storage
    result = db_store_get(table, inId.data(), inId.size(), &outValue[0], value_size);
    if (result != TCF_SUCCESS) {
        return result;
    }
    return result;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t tcf::db_store::db_store_put(
    const std::string& table,
    const ByteArray &inId,
    const ByteArray &inValue) {
    return (tcf_err_t)db_store_put(table, inId.data(), inId.size(), inValue.data(), inValue.size());
}

