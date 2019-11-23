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

from service_client.generic import TextServiceClient
# add the dot prefix to address the ModuleNotFoundError error
from .string_escape import escape, unescape
import logging

logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------


class LMDBHelperProxy:
    """
    LMDBHelperProxy passes commands serialized as strings
    to the LMDB remote listener.
    """

    def __init__(self, uri):
        self.set_remote_uri(uri)

    def set_remote_uri(self, uri):
        self.__uri_client = TextServiceClient(uri)

# ------------------------------------------------------------------------------
    # Requests are serialized as: <cmd>\n<arg1>\n<arg2>...

    def set(self, table, key, value):
        """
        Function to set a key-value pair in a lmdb table
        Parameters:
           - table is the name of lmdb table in which
             the key-value pair needs to be inserted.
           - key is the primary key of the table.
           - value is the value that needs to be inserted in the table.
        """
        # Set, table, key, value
        request = "S\n" + escape(table) + "\n" + escape(key) + \
            "\n" + escape(value)
        response = self.__uri_client._postmsg(request).decode("utf-8")
        args = response.split("\n")
        # Set successful (returned True)
        if args[0] == "t" and len(args) == 1:
            return True
        # Set unsuccessful (returned False)
        elif args[0] == "f" and len(args) == 1:
            return False
        # Error
        elif args[0] == "e":
            if len(args) != 2:
                logger.error("Unknown error format")
            else:
                logger.error("Request error: %s", args[1])
        else:
            logger.error("Unknown response format")

# ------------------------------------------------------------------------------
    def get(self, table, key):
        """
        Function to get the value for a key in a lmdb table
        Parameters:
           - table is the name of lmdb table from which
             the key-value pair needs to be retrieved.
           - key is the primary key of the table.
        """
        # Get, table, key
        request = "G\n" + escape(table) + "\n" + escape(key)
        response = self.__uri_client._postmsg(request).decode("utf-8")
        args = response.split("\n")
        # Value found
        if args[0] == "v" and len(args) == 2:
            return unescape(args[1])
        # Value not found
        elif args[0] == "n" and len(args) == 1:
            return None
        # Error
        elif args[0] == "e":
            if len(args) != 2:
                logger.error("Unknown error format")
            else:
                logger.error("Request error: %s", args[1])
        else:
            logger.error("Unknown response format")

# ------------------------------------------------------------------------------
    def remove(self, table, key, value=None):
        """
        Function to remove the value for a key in a lmdb table
        Parameters:
           - table is the name of lmdb table in which
             the key-value pair need to be removed.
           - key is the primary key of the table.
           - value is data to be removed, If the database does not support
             sorted duplicate data items (MDB_DUPSORT) the data parameter
             is ignored. If the database supports sorted duplicates and
             the data parameter is NULL, all of the duplicate data items
             for the key will be deleted. Otherwise, if the data parameter is
             non-NULL only the matching data item will be deleted.
        """
        # Remove, table, key
        request = "R\n" + escape(table) + "\n" + escape(key)
        if value is not None:
            request = "\n" + request + value.replace("\n", "\\n")
        response = self.__uri_client._postmsg(request).decode("utf-8")
        args = response.split("\n")
        # Remove successful (returned True)
        if args[0] == "t" and len(args) == 1:
            return True
        # Remove unsuccessful (returned False)
        elif args[0] == "f" and len(args) == 1:
            return False
        # Error
        elif args[0] == "e":
            if len(args) != 2:
                logger.error("Unknown error format")
            else:
                logger.error("Request error: %s", args[1])
        else:
            logger.error("Unknown response format")

# ------------------------------------------------------------------------------
    def lookup(self, table):
        """
        Function to get all the keys in a lmdb table
        Parameters:
           - table is the name of the lmdb table.
        """
        result = []
        # Lookup, table
        request = "L\n" + escape(table)
        response = self.__uri_client._postmsg(request).decode("utf-8")
        args = response.split("\n")
        # Lookup result found
        if args[0] == "l":
            if len(args) == 2:
                # Result is a list of keys separated by commas
                result = unescape(args[1]).split(",")
            else:
                logger.error("Unknown response format")
        # Lookup result not found
        elif args[0] == "n" and len(args) == 1:
            return result
        # Error
        elif args[0] == "e":
            if len(args) != 2:
                logger.error("Unknown error format")
            else:
                logger.error("Request error: %s", args[1])
        else:
            logger.error("Unknown response format")
        return result
