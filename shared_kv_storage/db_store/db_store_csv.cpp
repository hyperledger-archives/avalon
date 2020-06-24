/* Copyright 2020 Intel Corporation
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

#include <algorithm>
#include <stdlib.h>
#include <string>

#include "tcf_error.h"
#include "db_store_error.h"
#include "types.h"
#include "packages/base64/base64.h"
#include "packages/db_store_wrapper.h"
#include "packages/lmdb_store.h"

#include "db_store_csv.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void DbStoreCsv::db_store_csv_append(
    const std::string& table_b64,
    const std::string& key_b64,
    const std::string& value_b64){
    ByteArray raw_key(key_b64.begin(), key_b64.end());
    ByteArray raw_value(value_b64.begin(), value_b64.end());
    tcf_err_t presult = db_store::db_store_csv_extend(table_b64, raw_key, raw_value, false);
    db_error::ThrowIf<db_error::RuntimeError>(presult, "db store update(append) failed");
}
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void DbStoreCsv::db_store_csv_prepend(
    const std::string& table_b64,
    const std::string& key_b64,
    const std::string& value_b64){
    ByteArray raw_key(key_b64.begin(), key_b64.end());
    ByteArray raw_value(value_b64.begin(), value_b64.end());
    tcf_err_t presult = db_store::db_store_csv_extend(table_b64, raw_key, raw_value, true);
    db_error::ThrowIf<db_error::RuntimeError>(presult, "db store update(prepend) failed");
}
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
std::string DbStoreCsv::db_store_csv_pop(
    const std::string& table_b64,
    const std::string& key_b64){

    ByteArray raw_key(key_b64.begin(), key_b64.end());
    ByteArray raw_value;

    tcf_err_t presult = db_store::db_store_csv_pop(table_b64, raw_key, raw_value, false);
    db_error::ThrowIf<db_error::RuntimeError>(presult, "db store update(pop) failed");

    std::string out_string;
    // out_string being a std::string expects char datatype as the building block. Hence,
    // the raw bytes (unsigned char) that are retrieved from LMDB needs casting.
    std::transform(raw_value.begin(), raw_value.end(), std::back_inserter(out_string),
        [](unsigned char c) -> char { return (char)c; });
    return out_string;
}
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
std::string DbStoreCsv::db_store_csv_match_pop(
    const std::string& table_b64,
    const std::string& key_b64,
    const std::string& value_b64){

    ByteArray raw_key(key_b64.begin(), key_b64.end());
    ByteArray raw_value(value_b64.begin(), value_b64.end());

    tcf_err_t presult = db_store::db_store_csv_pop(table_b64, raw_key, raw_value, true);
    db_error::ThrowIf<db_error::RuntimeError>(presult, "db store update(match_pop) failed");

    return value_b64;
}
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void DbStoreCsv::db_store_csv_search_delete(
    const std::string& table_b64,
    const std::string& key_b64,
    const std::string& value_b64){
    ByteArray raw_key(key_b64.begin(), key_b64.end());
    ByteArray raw_value(value_b64.begin(), value_b64.end());
    tcf_err_t presult = db_store::db_store_csv_search_delete(table_b64, raw_key, raw_value);
    db_error::ThrowIf<db_error::RuntimeError>(presult, "db store update(search_delete) failed");
}
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
