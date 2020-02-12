# Copyright 2019 Intel Corporation
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

"""This file implements a simple TCF LMDB wrapper for using multiple tables in
a lmdb database.

The method put stores key and value to the table. The method get will
retrieve the value of the key. Lookup method will retrieve all the keys
of the provided table name.
"""

import json
import logging

import kv_storage.remote_lmdb.db_store as db_store
from kv_storage.interface.shared_kv_interface import KvStorage

logger = logging.getLogger(__name__)
lookup_flag = False

# ---------------------------------------------------------------------------------------------------


class KvDBStore(KvStorage):
    """KvStorage interface maintains information about registries supported by
    the TCS in direct model."""

    def open(self, lmdb_file, map_size="1 TB"):
        """
        Function to open the database file
        Parameters:
           - lmdb_file is the name and location of lmdb database file
           - map_size is the maximum size of the database, it must be
             a multiple of the page size (4096)
             and default to an insanely large max size (1 TB)
        """
        try:
            map_size = self.human_read_to_byte(map_size)
            if map_size % 4096 != 0:
                logger.error(
                    "Invalid KV Storage Size, it must be a multiple \
                     of the page size (4096)")
                raise Exception("Invalid Map Storage Size")
            ret = db_store.db_store_init(lmdb_file, map_size)
            return True
        except Exception as err:
            logger.error("Exception reading KV Storage Size: %s \n %s", str(
                err), type(lmdb_file))
            return False

# ---------------------------------------------------------------------------------------------------
    def close(self):
        """Function to close the database file."""
        db_store.db_store_close()

# ---------------------------------------------------------------------------------------------------
    def set(self, table, key, value):
        """
        Function to set a key-value pair in a lmdb table
        Parameters:
           - table is the name of lmdb table in which key-value pair
             need to be inserted.
           - key is the primary key of the table.
           - value is the value that needs to be inserted in the table.
        """
        try:
            db_store.db_store_put(table, key, value)
            return True
        except Exception:
            return False

# ---------------------------------------------------------------------------------------------------
    def get(self, table, key):
        """
        Function to get the value for a key in a lmdb table
        Parameters:
           - table is the name of lmdb table in which key-value pair
             need to be retrieved.
           - key is the primary key of the table.
        """
        try:
            if key != "" or lookup_flag is True:
                value = db_store.db_store_get(table, key)
            else:
                value = None
        except Exception:
            value = None

        if not value:
            value = None

        return value

# ---------------------------------------------------------------------------------------------------
    def remove(self, table, key, value=None):
        """
        Function to remove the key/value from a lmdb table
        Parameters:
           - table is the name of lmdb table in which key-value pair need
             to be removed.
           - key is the primary key of the table.
           - value is data to be removed, If the database does not support
             sorted duplicate data items (MDB_DUPSORT) the data parameter is
             ignored. If the database supports sorted duplicates and the data
             parameter is NULL, all of the duplicate data items for the key
             will be deleted. Otherwise, if the data parameter is non-NULL
             only the matching data item will be deleted.
        """
        try:
            if value is None:
                db_store.db_store_del(table, key, "")
            else:
                db_store.db_store_del(table, key, value)
            return True
        except Exception:
            return False

# ---------------------------------------------------------------------------------------------------
    def lookup(self, table):
        """
        Function to get all the keys in a lmdb table
        Parameters:
           - table is the name of lmdb table.
        """
        result = []
        try:
            lookup_flag = True
            table_keys = db_store.db_store_get(table, "")
            lookup_flag = False
            table_keys = table_keys.split(",")
            for i in table_keys:
                result.append(i)
        except Exception:
            result = []

        return result
# ---------------------------------------------------------------------------------------------------
