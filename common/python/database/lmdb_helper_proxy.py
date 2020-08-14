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

import logging
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------


class MessageException(Exception):
    """
    A class to capture communication exceptions when communicating with
    services
    """
    pass


class LMDBHelperProxy():
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
        request = "S\n" + self.__escape(table) + "\n" + self.__escape(key) + \
            "\n" + self.__escape(value)

        return self.__set_update(request)

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
        request = "G\n" + self.__escape(table) + "\n" + self.__escape(key)

        return self.__get_update(request)

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
        request = "R\n" + self.__escape(table) + "\n" + self.__escape(key)
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
        request = "L\n" + self.__escape(table)
        response = self.__uri_client._postmsg(request).decode("utf-8")
        args = response.split("\n")
        # Lookup result found
        if args[0] == "l":
            if len(args) == 2:
                # Result is a list of keys separated by commas
                result = self.__unescape(args[1]).split(",")
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

# ------------------------------------------------------------------------------
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
        # csv_append, table, key, value
        # CA corresponding to Csv Append
        request = "CA\n" + self.__escape(table) + "\n" + self.__escape(key) + \
            "\n" + self.__escape(value)

        return self.__set_update(request)

# ------------------------------------------------------------------------------
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
        # csv_prepend, table, key, value
        # CP corresponding to Csv Prepend
        request = "CP\n" + self.__escape(table) + "\n" + self.__escape(key) + \
            "\n" + self.__escape(value)

        return self.__set_update(request)

# ------------------------------------------------------------------------------
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
        # csv_pop, table, key
        # CR corresponding to Csv Pop where the 1st element from the csv is
        # retrieved and the rest left intact.
        request = "CR\n" + self.__escape(table) + "\n" + self.__escape(key)

        return self.__get_update(request)

# ------------------------------------------------------------------------------
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
        # csv_pop, table, key, value
        # CM corresponding to Csv match and pop where the 1st element from the
        # csv is conditionally(if matches) retrieved and the rest left intact.
        request = "CM\n" + self.__escape(table) + "\n" + self.__escape(key) + \
            "\n" + self.__escape(value)

        return self.__get_update(request)

# ------------------------------------------------------------------------------
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
        # csv_search_delete, table, key, value
        # CD corresponding to Csv Search Delete
        request = "CD\n" + self.__escape(table) + "\n" + self.__escape(key) + \
            "\n" + self.__escape(value)

        return self.__set_update(request)

# ------------------------------------------------------------------------------
    def __set_update(self, request):
        """
        Helper method to post request to remote uri and process
        response for set/update methods.

        Parameters:
            @param request - Prepared request string to send to remote uri
        Returns:
            @returns True - If operation is successful. False, otherwise.
        """
        response = self.__uri_client._postmsg(request).decode("utf-8")
        args = response.split("\n")
        # Set/Update successful (returned True)
        if args[0] == "t" and len(args) == 1:
            return True
        # Set/Update unsuccessful (returned False)
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
    def __get_update(self, request):
        """
        Helper method to post request to remote uri and process
        response for get/retrieve(get and remove) methods.

        Parameters:
            @param request - Prepared request string to send to remote uri
        Returns:
            @returns value - If operation is successful. None, otherwise.
        """
        response = self.__uri_client._postmsg(request).decode("utf-8")
        args = response.split("\n")
        # Value found
        if args[0] == "v" and len(args) == 2:
            return self.__unescape(args[1])
        # Value not found or could not be retrieved
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
    def __escape(self, string):
        return string.encode("unicode_escape").decode("utf-8")

# ------------------------------------------------------------------------------
    def __unescape(self, string):
        return string.encode("utf-8").decode("unicode_escape")


class TextServiceClient(object):
    """
    Class similar to HTTP client that handles UTF8 text instead
    of JSONs
    """

    def __init__(self, url):
        self.ServiceURL = url
        self.ProxyHandler = urllib.request.ProxyHandler({})

    def _postmsg(self, request):
        """
        Post a request UTF8 text listener and return the response.
        """

        data = request.encode('utf-8')
        datalen = len(data)

        url = self.ServiceURL

        logger.debug('post request to %s with DATALEN=%d, DATA=<%s>',
                     url, datalen, data)

        try:
            request = urllib.request.Request(
                url, data,
                {'Content-Type': 'text/plain; charset=utf-8',
                 'Content-Length': datalen})
            opener = urllib.request.build_opener(self.ProxyHandler)
            response = opener.open(request, timeout=10)

        except urllib.error.HTTPError as err:
            logger.warn('operation failed with response: %s', err.code)
            raise MessageException(
                'operation failed with response: {0}'.format(err.code))

        except urllib.error.URLError as err:
            logger.warn('operation failed: %s', err.reason)
            raise MessageException('operation failed: {0}'.format(err.reason))

        except Exception as err:
            logger.exception('no response from server: %s', str(err))
            raise MessageException('no response from server: {0}'.format(err))

        content = response.read()
        headers = response.info()
        response.close()

        encoding = headers.get('Content-Type')
        if encoding != 'text/plain; charset=utf-8':
            logger.info('server responds with message %s of type %s',
                        content, encoding)
            return None

        return content
