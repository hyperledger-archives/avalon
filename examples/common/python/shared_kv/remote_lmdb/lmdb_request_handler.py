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

import os
import urllib.request
import urllib.error
from twisted.web import resource, http
from twisted.web.error import Error
import tcf_enclave_manager.tcf_enclave as db_store
from error_code.error_status import WorkorderError
from string_escape import escape, unescape

import logging
logger = logging.getLogger(__name__)

TCFHOME = os.environ.get("TCF_HOME", "../../../../")
lookup_flag = False

class LMDBRequestHandler(resource.Resource):
    """
    LMDBRequestHandler is comprised of HTTP interface which 
    listens for calls to LMDB
    """
    # The isLeaf instance variable describes whether or not 
    # a resource will have children and only leaf resources get rendered.
    # TCSListener is the most derived class hence isLeaf is required.

    isLeaf = True

    ## -----------------------------------------------------------------
    def __init__(self, config):

        if config.get('KvStorage') is None:
            logger.error("Kv Storage path is missing")
            sys.exit(-1)

        storage_path = TCFHOME + '/' + config['KvStorage']['StoragePath']
        if not self.open(storage_path):
            logger.error("Failed to open KV Storage DB")
            sys.exit(-1)

    def __del__(self):
       self.close()

    def _process_request(self, request):
        response = ""
        logger.info(request.encode('utf-8'))
        args = request.split('\n')
        for i in range(len(args)):
            args[i] = unescape(args[i])
        logger.info(args)
        cmd = args[0]

        #Lookup
        if (cmd=="L"):
            if len(args) == 2:
                result = self.lookup(args[1])
                if result != "":
                    response = "l\n" + escape(result)
                else:
                    response = "n"
            else:
                logger.error("Invalid args for cmd Lookup")
                response = "e\nInvalid args for cmd Lookup"

        #Get
        elif (cmd=="G"):
            if len(args) == 3:
                result = self.get(args[1], args[2])
                if result is not None:
                    response = "v\n" + escape(result)
                else:
                    response = "n"
            else:
                logger.error("Invalid args for cmd Get")
                response = "e\nInvalid args for cmd Get"   

        #Set
        elif (cmd=="S"):
            if len(args) == 4:
                result = self.set(args[1], args[2], args[3])
                if result:
                    response = "t"
                else:
                    response = "f" 
            else:
                logger.error("Invalid args for cmd Set")
                response = "e\nInvalid args for cmd Set"  

        #Remove
        elif (cmd=="R"):
            if len(args) == 3 or len(args) == 4:
                if len(args) == 3:
                    result = self.remove(args[1], args[2])
                else:
                    result = self.remove(args[1], args[2], value=args[3])
                if result:
                    response = "t"
                else:
                    response = "f"
            else:
                logger.error("Invalid args for cmd Remove")
                response = "e\nInvalid args for cmd Remove"  

        else:
            logger.error("Unknown cmd")
            response = "e\nUnknown cmd"
        return response

    def render_GET(self, request):
        response = 'Only POST request is supported'
        logger.error("GET request is not supported." + \
            " Only POST request is supported")
        
        return response

    def render_POST(self, request):
        response = ""
       
        logger.info('Received a new request from the client')

        try :
            # Process the message encoding
            encoding = request.getHeader('Content-Type')
            data = request.content.read().decode('utf-8')

            if encoding == 'text/plain; charset=utf-8' :
                response = self._process_request(data)
            else :
                response = 'UNKNOWN_ERROR: unknown message encoding'
                return response

        except :
            logger.exception('exception while decoding http request %s', 
                request.path)
            response = 'UNKNOWN_ERROR: unable to decode incoming request '
            return response

        # Send back the results
        try :
            logger.info('response[%s]: %s', encoding, response.encode('utf-8'))
            request.setHeader('content-type', encoding)
            request.setResponseCode(http.OK)
            return response.encode('utf-8')

        except :
            logger.exception('unknown exception while processing request %s', 
                request.path)
            response = 'UNKNOWN_ERROR: unknown exception processing ' + \
                'http request {0}'.format(request.path)
            return response

#------------------------------------------------------------------------------

    def open(self, lmdb_file):
        """
        Function to open the database file
        Parameters:
           - lmdb_file is the name and location of lmdb database file
        """
        db_store.db_store_init(lmdb_file)
        return True

#------------------------------------------------------------------------------
    def close(self):
        """
        Function to close the database file
        """
        db_store.db_store_close()

#------------------------------------------------------------------------------
    def set(self, table, key, value):
        """
        Function to set a key-value pair in a lmdb table 
        Parameters:
           - table is the name of lmdb table in which 
             the key-value pair needs to be inserted.
           - key is the primary key of the table.
           - value is the value that needs to be inserted in the table.
        """
        try:
            db_store.db_store_put(table,key,value)
            return True
        except:
            return False

#------------------------------------------------------------------------------
    def get(self, table, key):
        """
        Function to get the value for a key in a lmdb table 
        Parameters:
           - table is the name of lmdb table from which
             the key-value pair needs to be retrieved.
           - key is the primary key of the table.
        """
        try:
            if key != "" or lookup_flag == True:
                value = db_store.db_store_get(table, key)
            else:
                value = None
        except:
            value = None

        if not value:
            value = None

        return value

#------------------------------------------------------------------------------
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
        try:
            if value is None:
                db_store.db_store_del(table, key, "")
            else:
                db_store.db_store_del(table, key, value)
            return True
        except:
            return False

#------------------------------------------------------------------------------
    def lookup(self, table):
        """
        Function to get all the keys in a lmdb table 
        Parameters:
           - table is the name of lmdb table.
        """
        try:
            lookup_flag = True
            result = db_store.db_store_get(table,"")
            lookup_flag = False
        except:
            result = ""
        return result
#------------------------------------------------------------------------------
