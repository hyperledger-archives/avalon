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

#include <bits/stdc++.h>
#include <stdexcept>
#include <pthread.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include "lmdb.h"
#include "c11_support.h"
#include "hex_string.h"
#include "db_store_error.h"
#include "tcf_error.h"
#include "types.h"
#define MAX_DBS 20

/* Common API for all database stores */
#include "db_store_wrapper.h"
/* API for this specific LMDB-backed database store */
#include "lmdb_store.h"


/* -----------------------------------------------------------------
 * CLASS: SafeThreadLock
 *
 * This class initializes the lock for serializing  and wraps transactions to
 * ensure that the resources are released when the object is deallocated.
 * ----------------------------------------------------------------- */

/* Lock to protect access to the database */
static pthread_mutex_t lmdb_store_lock = PTHREAD_MUTEX_INITIALIZER;

class SafeThreadLock {
public:
    SafeThreadLock(void) {
        pthread_mutex_lock(&lmdb_store_lock);
    }

    ~SafeThreadLock(void) {
        pthread_mutex_unlock(&lmdb_store_lock);
    }
};

/* -----------------------------------------------------------------
 * CLASS: SafeUpdateLock
 *
 * This class initializes a mutex lock to serialize csv update related
 * transactions.
 * ----------------------------------------------------------------- */

/* Lock to protect access to the database */
static pthread_mutex_t csv_update_lock = PTHREAD_MUTEX_INITIALIZER;

class SafeUpdateLock {
public:
    SafeUpdateLock(void) {
        pthread_mutex_lock(&csv_update_lock);
    }

    ~SafeUpdateLock(void) {
        pthread_mutex_unlock(&csv_update_lock);
    }
};

/* -----------------------------------------------------------------
 * CLASS: SafeTransaction
 *
 * This class initializes the lmdb database and wraps transactions to
 * ensure that the resources are released when the object is deallocated.
 * ----------------------------------------------------------------- */



/* @TODO : Shift from functional to object-oriented approach is required for
 * this file. Upgrade this file to a Singleton Class or lmdb_store_env as a static
 * member variable of a normal class. Then data type specific APIs can be segregated
 * to a derived class and this class holding pristine get/set/delete APIs only.
 */
/* Lightning database environment used to store data */
static MDB_env* lmdb_store_env;

class SafeTransaction {
public:
    MDB_txn* txn = NULL;

    SafeTransaction(unsigned int flags) {
        int ret = mdb_txn_begin(lmdb_store_env, NULL, flags, &txn);
        if (ret != MDB_SUCCESS) {
            // SAFE_LOG(TCF_LOG_ERROR, "Failed to initialize LMDB transaction; %d", ret);
            txn = NULL;
        }
    }

    ~SafeTransaction(void) {
        if (txn != NULL)
            mdb_txn_commit(txn);
    }
};

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t lmdb_store::db_store_init(const std::string& db_path, const size_t map_size) {
    int ret;

    ret = mdb_env_create(&lmdb_store_env);
    db_error::ThrowIf<db_error::RuntimeError>(ret != 0, "Failed to create LMDB environment");
    ret=mdb_env_set_maxdbs(lmdb_store_env, MAX_DBS);
    db_error::ThrowIf<db_error::RuntimeError>(ret != 0, "Failed to set maximum database");
    ret = mdb_env_set_mapsize(lmdb_store_env, map_size);
    db_error::ThrowIf<db_error::RuntimeError>(ret != 0, "Failed to set LMDB default size");

    /*
     * MDB_NOSUBDIR avoids creating an additional directory for the database
     * MDB_WRITEMAP | MDB_NOMETASYNC should substantially improve LMDB's performance
     * This risks possibly losing at most the last transaction if the system crashes
     * before it is written to disk.
     */
    ret = mdb_env_open(lmdb_store_env, db_path.c_str(), MDB_NOSUBDIR | MDB_WRITEMAP | MDB_NOMETASYNC | MDB_MAPASYNC, 0664);
    if (ret != 0) {
        // SAFE_LOG(TCF_LOG_ERROR, "Failed to open LMDB database; %d", ret);
        return TCF_ERR_SYSTEM;
    }

    return TCF_SUCCESS;
}

void lmdb_store::db_store_close() {
    if (lmdb_store_env != NULL)
        mdb_env_close(lmdb_store_env);
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t db_store::db_store_get_value_size(
    const std::string& table,
    const uint8_t* inId,
    const size_t inIdSize,
    bool* outIsPresent,
    size_t* outValueSize) {
    MDB_dbi dbi;
    MDB_val lmdb_id;
    MDB_val lmdb_data;
    int ret;

#if DB_STORE_DEBUG
    {
        std::string idStr = BinaryToHexString(inId, inIdSize);
        // SAFE_LOG(TCF_LOG_DEBUG, "db_store_get_value_size: '%s'", idStr.c_str());
    }
#endif

    SafeThreadLock slock;      // lock by construction
    SafeTransaction stxn(MDB_RDONLY);

    if (stxn.txn == NULL) {
        return TCF_ERR_SYSTEM;
    }

    ret = mdb_dbi_open(stxn.txn, table.c_str(), 0, &dbi);
    if (ret == MDB_NOTFOUND) {
        // Set outIsPresent to false if database not found and return SUCCESS
        // for the db_store_get_value_size operation
        *outIsPresent = false;
        return TCF_SUCCESS;
    }
    else if (ret != 0) {
        // SAFE_LOG(TCF_LOG_ERROR, "Failed to open LMDB transaction : %d", ret);
        *outIsPresent = false;
        return TCF_ERR_SYSTEM;
    }

    lmdb_id.mv_size = inIdSize;
    lmdb_id.mv_data = (void*)inId;

    ret = mdb_get(stxn.txn, dbi, &lmdb_id, &lmdb_data);
    if (ret == MDB_NOTFOUND) {
        *outIsPresent = false;
        return TCF_SUCCESS;
    }
    else if (ret != 0) {
        // SAFE_LOG(TCF_LOG_ERROR, "Failed to get from LMDB database : %d", ret);
        *outIsPresent = false;
        return TCF_ERR_SYSTEM;
    }
    *outIsPresent = true;
    *outValueSize = lmdb_data.mv_size;

#if DB_STORE_DEBUG
    {
        std::string idStr = BinaryToHexString(inId, inIdSize);
        std::string valueStr = BinaryToHexString((uint8_t*)lmdb_data.mv_data, lmdb_data.mv_size);
        // SAFE_LOG(TCF_LOG_DEBUG, "db store found id: '%s' -> '%s'", idStr.c_str(), valueStr.c_str());
    }
#endif

    return TCF_SUCCESS;
}


// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t db_store::db_store_get(
    const std::string& table,
    const uint8_t* inId,
    const size_t inIdSize,
    uint8_t* outValue,
    const size_t inValueSize) {
    MDB_dbi dbi;
    MDB_val lmdb_id;
    MDB_val lmdb_data;
    int ret;

#if DB_STORE_DEBUG
    {
        std::string idStr = BinaryToHexString(inId, inIdSize);
        // SAFE_LOG(TCF_LOG_DEBUG, "db_store_get: '%s'", idStr.c_str());
    }
#endif

    SafeThreadLock slock;
    SafeTransaction stxn(MDB_RDONLY);

    if (stxn.txn == NULL)
        return TCF_ERR_SYSTEM;

    ret = mdb_dbi_open(stxn.txn, table.c_str(), 0, &dbi);
    if (ret != 0) {
        // SAFE_LOG(TCF_LOG_ERROR, "Failed to open LMDB transaction : %d", ret);
        return TCF_ERR_SYSTEM;
    }

    lmdb_id.mv_size = inIdSize;
    lmdb_id.mv_data = (void*)inId;

    ret = mdb_get(stxn.txn, dbi, &lmdb_id, &lmdb_data);
    if (ret == MDB_NOTFOUND) {
        // SAFE_LOG(TCF_LOG_ERROR, "Failed to find id in db store");
        return TCF_ERR_VALUE;
    }
    else if (ret != 0) {
        // SAFE_LOG(TCF_LOG_ERROR, "Failed to get from LMDB database : %d", ret);
        return TCF_ERR_SYSTEM;
    }
    else if (inValueSize != lmdb_data.mv_size) {
        // SAFE_LOG(TCF_LOG_ERROR, "Requested db of size %zu but buffer size is %zu", inValueSize,
        //    lmdb_data.mv_size);
        return TCF_ERR_VALUE;
    }
    memcpy_s(outValue, inValueSize, lmdb_data.mv_data, lmdb_data.mv_size);

#if DB_STORE_DEBUG
    {
        std::string idStr = BinaryToHexString(inId, inIdSize);
        std::string valueStr = BinaryToHexString((uint8_t*)lmdb_data.mv_data, lmdb_data.mv_size);
        // SAFE_LOG(TCF_LOG_DEBUG, "db store found id: '%s' -> '%s'", idStr.c_str(), valueStr.c_str());
    }
#endif

    return TCF_SUCCESS;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t db_store::db_store_put(
    const std::string& table,
    const uint8_t* inId,
    const size_t inIdSize,
    const uint8_t* inValue,
    const size_t inValueSize) {
    MDB_dbi dbi;
    MDB_val lmdb_id;
    MDB_val lmdb_data;
    int ret;

#if DB_STORE_DEBUG
   {
        std::string idStr = BinaryToHexString(inId, inIdSize);
        std::string valueStr = BinaryToHexString(inValue, inValueSize);
        // SAFE_LOG(TCF_LOG_DEBUG, "db store Put: %zu bytes '%s' -> %zu bytes '%s'", inIdSize,
        //   idStr.c_str(), inValueSize, valueStr.c_str());
   }
#endif

    SafeThreadLock slock;
    SafeTransaction stxn(0);

    if (stxn.txn == NULL)
        return TCF_ERR_SYSTEM;

    ret = mdb_dbi_open(stxn.txn, table.c_str(), MDB_CREATE, &dbi);
    if (ret != 0) {
        // SAFE_LOG(TCF_LOG_ERROR, "Failed to open LMDB transaction : %d", ret);
        return TCF_ERR_SYSTEM;
    }

    lmdb_id.mv_size = inIdSize;
    lmdb_id.mv_data = (void*)inId;
    lmdb_data.mv_size = inValueSize;
    lmdb_data.mv_data = (void*)inValue;

    ret = mdb_put(stxn.txn, dbi, &lmdb_id, &lmdb_data, 0);
    if (ret != 0) {
        // SAFE_LOG(TCF_LOG_ERROR, "Failed to put to LMDB database : %d", ret);
        return TCF_ERR_SYSTEM;
    }

    return TCF_SUCCESS;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t db_store::db_store_del(
    const std::string& table,
    const uint8_t* inId,
    const size_t inIdSize,
    const uint8_t* inValue,
    const size_t inValueSize) {
    MDB_dbi dbi;
    MDB_val lmdb_id;
    MDB_val lmdb_data;
    int ret;

#if DB_STORE_DEBUG
   {
        std::string idStr = BinaryToHexString(inId, inIdSize);
        // SAFE_LOG(TCF_LOG_DEBUG, "db store Del: %zu bytes '%s' -> %zu bytes '%s'", inIdSize,
        //   idStr.c_str(), inValueSize, valueStr.c_str());
   }
#endif

    SafeThreadLock slock;
    SafeTransaction stxn(0);

    if (stxn.txn == NULL)
        return TCF_ERR_SYSTEM;

    ret = mdb_dbi_open(stxn.txn, table.c_str(), MDB_CREATE, &dbi);
    if (ret != 0) {
        // SAFE_LOG(TCF_LOG_ERROR, "Failed to open LMDB transaction : %d", ret);
        return TCF_ERR_SYSTEM;
    }

    lmdb_id.mv_size = inIdSize;
    lmdb_id.mv_data = (void*)inId;
    lmdb_data.mv_size = inValueSize;
    lmdb_data.mv_data = (void*)inValue;

    ret = mdb_del(stxn.txn, dbi, &lmdb_id, &lmdb_data);
    if (ret != 0) {
        // SAFE_LOG(TCF_LOG_ERROR, "Failed to delete from LMDB database : %d", ret);
        return TCF_ERR_SYSTEM;
    }

    return TCF_SUCCESS;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t db_store::db_store_get_value_size(
    const std::string& table,
    const ByteArray& inId,
    bool* outIsPresent,
    size_t* outValueSize) {
    return db_store_get_value_size(table, inId.data(), inId.size(), outIsPresent, outValueSize);
}


// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t db_store::db_store_get(
    const std::string& table,
    const ByteArray& inId,
    ByteArray& outValue) {
    tcf_err_t result = TCF_SUCCESS;

    // Get all keys
    if (inId.size()==0) {
        std::string keys_result;
        keys_result = db_store_get_all(table, inId.data(), inId.size());
        if (keys_result.size() == 0)
        {
            return TCF_ERR_VALUE;
        }

        outValue.resize(keys_result.size());
        memcpy_s(outValue.data(), keys_result.size(), keys_result.c_str(), keys_result.size());
        result=TCF_SUCCESS;
        return result;

    }
    bool isPresent;
    size_t value_size;

    result = db_store_get_value_size(table, inId.data(), inId.size(), &isPresent, &value_size);
    if (result != TCF_SUCCESS) {
        return result;
    }
    if (!isPresent) {
        return TCF_ERR_VALUE;
    }

    // Resize the output array
    outValue.resize(value_size);

    // Fetch the state from the db storage
    result = db_store_get(table, inId.data(), inId.size(), &outValue[0], value_size);
    if (result != TCF_SUCCESS) {
        return result;
    }
    return result;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t db_store::db_store_put(
    const std::string& table,
    const ByteArray& inId,
    const ByteArray& inValue) {
    return db_store_put(table, inId.data(), inId.size(), inValue.data(), inValue.size());
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t db_store::db_store_del(
    const std::string& table,
    const ByteArray& inId,
    const ByteArray& inValue) {
    return db_store_del(table, inId.data(), inId.size(), inValue.data(), inValue.size());
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t db_store::db_store_csv_extend(
    const std::string& table,
    const ByteArray& inId,
    const ByteArray& inValue,
    const bool isPrepend){

    SafeUpdateLock ulock;

    tcf_err_t result = TCF_SUCCESS;
    bool isPresent;
    size_t value_size;

    result = db_store_get_value_size(table, inId.data(), inId.size(), &isPresent, &value_size);
    if (result != TCF_SUCCESS) return result;

    // If key not present, simply add the new key->value pair
    if (!isPresent) {
        return db_store_put(table, inId.data(), inId.size(), inValue.data(), inValue.size());
    }

    ByteArray valueBuffer;
    // Resize the valueBuffer to current value size
    valueBuffer.resize(value_size);

    // Fetch the state from the db storage
    result = db_store_get(table, inId.data(), inId.size(), &valueBuffer[0], value_size);
    if (result != TCF_SUCCESS) {
        return result;
    }

    if(isPrepend){
        ByteArray temp;
        // Insert the value to pe prepended. Then append a ',' to the
        // buffer and then append the existing value.
        temp.insert(temp.begin(),inValue.begin(), inValue.end());
        temp.emplace_back(',');
        temp.insert(temp.begin()+inValue.size()+1, valueBuffer.begin(), valueBuffer.end());
        valueBuffer = temp;
    }
    else {
        // Append a ',' to the end and then append the new value.
        valueBuffer.emplace_back(',');
        valueBuffer.insert(valueBuffer.end(), inValue.begin(), inValue.end());
    }

    return db_store_put(table, inId.data(), inId.size(), valueBuffer.data(), valueBuffer.size());
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t db_store::db_store_csv_pop(
    const std::string& table,
    const ByteArray& inId,
    ByteArray& outValue,
    const bool isMatch){

    SafeUpdateLock ulock;

    tcf_err_t result = TCF_SUCCESS;
    bool isPresent;
    size_t value_size;

    result = db_store_get_value_size(table, inId.data(), inId.size(), &isPresent, &value_size);
    if (result != TCF_SUCCESS) return result;

    // If key not present, return Error
    if (!isPresent) {
        // SAFE_LOG(TCF_LOG_ERROR, "Failed to find key in LMDB database");
        return TCF_ERR_VALUE;
    }

    ByteArray valueBuffer;
    // Resize the valueBuffer to current value size
    valueBuffer.resize(value_size);

    // Fetch the value from the db storage
    result = db_store_get(table, inId.data(), inId.size(), &valueBuffer[0], value_size);
    if (result != TCF_SUCCESS) {
        // SAFE_LOG(TCF_LOG_ERROR, "Failed to get from LMDB database : %d", result);
        return result;
    }

    bool isLast = true;
    ByteArray first_value;
    // Loop over valueBuffer byte by byte and append to first_value till a ',' is
    // encountered. Effectively parse the 1st string from the comma separated value.
    for (auto itr : valueBuffer){
        if(itr == ',') {
            isLast = false;
            break;
        }
        first_value.emplace_back(itr);
    }

    // If matching is required and there isn't a match, nothing needs to be done.
    // Return an error indicating failure in match.
    if(isMatch && outValue != first_value){
        return TCF_ERR_SYSTEM;
    }

    // If this is the only value, return value and delete key->value from db storage
    if(isLast){
        outValue = valueBuffer;
        return db_store_del(table, inId.data(), inId.size(), valueBuffer.data(), valueBuffer.size());
    }

    outValue = first_value;
    // valueBuffer which holds the current value in the store now needs to be truncated from
    // the beginning, removing the first value in the csv. Then it is persisted back into the
    // store to hold the rest of the comma-separated values.
    valueBuffer.erase(valueBuffer.begin(), valueBuffer.begin()+outValue.size()+1);
    return db_store_put(table, inId.data(), inId.size(), valueBuffer.data(), valueBuffer.size());
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t db_store::db_store_csv_search_delete(
    const std::string& table,
    const ByteArray& inId,
    const ByteArray& inValue){

    SafeUpdateLock ulock;

    tcf_err_t result = TCF_SUCCESS;
    bool isPresent;
    size_t value_size;

    result = db_store_get_value_size(table, inId.data(), inId.size(), &isPresent, &value_size);
    if (result != TCF_SUCCESS) return result;

    // If key not present, return Error
    if (!isPresent) {
        // SAFE_LOG(TCF_LOG_ERROR, "Failed to find key in LMDB database");
        return TCF_ERR_VALUE;
    }

    ByteArray valueBuffer;
    // Resize the valueBuffer to current value size
    valueBuffer.resize(value_size);

    // Fetch the value from the db storage
    result = db_store_get(table, inId.data(), inId.size(), &valueBuffer[0], value_size);
    if (result != TCF_SUCCESS) {
        // SAFE_LOG(TCF_LOG_ERROR, "Failed to get from LMDB database : %d", result);
        return result;
    }

    bool found = false;
    // Iterate over the stored comma separated values and match them with the value passed
    // in. If a match is found, it needs to be deleted and then the updated csv stored back.
    for(auto itr = valueBuffer.begin(); itr < valueBuffer.end(); itr += inValue.size() + 1){
        if( std::equal(itr, itr+inValue.size() , inValue.begin())){

            // If the value is anywhere in the csv except last, remove value and following ','
            if ((itr+inValue.size()) < valueBuffer.end())
                valueBuffer.erase(itr, itr+inValue.size()+1);
            // Else if the value is not the only one implying it is last, remove value and preceeding ','
            else if (inValue.size() < valueBuffer.size())
                valueBuffer.erase(itr-1, itr+inValue.size());
            // Else if the value is the only one in the csv
            else if (inValue.size() == valueBuffer.size())
                valueBuffer.erase(itr, itr+inValue.size());
            
            found = true;
            break;
        }
    }

    if(!found){
        return TCF_ERR_VALUE;
    }

    // If this was the only value, delete key->value from db storage
    if(valueBuffer.size() == 0){
        return db_store_del(table, inId.data(), inId.size(), valueBuffer.data(), valueBuffer.size());
    }
    // Restore updated csv to database
    return db_store_put(table, inId.data(), inId.size(), valueBuffer.data(), valueBuffer.size());
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
std::string db_store::db_store_get_all(
    const std::string& table,
    const uint8_t* inId,
    const size_t inIdSize) {
    MDB_dbi dbi;
    MDB_val lmdb_id;
    MDB_val lmdb_data;
    int ret;
    std::string table_keys;

#if DB_STORE_DEBUG
    {
        std::string idStr = BinaryToHexString(inId, inIdSize);
        // SAFE_LOG(TCF_LOG_DEBUG, "db_store_get: '%s'", idStr.c_str());
    }
#endif

    SafeThreadLock slock;
    SafeTransaction stxn(MDB_RDONLY);

    if (stxn.txn == NULL) {
        // return TCF_ERR_SYSTEM;
        return table_keys;
    }
    ret = mdb_dbi_open(stxn.txn, table.c_str(), 0, &dbi);
    if (ret != 0) {
        // SAFE_LOG(TCF_LOG_ERROR, "Failed to open LMDB transaction : %d", ret);
        return table_keys;
    }

    MDB_cursor *cursor;
    ret= mdb_cursor_open(stxn.txn, dbi, &cursor);
    if (ret != 0) {
        // SAFE_LOG(TCF_LOG_ERROR, "Failed to get from LMDB database : %d", ret);
        return table_keys;
    }
    ret = mdb_cursor_get(cursor, &lmdb_id, &lmdb_data, MDB_FIRST);
    if (ret != 0) {
        // SAFE_LOG(TCF_LOG_ERROR, "Failed to get from LMDB database : %d", ret);
        return table_keys;
    }
    std::string temp_str;
    int size_key;
    do {
        temp_str=(char*)lmdb_id.mv_data;
        size_key=lmdb_id.mv_size;
        std::string temp_substr = temp_str.substr (0,size_key);
        table_keys.append(temp_substr);
        table_keys.append(",");
    } while ( mdb_cursor_get(cursor, &lmdb_id, &lmdb_data, MDB_NEXT) == 0);

    table_keys.pop_back();

#if DB_STORE_DEBUG
    {
        std::string idStr = BinaryToHexString(inId, inIdSize);
        std::string valueStr = BinaryToHexString((uint8_t*)lmdb_data.mv_data, lmdb_data.mv_size);
        // SAFE_LOG(TCF_LOG_DEBUG, "db store found id: '%s' -> '%s'", idStr.c_str(), valueStr.c_str());
    }
#endif

    return table_keys;
}

