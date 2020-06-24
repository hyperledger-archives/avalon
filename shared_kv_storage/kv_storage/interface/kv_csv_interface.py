# Copyright 2020 Intel Corporation
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


class KvCsvStorage(ABC):
    """KvCsvStorage interface provides APIs to manipulate values
       stored as csv in KV Storage."""

    @abstractmethod
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
        pass

# ---------------------------------------------------------------------------------------------------
    @abstractmethod
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
        pass

# ---------------------------------------------------------------------------------------------------
    @abstractmethod
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
        pass

# ---------------------------------------------------------------------------------------------------
    @abstractmethod
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
        pass

# ---------------------------------------------------------------------------------------------------
    @abstractmethod
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
        pass
