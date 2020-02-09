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

#include <algorithm>
#include <stdlib.h>
#include <string>

#include "tcf_error.h"
#include "db_store_error.h"
#include "types.h"
#include "packages/base64/base64.h"
#include "packages/db_store_wrapper.h"
#include "packages/lmdb_store.h"

#include "db_store.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void db_store_init(const std::string& db_path, const size_t map_size) {
    tcf_err_t presult = lmdb_store::db_store_init(db_path, map_size);
    db_error::ThrowIf<db_error::RuntimeError>(presult, "db store init failed");
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void db_store_close() {
    lmdb_store::db_store_close();
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
int db_store_get_value_size(
    const std::string& table_b64,
    const std::string& key_b64) {
    ByteArray raw_key = base64_decode(key_b64);

    bool is_present;
    size_t value_size;
    tcf_err_t presult = db_store::db_store_get_value_size(table_b64, raw_key, &is_present, &value_size);
    db_error::ThrowIf<db_error::RuntimeError>(presult, "db store get value size failed");

    /*
     * TODO
     *
     * It would be better to provide a "value not found" error to the client via another
     * mechanism (404 error?) instead of returning a negative size.
     */
    if (is_present) {
        return (int)value_size;
    } else {
        return -1;
    }
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
std::string db_store_get(
    const std::string& table_b64,
    const std::string& key_b64) {
    ByteArray raw_key(key_b64.begin(), key_b64.end());
    ByteArray raw_value;

    tcf_err_t presult = db_store::db_store_get(table_b64, raw_key, raw_value);
    db_error::ThrowIf<db_error::RuntimeError>(presult, "db store get failed");

    std::string out_string;
    std::transform(raw_value.begin(), raw_value.end(), std::back_inserter(out_string),
        [](unsigned char c) -> char { return (char)c; });
    return out_string;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void db_store_put(
    const std::string& table_b64,
    const std::string& key_b64,
    const std::string& value_b64) {
    ByteArray raw_key(key_b64.begin(), key_b64.end());
    ByteArray raw_value(value_b64.begin(), value_b64.end());
    tcf_err_t presult = db_store::db_store_put(table_b64, raw_key, raw_value);
    db_error::ThrowIf<db_error::RuntimeError>(presult, "db store put failed");
}
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void db_store_del(
    const std::string& table_b64,
    const std::string& key_b64,
    const std::string& value_b64) {
    ByteArray raw_key(key_b64.begin(), key_b64.end());
    ByteArray raw_value(value_b64.begin(), value_b64.end());
    tcf_err_t presult = db_store::db_store_del(table_b64, raw_key, raw_value);
    db_error::ThrowIf<db_error::RuntimeError>(presult, "db store delete failed");
}
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

