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

#include <string>
#include "db_store.h"

class DbStoreCsv : public DbStore {
    public:

        DbStoreCsv() {}

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        /**
         * Updates a key->value pair in the database store. Appends a new string
         * to the end of the value separated by comma. The behavior is similar
         * to pushing to the tail of a deque. Adds key-value pair if no entry is
         * found.
         *
         * @param table_b64     base64 encoded table name
         * @param key_b64       base64 encoded key string
         * @param value_b64     base64 encoded value string
         *
         * @return
         *  Success: void/no return
         *  Failure: throws exception
         */
        void db_store_csv_append(
            const std::string& table_b64,
            const std::string& key_b64,
            const std::string& value_b64);

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        /**
         * Updates a key->value pair in the database store. Prepends a new string
         * to the beginning of the value separated by comma. The behavior is
         * similar to pushing to the head of a deque. Adds key-value pair if no
         * entry is found.
         *
         * @param table_b64     base64 encoded table name
         * @param key_b64       base64 encoded key string
         * @param value_b64     base64 encoded value string
         *
         * @return
         *  Success: void/no return
         *  Failure: throws exception
         */
        void db_store_csv_prepend(
            const std::string& table_b64,
            const std::string& key_b64,
            const std::string& value_b64);

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        /**
         * Updates a key->value pair in the database store. Removes the first
         * string from value which is a comma separated string. The behavior
         * is similar to removing from the head of a deque. Deletes the
         * key-value pair if this is the lone element in the value.
         *
         * @param table_b64     base64 encoded table name
         * @param key_b64       base64 encoded key string
         *
         * @return
         *  Success: base64 encoded string representing the first element of the
         *           comma separated value for the key
         *  Failure: throws exception
         */
        std::string db_store_csv_pop(
            const std::string& table_b64,
            const std::string& key_b64);

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        /**
         * Updates a key->value pair in the database store conditionally.
         * Reads the first string from value which is a comma separated
         * string and removes it if the value passed in matches. The behavior
         * is similar to peeking and then removing (if matched) from the head
         * of a deque. Deletes the key-value pair if this is the lone element
         * in the value.
         *
         * @param table_b64     base64 encoded table name
         * @param key_b64       base64 encoded key string
         * @param value_b64     base64 encoded value string to match
         *
         * @return
         *  Success: base64 encoded string representing the first element of the
         *           comma separated value for the key
         *  Failure: throws exception
         */
        std::string db_store_csv_match_pop(
            const std::string& table_b64,
            const std::string& key_b64,
            const std::string& value_b64);

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        /**
         * Updates a key->value pair in the database store conditionally.
         * Reads each of the comma-separated strings and then compares it
         * with the value passed in. If there is a match, the passed value
         * is deleted. If this is the lone string, the key-value pair
         * altogether is removed.
         *
         * @param table_b64     base64 encoded table name
         * @param key_b64       base64 encoded key string
         * @param value_b64     base64 encoded value string to search and delete
         *
         * @return
         *  Success: void/no return
         *  Failure: throws exception
         */
        void db_store_csv_search_delete(
            const std::string& table_b64,
            const std::string& key_b64,
            const std::string& value_b64);

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
};
