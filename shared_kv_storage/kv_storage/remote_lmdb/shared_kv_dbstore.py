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

"""
This file implements a simple Avalon LMDB wrapper for using multiple tables in
a LMDB database.

The method put stores key and value to the table. The method get will
retrieve the value of the key. Lookup method will retrieve all the keys
of the provided table name.
"""

import json
import logging

import kv_storage.remote_lmdb.db_store_csv as db_store_csv
from kv_storage.interface.shared_kv_interface import KvStorage
from kv_storage.interface.kv_csv_interface import KvCsvStorage

logger = logging.getLogger(__name__)
lookup_flag = False

# ---------------------------------------------------------------------------------------------------


class KvDBStore(KvStorage, KvCsvStorage):
    """KvStorage interface maintains information about registries supported by
    the TCS in direct model."""

    def __init__(self):
        self._db_store = db_store_csv.DbStoreCsv()

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
            ret = self._db_store.db_store_init(lmdb_file, map_size)
            return True
        except Exception as err:
            logger.error("Exception reading KV Storage Size: %s \n %s", str(
                err), type(lmdb_file))
            return False

# ---------------------------------------------------------------------------------------------------
    def close(self):
        """Function to close the database file."""
        self._db_store.db_store_close()

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
            self._db_store.db_store_put(table, key, value)
            return True
        except Exception:
            # @TODO : Instead of suppressing exception here, pass it back
            # and let the caller decide how to react to the exception.
            logger.debug("Could not set key-value in database.")
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
                value = self._db_store.db_store_get(table, key)
            else:
                value = None
        except Exception:
            # @TODO : Instead of suppressing exception here, pass it back
            # and let the caller decide how to react to the exception.
            logger.debug("Could not retrieve value from database.")
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
                self._db_store.db_store_del(table, key, "")
            else:
                self._db_store.db_store_del(table, key, value)
            return True
        except Exception:
            # @TODO : Instead of suppressing exception here, pass it back
            # and let the caller decide how to react to the exception.
            logger.debug("Could not delete key-value from database.")
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
            table_keys = self._db_store.db_store_get(table, "")
            lookup_flag = False
            table_keys = table_keys.split(",")
            for i in table_keys:
                result.append(i)
        except Exception:
            # @TODO : Instead of suppressing exception here, pass it back
            # and let the caller decide how to react to the exception.
            logger.debug("Could not lookup keys in database.")
            result = []

        return result
# ---------------------------------------------------------------------------------------------------

    def csv_append(self, table, key, value):
        """
        Function to update a key-value pair in a lmdb table that holds
        comma-separated strings as value. This function adds a string
        to the end of the comma-separated value.

        Parameters:
           @param table - Name of the lmdb table in which key-value pair
                          needs to be updated.
           @param key - The primary key of the table.
           @param value - The value that needs to be appended to the existing
                          value(comma-separated) corresponding to the key.
        """
        try:
            self._db_store.db_store_csv_append(table, key, value)
            return True
        except Exception:
            # @TODO : Instead of suppressing exception here, pass it back
            # and let the caller decide how to react to the exception.
            logger.debug("Could not append value to csv in database.")
            return False

# ---------------------------------------------------------------------------------------------------
    def csv_prepend(self, table, key, value):
        """
        Function to update a key-value pair in a lmdb table that holds
        comma-separated strings as value. This function adds a string
        to the beginning of the comma-separated value.

        Parameters:
           @param table - Name of the lmdb table in which key-value pair
                          needs to be updated.
           @param key - The primary key of the table.
           @param value - The value that needs to be prepended to the existing
                          value(comma-separated) corresponding to the key.
        """
        try:
            self._db_store.db_store_csv_prepend(table, key, value)
            return True
        except Exception:
            # @TODO : Instead of suppressing exception here, pass it back
            # and let the caller decide how to react to the exception.
            logger.debug("Could not prepend value to csv in database.")
            return False

# ---------------------------------------------------------------------------------------------------
    def csv_pop(self, table, key):
        """
        Function to update a key-value pair in a lmdb table that holds
        comma-separated strings as value. This function retrieves a string
        from the beginning of the comma-separated value. It also deletes
        the string from the value and if this is the lone string, the key-
        value pair is removed.

        Parameters:
           @param table - Name of the lmdb table from which key-value pair
                          needs to be read and updated.
           @param key - The primary key of the table.
        Returns:
           @returns value - First element from comma-separated value for key
                            passed in.
        """
        try:
            if key != "":
                value = self._db_store.db_store_csv_pop(table, key)
            else:
                value = None
        except Exception:
            # @TODO : Instead of suppressing exception here, pass it back
            # and let the caller decide how to react to the exception.
            logger.debug("Could not pop value from csv in database.")
            value = None

        if not value:
            value = None

        return value

# ---------------------------------------------------------------------------------------------------
    def csv_match_pop(self, table, key, value):
        """
        Function to conditionally update a key-value pair in a lmdb table
        that holds comma-separated strings as value. This function reads
        the first of comma-separated strings and then compares it with the
        value passed in. If there is a match, the passed value is returned.
        It also deletes the string from the value and if this is the lone
        string, the key-value pair altogether is removed.

        Parameters:
           @param table - Name of the lmdb table from which key-value pair
                          needs to be read and updated.
           @param key - The primary key of the table.
           @param value - Value to be compared against.
        Returns:
           @returns value - value if the first string of the comma-separated
                            strings matches. None, otherwise.
        """
        try:
            if key != "":
                value = self._db_store.db_store_csv_match_pop(
                    table, key, value)
            else:
                value = None
        except Exception:
            # @TODO : Instead of suppressing exception here, pass it back
            # and let the caller decide how to react to the exception.
            logger.debug("Could not match pop value from csv in database.")
            value = None
        if not value:
            value = None

        return value

# ---------------------------------------------------------------------------------------------------

    def csv_search_delete(self, table, key, value):
        """
        Function to conditionally update a key-value pair in a lmdb table
        that holds comma-separated strings as value. This function reads
        each of the comma-separated strings and then compares it with the
        value passed in. If there is a match, the passed value is deleted.
        If this is the lone string, the key-value pair altogether is removed.

        Parameters:
           @param table - Name of the lmdb table from which key-value pair
                          needs to be read and updated.
           @param key - The primary key of the table.
           @param value - Value to be compared against and deleted.
        """
        try:
            value = self._db_store.db_store_csv_search_delete(
                table, key, value)
            return True
        except Exception:
            # @TODO : Instead of suppressing exception here, pass it back
            # and let the caller decide how to react to the exception.
            logger.debug("Could not search/delete value from csv in database.")
            return False

# ---------------------------------------------------------------------------------------------------
