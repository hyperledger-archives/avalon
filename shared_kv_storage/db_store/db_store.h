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

#include <string>
#include <map>

/**
 * Initialize the database store - must be called before performing gets/puts
 *
 * @param db_path       path to the persistent database store database
 * @param map_size      the maximum size of the database
 */
void db_store_init(const std::string& db_path, const size_t map_size);

/**
 * Close the database store - must be called when exiting
 *
 */
void db_store_close();

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
/**
 * Gets the size of a key in the database store
 *
 * @param table_b64     base64 encode table name
 * @param key_b64       base64 encoded key string
 *
 * @return
 *  Success: length of value corresponding to key
 *  Failure: -1
 */
int db_store_get_value_size(
    const std::string& table_b64,
    const std::string& key_b64);

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
/**
 * Gets the value corresponding to a key from the database store
 *
 * @param table_b64     base64 encode table name
 * @param key_b64       base64 encoded key string
 *
 * @return
 *  Success: base64 encoded value corresponding to key
 *  Failure: throws exception
 */
std::string db_store_get(
    const std::string& table_b64,
    const std::string& key_b64);

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
/**
 * Puts a key->value pair into the database store
 *
 * @param table_b64     base64 encode table name
 * @param key_b64       base64 encoded key string
 * @param value_b64     base64 encoded value string
 *
 * @return
 *  Success: void/no return
 *  Failure: throws exception
 */
void db_store_put(
    const std::string& table_b64,
    const std::string& key_b64,
    const std::string& value_b64);

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
/**
 * Deletes a key->value pair from the database store
 *
 * @param table_b64     base64 encode table name
 * @param key_b64       base64 encoded key string
 * @param value_b64     base64 encoded value string
 *
 * @return
 *  Success: void/no return
 *  Failure: throws exception
 */
void db_store_del(
    const std::string& table_b64,
    const std::string& key_b64,
    const std::string& value_b64);
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

