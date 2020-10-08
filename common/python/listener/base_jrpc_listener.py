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

# Values from -32768 to -32000 are reserved for pre-defined errors in
# the JSON RPC spec.
# 0 - success
# 1 - unknown error
# 2 - invalid parameter format or value
# 3 - access denied
# 4 - invalid signature
# 5 - no more lookup results
# 6 - unsupported mode (e.g. synchronous, asynchronous, pull, or notification)
# 7 - busy


import os
import sys
import json
import logging

from urllib.parse import urlsplit
from twisted.web import server, resource, http
from twisted.internet import reactor, error as reactor_error
from jsonrpc.dispatcher import Dispatcher
from jsonrpc import JSONRPCResponseManager
from error_code.error_status import JRPCErrorCodes

import utility.jrpc_utility as jrpc_utility

logger = logging.getLogger(__name__)

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


TCFHOME = os.environ.get("TCF_HOME", "../../")


class BaseJRPCListener(resource.Resource):
    """
    BaseJRPCListener Class is comprised of HTTP interface which listens for the
    end user requests using JRPC.
    """
    # The isLeaf instance variable describes whether or not a resource will
    # have children and only leaf resources get rendered.
    # BaseListener is the supposed to be one but last class in the derivation
    # tree. So, isLeaf is set to False.

    isLeaf = False

    # -----------------------------------------------------------------
    def __init__(self, rpc_methods):
        self.dispatcher = Dispatcher()
        for m in rpc_methods:
            self.dispatcher.add_method(m)

    def _process_request(self, input_json_str):
        """
        Handles incoming requests or rather dispatches to appropriate
        rpc method

        Parameters :
            input_json_str - JSON formatted str of the request
        Returns :
            response - data field from the response received which is a dict
        """
        response = {}
        response['error'] = {}
        response['error']['code'] = \
            JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE

        try:
            input_json = json.loads(input_json_str)
            if not ("id" in input_json.keys()) or \
               not ("method" in input_json.keys()) or \
               not (input_json["jsonrpc"] == "2.0"):
                raise KeyError("Improper id or jsonrpc or method")

            logger.info("Received request: %s", input_json['method'])
        except Exception as err:
            logger.error("Exception while processing Json: %s", str(err))
            response["error"]["message"] = "{}".format(str(err))
            return response

        # save the full json for WorkOrderSubmit
        input_json["params"]["raw"] = input_json_str
        data = json.dumps(input_json).encode('utf-8')
        response = JSONRPCResponseManager.handle(data, self.dispatcher)
        return response.data

    def render_GET(self, request):
        """
        Handle a GET request to the listener. Not supported. So only
        error is expected to be returned as response.

        Parameters :
            request - Request coming in from a client
        Returns :
            response - A dict type response which always contains error
        """
        # JRPC response with id 0 is returned because id parameter
        # will not be found in GET request
        response = jrpc_utility.create_error_response(
            JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE, "0",
            "Only POST request is supported")
        logger.error(
            "GET request is not supported. Only POST request is supported")

        return response

    def render_POST(self, request):
        """
        Handle a POST request to the listener. Decode and delegate to
        _process_request for handling.

        Parameters :
            request - Request coming in from a client
        Returns :
            response - A dict type response
        """
        response = {}

        logger.info('Received a new request from the client')
        try:
            # process the message encoding
            encoding = request.getHeader('Content-Type')
            data = request.content.read()
            # To support curl command content type
            # 'application/x-www-form-urlencoded' required
            if encoding in ['application/json',
                            'application/x-www-form-urlencoded']:
                input_json_str = data.decode('utf-8')
                response = self._process_request(input_json_str)

            else:
                # JRPC response with 0 as id is returned because id can't be
                # fetched from a request with unknown encoding.
                response = jrpc_utility.create_error_response(
                    JRPCErrorCodes.UNKNOWN_ERROR,
                    0,
                    "UNKNOWN_ERROR: unknown message encoding")
                return response

        except Exception as err:
            logger.exception(
                'exception while decoding http request %s: %s',
                request.path, str(err))
            # JRPC response with 0 as id is returned because id can't be
            # fetched from improper request
            response = jrpc_utility.create_error_response(
                JRPCErrorCodes.UNKNOWN_ERROR,
                0,
                "UNKNOWN_ERROR: unable to decode incoming request")
            return response

        # send back the results
        try:
            if encoding in ['application/json',
                            'application/x-www-form-urlencoded']:
                response = json.dumps(response)
            logger.info('response[%s]: %s', encoding, response)
            request.setHeader('content-type', encoding)
            request.setResponseCode(http.OK)
            return response.encode('utf8')

        except Exception as err:
            logger.exception(
                'unknown exception while processing request %s: %s',
                request.path, str(err))
            response = jrpc_utility.create_error_response(
                JRPCErrorCodes.UNKNOWN_ERROR,
                jrpc_id,
                "UNKNOWN_ERROR: unknown exception processing http " +
                "request {0}: {1}".format(request.path, str(err)))
            return response

    def start(self, host_name, port):
        """
        Start the listener instance on specified socket.

        Parameters :
            host_name - The hostname where this listener is reachable
            port - The port at which this listener needs to listen
        """
        root = self
        site = server.Site(root)
        reactor.listenTCP(port, site, interface=host_name)

        logger.info('%s started on port %s', type(self).__name__, port)

        try:
            reactor.run()
        except reactor_error.ReactorNotRunning:
            logger.error('shutdown')
        except Exception as err:
            logger.error('shutdown: %s', str(err))

        exit(0)

# -----------------------------------------------------------------
# -----------------------------------------------------------------


def parse_bind_url(url):
    """
    Parse the url, validate against supported format and return
    the hostname and port

    Parameters :
        url - Input url str
    Returns :
        host_name - Hostname that is a str
        port - Port address that is a str
    """
    try:
        parsed_str = urlsplit(url)
        scheme = parsed_str.scheme
        host_name = parsed_str.hostname
        port = parsed_str.port
        if (port is None or scheme is None or host_name is None) \
                and scheme != 'http':
            logger.error("Bind url should be format {} {} {} \
                    http://<hostname>:<port>".format(scheme, host_name, port))
            sys.exit(-1)
    except ValueError as e:
        logger.error("Wrong url format {}".format(e))
        logger.error("Bind url should be format \
                http://<hostname>:<port>")
        sys.exit(-1)
    return host_name, port


def get_config_dir(relative_path):
    """
    Returns the avalon configuration directory based on the
    TCF_HOME environment variable (if set).
    """
    if 'TCF_HOME' in os.environ:
        return os.path.join(os.environ['TCF_HOME'], relative_path)
    else:
        logger.error("Quit : TCF_HOME is not defined in your environment")
        sys.exit(-1)
