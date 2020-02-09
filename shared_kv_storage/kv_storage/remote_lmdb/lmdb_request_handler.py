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

from os import sys, environ
from twisted.web import resource, http
from kv_storage.remote_lmdb.string_escape import escape, unescape
from kv_storage.remote_lmdb.shared_kv_dbstore import KvDBStore


import logging

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TCFHOME = environ.get("TCF_HOME", "../../../../")
lookup_flag = False


class LMDBRequestHandler(resource.Resource):
    """LMDBRequestHandler is comprised of HTTP interface which listens for
    calls to LMDB."""
    # The isLeaf instance variable describes whether or not
    # a resource will have children and only leaf resources get rendered.
    # LMDBRequestHandler is the most derived class hence isLeaf is required.

    isLeaf = True

    # -----------------------------------------------------------------
    def __init__(self, config):

        if config.get('KvStorage') is None:
            logger.error("Kv Storage path is missing")
            sys.exit(-1)

        self.kv_helper = KvDBStore()

        storage_path = TCFHOME + '/' + config['KvStorage']['StoragePath']
        storage_size = config['KvStorage']['StorageSize']
        if not self.kv_helper.open(storage_path, storage_size):
            logger.error("Failed to open KV Storage DB")
            sys.exit(-1)

    def __del__(self):
        self.kv_helper.close()

    def _process_request(self, request):
        response = ""
        logger.info(request.encode('utf-8'))
        args = request.split('\n')
        for i in range(len(args)):
            args[i] = unescape(args[i])
        logger.info(args)
        cmd = args[0]

        # Lookup
        if (cmd == "L"):
            if len(args) == 2:
                result_list = self.kv_helper.lookup(args[1])
                result = ""
                for key in result_list:
                    if result == "":
                        result = key
                    else:
                        result = result + "," + key
                # Lookup result found
                if result != "":
                    response = "l\n" + escape(result)
                # No result found
                else:
                    response = "n"
            # Error
            else:
                logger.error("Invalid args for cmd Lookup")
                response = "e\nInvalid args for cmd Lookup"

        # Get
        elif (cmd == "G"):
            if len(args) == 3:
                result = self.kv_helper.get(args[1], args[2])
                # Value found
                if result is not None:
                    response = "v\n" + escape(result)
                # Value not found
                else:
                    response = "n"
            # Error
            else:
                logger.error("Invalid args for cmd Get")
                response = "e\nInvalid args for cmd Get"

        # Set
        elif (cmd == "S"):
            if len(args) == 4:
                result = self.kv_helper.set(args[1], args[2], args[3])
                # Set successful (returned True)
                if result:
                    response = "t"
                # Set unsuccessful (returned False)
                else:
                    response = "f"
            # Error
            else:
                logger.error("Invalid args for cmd Set")
                response = "e\nInvalid args for cmd Set"

        # Remove
        elif (cmd == "R"):
            if len(args) == 3 or len(args) == 4:
                if len(args) == 3:
                    result = self.kv_helper.remove(args[1], args[2])
                else:
                    result = self.kv_helper.remove(
                        args[1], args[2], value=args[3])
                # Remove successful (returned True)
                if result:
                    response = "t"
                # Remove unsuccessful (returned False)
                else:
                    response = "f"
            # Error
            else:
                logger.error("Invalid args for cmd Remove")
                response = "e\nInvalid args for cmd Remove"
        # Error
        else:
            logger.error("Unknown cmd")
            response = "e\nUnknown cmd"
        return response

    def render_GET(self, request):
        response = 'Only POST request is supported'
        logger.error("GET request is not supported." +
                     " Only POST request is supported")

        return response

    def render_POST(self, request):
        response = ""

        logger.info('Received a new request from the client')

        try:
            # Process the message encoding
            encoding = request.getHeader('Content-Type')
            data = request.content.read().decode('utf-8')

            if encoding == 'text/plain; charset=utf-8':
                response = self._process_request(data)
            else:
                response = 'UNKNOWN_ERROR: unknown message encoding'
                return response

        except Exception:
            logger.exception('exception while decoding http request %s',
                             request.path)
            response = 'UNKNOWN_ERROR: unable to decode incoming request '
            return response

        # Send back the results
        try:
            logger.info('response[%s]: %s', encoding, response.encode('utf-8'))
            request.setHeader('content-type', encoding)
            request.setResponseCode(http.OK)
            return response.encode('utf-8')

        except Exception:
            logger.exception('unknown exception while processing request %s',
                             request.path)
            response = 'UNKNOWN_ERROR: unknown exception processing ' + \
                'http request {0}'.format(request.path)
            return response
