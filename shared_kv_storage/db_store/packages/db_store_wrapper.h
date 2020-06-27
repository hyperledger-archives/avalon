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

#pragma once

#include "tcf_error.h"
#include "types.h"


/*
 * Many different implementations of this database store API exist within TCF
 * The idea is that every implementation has these methods, but they may
 * have their own methods (particularly initialization) in their own
 * specific namespaces
 */
namespace db_store {
    /**
     * Gets the size of a key in the database store
     * Primary expected use: ocall
     *
     * @param table		table name
     * @param inId          pointer to id byte array
     * @param inIdSize      length of inId
     * @param outIsPresent  [output] true if value is present, false if not
     * @param outValueSize  [output] size (in # bytes) of value if present
     *
     * @return
     *  TCF_SUCCESS  outValueSize set to the number of bytes of value
     *  else         failed, outValueSize undefined
     */
    tcf_err_t db_store_get_value_size(
        const std::string& table,
        const uint8_t* inId,
        const size_t inIdSize,
        bool* outIsPresent,
        size_t* outValueSize);

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    /**
     * Gets a value from the database store
     * Primary expected use: ocall
     *
     * @param table         table name
     * @param inId          pointer to id byte array
     * @param inIdSize      length of inId
     * @param outValue      [output] buffer where value should be copied
     * @param inValueSize   length of caller's outValue buffer
     *
     * @return
     *  TCF_SUCCESS  outValue contains the requested value
     *  else         failed, outValue unchanged
     */
    tcf_err_t db_store_get(
        const std::string& table,
        const uint8_t* inId,
        const size_t inIdSize,
        uint8_t *outValue,
        const size_t inValueSize);

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    /**
     * Gets a comma separated string of keys
     * Primary expected use: db_store_get to do lookup
     *
     * @param table         table name
     * @param inId          pointer to id byte array
     * @param inIdSize      length of inId
     *
     * @return
     *  Table_keys   contains the keys
     *  else         returns empty string
     */
    std::string db_store_get_all(
        const std::string& table,
        const uint8_t* inId,
        const size_t inIdSize);

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    /**
     * Puts a value into the database store
     * Primary expected use: ocall
     *
     * @param table         table name
     * @param inId          pointer to id byte array
     * @param inIdSize      length of inId
     * @param inValue       pointer to value byte array
     * @param inValueSize   length of inValue
     *
     * @return
     *  TCF_SUCCESS  id->value stored
     *  else         failed, database store unchanged
     */
    tcf_err_t db_store_put(
        const std::string& table,
        const uint8_t* inId,
        const size_t inIdSize,
        const uint8_t* inValue,
        const size_t inValueSize);

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    /**
     * Deletes a key/value from the database store
     * Primary expected use: ocall
     *
     * @param table         table name
     * @param inId          pointer to id byte array
     * @param inIdSize      length of inId
     * @param inValue       pointer to value byte array
     * @param inValueSize   length of inValue
     *
     * @return
     *  TCF_SUCCESS  id->value stored
     *  else         failed, database store unchanged
     */
    tcf_err_t db_store_del(
        const std::string& table,
        const uint8_t* inId,
        const size_t inIdSize,
        const uint8_t* inValue,
        const size_t inValueSize);


    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    /**
     * Gets the size of a value in the database store
     * Primary expected use: python / untrusted side
     *
	 * @param table         table name
     * @param inId          id byte array
     * @param outIsPresent  [output] true if value is present, false if not
     * @param outValueSize  [output] size (in # bytes) of value if present
     *
     * @return
     *  TCF_SUCCESS  outValueSize set to the number of bytes of value
     *  else         failed, outValueSize undefined
     */
    tcf_err_t db_store_get_value_size(
        const std::string& table,
        const ByteArray& inId,
        bool* outIsPresent,
        size_t* outValueSize);

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    /**
     * Gets a value from the database store
     * Primary expected use: python / untrusted side
     *
     * @param table         table name
     * @param inId      id byte array
     * @param outValue  [output] where data will be written
     *
     * @return
     *  TCF_SUCCESS   outValue contains the requested value
     *  TCF_ERR_VALUE  key was not present in the database store
     *  else          failed, outValue unchanged
     */
    tcf_err_t db_store_get(
        const std::string& table,
        const ByteArray& inId,
        ByteArray& outValue);

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    /**
     * Puts a value into the database store
     * Primary expected use: python / untrusted side
     *
     * @param table         table name
     * @param inId      id byte array
     * @param inValue    data to be written
     *
     * @return
     *  TCF_SUCCESS  id->value stored
     *  else         failed, d store unchanged
     */
    tcf_err_t db_store_put(
        const std::string& table,
        const ByteArray& inId,
        const ByteArray& inValue);

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    /**
     * Deletes a key/value from the database store
     * Primary expected use: python / untrusted side
     *
     * @param table         table name
     * @param inId      id byte array
     * @param inValue    data to be written
     *
     * @return
     *  TCF_SUCCESS  id->value deleted
     *  else         failed, d store unchanged
     */
    tcf_err_t db_store_del(
        const std::string& table,
        const ByteArray& inId,
        const ByteArray& inValue);

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    /**
     * Updates a key->value pair in the database store. Appends/prepends a
     * new string to the value separated by comma. The behavior is similar
     * to pushing to the head/tail of a deque. Adds key-value pair if no
     * entry is found.
     * Primary expected use: python / untrusted side
     *
     * @param table     table name
     * @param inId      id byte array
     * @param inValue   data to be appended/written
     * @param isPrepend flag to indicate if it is a prepend operation or append
     *
     * @return
     *  TCF_SUCCESS  id->value updated/stored
     *  else         failed, data store unchanged
     */
    tcf_err_t db_store_csv_extend(
        const std::string& table,
        const ByteArray& inId,
        const ByteArray& inValue,
        const bool isPrepend);

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    /**
     * Updates a key->value pair in the database store. Removes the first
     * string from value which is a comma separated string. The behavior
     * is similar to removing from the head of a deque. Deletes the
     * key-value pair if this is the lone element in the value.
     * Primary expected use: python / untrusted side
     *
     * @param table      table name
     * @param inId       id byte array
     * @param outValue   data to be written
     * @param isMatch    flag to indicate if a match is required before pop
     *
     * @return
     *  TCF_SUCCESS    outValue contains the first element in the value
     *                 field and it is removed from data store
     *  TCF_ERR_VALUE  key was not present in the database store
     *  else           failed, outValue unchanged and data store unchanged
     */
    tcf_err_t db_store_csv_pop(
        const std::string& table,
        const ByteArray& inId,
        ByteArray& outValue,
        const bool isMatch);

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    /**
     * Updates a key->value pair in the database store. Reads each of the
     * comma-separated strings and then compares it with the value passed
     * in. If there is a match, the passed value is deleted. If this is the
     * lone string, the key-value pair altogether is removed.
     * Primary expected use: python / untrusted side
     *
     * @param table     table name
     * @param inId      id byte array
     * @param inValue   data to be deleted
     *
     * @return
     *  TCF_SUCCESS  id->value updated/deleted
     *  else         failed, data store unchanged
     */
    tcf_err_t db_store_csv_search_delete(
        const std::string& table,
        const ByteArray& inId,
        const ByteArray& inValue);

}  /* namespace db_store */

