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
from abc import ABC, abstractmethod


class KvStorage(ABC):
    """KvStorage interface provides APIs to access key value store."""
    @abstractmethod
    def open(self, lmdb_file, map_size="1 TB"):
        """
        Function to open the database file
        Parameters:
           - lmdb_file is the name and location of lmdb database file
           - map_size is the maximum size of the database, it must be a
             multiple of the page size (4096)
             and defaults to large max size (1 TB)
        """
        pass

# ---------------------------------------------------------------------------------------------------
    @abstractmethod
    def close(self):
        """Function to close the database file."""
        pass

# ---------------------------------------------------------------------------------------------------
    @abstractmethod
    def set(self, table, key, value):
        """
        Function to set a key-value pair in a lmdb table
        Parameters:
           - table is the name of lmdb table in which key-value pair
             need to be inserted.
           - key is the primary key of the table.
           - value is the value that needs to be inserted in the table.
        """
        pass

# ---------------------------------------------------------------------------------------------------
    @abstractmethod
    def get(self, table, key):
        """
        Function to get the value for a key in a lmdb table
        Parameters:
           - table is the name of lmdb table in which key-value pair
             need to be retrieved.
           - key is the primary key of the table.
        """
        pass

# ---------------------------------------------------------------------------------------------------
    @abstractmethod
    def remove(self, table, key, value=None):
        """
        Function to remove the key/value from a lmdb table
        Parameters:
           - table is the name of lmdb table in which key-value pair need
             to be removed.
           - key is the primary key of the table.
           - value is data to be removed, If the database does not support
             sorted duplicate data items (MDB_DUPSORT) the data parameter
             is ignored. If the database supports sorted duplicates and the
             data parameter is NULL, all of the duplicate data items for the
             key will be deleted. Otherwise, if the data parameter is
             non-NULL only the matching data item will be deleted.
        """
        pass

# ---------------------------------------------------------------------------------------------------
    @abstractmethod
    def lookup(self, table):
        """
        Function to get all the keys in a lmdb table
        Parameters:
           - table is the name of lmdb table.
        """
        pass
# ---------------------------------------------------------------------------------------------------

    def human_read_to_byte(self, size):
        """Convert human readable memory size to byte."""
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        size = size.split()  # divide '1 GB' into ['1', 'GB']
        if len(size) != 2 or int(size[0]) <= 0:
            raise ValueError("Invalid data format")
        num, unit = int(size[0]), size[1].upper()
        try:
            idx = size_name.index(unit)
        except ValueError:
            raise ValueError("Invalid size")
        factor = 1024 ** idx
        return num * factor
