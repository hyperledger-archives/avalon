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

namespace lmdb_store {
    /**
     * Initialize the database store - must be called before performing gets/puts
     * Primary expected use: python / untrusted side
     *
     * @param db_path
     *   The path to the LMDB (lightning memory mapped database) which provides
     *   the back-end to this database store implementation
     *
     * @param map_size
     *   The maximum size of the database
     *
     * @return
     *  Success (return TCF_SUCCESS) - database store ready to use
     *  Failure (return nonzero) - database store is unusable
     */
    tcf_err_t db_store_init(const std::string& db_path, const size_t map_size);

    /**
     * Close the database store and flush the data to disk
     */
    void db_store_close();
}  /* namespace lmdb_store */


