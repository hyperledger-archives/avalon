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
import argparse
import json

from twisted.web import server, resource, http
from twisted.internet import reactor
from tcs_work_order_handler import TCSWorkOrderHandler
from tcs_worker_registry_handler import TCSWorkerRegistryHandler
from tcs_workorder_receipt_handler import TCSWorkOrderReceiptHandler
from tcs_worker_encryption_key_handler import WorkerEncryptionKeyHandler
from database import connector
from error_code.error_status import WorkOrderStatus
import utility.utility as utility

from jsonrpc import JSONRPCResponseManager
from jsonrpc.dispatcher import Dispatcher

import logging
logger = logging.getLogger(__name__)

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


class TCSListener(resource.Resource):
    """
    TCSListener Class is comprised of HTTP interface which listens for the
    end user requests, Worker Registry Handler, Work Order Handler and
    Work Order Receipts Handler .
    """
    # The isLeaf instance variable describes whether or not a resource will have children and only leaf resources get rendered.
    # TCSListener is the most derived class hence isLeaf is required.

    isLeaf = True

    # -----------------------------------------------------------------
    def __init__(self, config):
        try:
            (self.kv_helper, _) = connector.open(config)
        except Exception as err:
            logger.error(f"failed to open db: {err}")
            sys.exit(-1)

        self.worker_registry_handler = TCSWorkerRegistryHandler(self.kv_helper)
        self.workorder_handler = TCSWorkOrderHandler(
            self.kv_helper, config["Listener"]["max_work_order_count"])
        self.workorder_receipt_handler = TCSWorkOrderReceiptHandler(
            self.kv_helper)
        self.worker_encryption_key_handler = WorkerEncryptionKeyHandler(
            self.kv_helper)

        self.dispatcher = Dispatcher()
        rpc_methods = [
            self.worker_encryption_key_handler.EncryptionKeyGet,
            self.worker_encryption_key_handler.EncryptionKeySet,
            self.worker_registry_handler.WorkerLookUp,
            self.worker_registry_handler.WorkerLookUpNext,
            self.worker_registry_handler.WorkerRegister,
            self.worker_registry_handler.WorkerSetStatus,
            self.worker_registry_handler.WorkerRetrieve,
            self.worker_registry_handler.WorkerUpdate,
            self.workorder_handler.WorkOrderSubmit,
            self.workorder_handler.WorkOrderGetResult,
            self.workorder_receipt_handler.WorkOrderReceiptCreate,
            self.workorder_receipt_handler.WorkOrderReceiptUpdate,
            self.workorder_receipt_handler.WorkOrderReceiptRetrieve,
            self.workorder_receipt_handler.WorkOrderReceiptUpdateRetrieve,
            self.workorder_receipt_handler.WorkOrderReceiptLookUp,
            self.workorder_receipt_handler.WorkOrderReceiptLookUpNext
        ]
        for m in rpc_methods:
            self.dispatcher.add_method(m)

    def _process_request(self, input_json_str):
        response = {}
        response['error'] = {}
        response['error']['code'] = WorkOrderStatus.INVALID_PARAMETER_FORMAT_OR_VALUE

        try:
            input_json = json.loads(input_json_str)
        except:
            response = {
                "error": {
                    "code": WorkOrderStatus.INVALID_PARAMETER_FORMAT_OR_VALUE,
                    "message": "Error: Improper Json. Unable to load",
                },
            }
            return response

        logger.info("Received request: %s", input_json['method'])
        # save the full json for WorkOrderSubmit
        input_json["params"]["raw"] = input_json_str

        data = json.dumps(input_json).encode('utf-8')
        response = JSONRPCResponseManager.handle(data, self.dispatcher)
        return response.data

    def render_GET(self, request):
        # JRPC response with id 0 is returned because id parameter
        # will not be found in GET request
        response = utility.create_error_response(
            WorkOrderStatus.INVALID_PARAMETER_FORMAT_OR_VALUE, "0",
            "Only POST request is supported")
        logger.error(
            "GET request is not supported. Only POST request is supported")

        return response

    def render_POST(self, request):
        response = {}

        logger.info('Received a new request from the client')
        try:
            # process the message encoding
            encoding = request.getHeader('Content-Type')
            data = request.content.read()
            if encoding == 'application/json':

                try:
                    input_json_str = data.decode('utf-8')
                    input_json = json.loads(input_json_str)
                    jrpc_id = input_json["id"]
                    response = self._process_request(input_json_str)

                except AttributeError:
                    logger.error("Error while loading input json")
                    response = utility.create_error_response(
                        WorkOrderStatus.UNKNOWN_ERROR,
                        jrpc_id,
                        "UNKNOWN_ERROR: Error while loading the input JSON file")
                    return response

            else:
                # JRPC response with 0 as id is returned because id can't be fecthed
                # from a request with unknown encoding
                response = utility.create_error_response(
                    WorkOrderStatus.UNKNOWN_ERROR,
                    0,
                    "UNKNOWN_ERROR: unknown message encoding")
                return response

        except:
            logger.exception(
                'exception while decoding http request %s', request.path)
            # JRPC response with 0 as id is returned because id can't be
            # fetched from improper request
            response = utility.create_error_response(
                WorkOrderStatus.UNKNOWN_ERROR,
                0,
                "UNKNOWN_ERROR: unable to decode incoming request")
            return response

        # send back the results
        try:
            if encoding == 'application/json':
                response = json.dumps(response)
            logger.info('response[%s]: %s', encoding, response)
            request.setHeader('content-type', encoding)
            request.setResponseCode(http.OK)
            return response.encode('utf8')

        except:
            logger.exception(
                'unknown exception while processing request %s', request.path)
            response = utility.create_error_response(
                WorkOrderStatus.UNKNOWN_ERROR,
                jrpc_id,
                "UNKNOWN_ERROR: unknown exception processing http \
                    request {0}".format(request.path))
            return response

# -----------------------------------------------------------------
# -----------------------------------------------------------------


def local_main(config):

    root = TCSListener(config)
    site = server.Site(root)
    reactor.listenTCP(int(bind_uri), site)

    logger.info('TCS Listener started on port %s', bind_uri)

    try:
        reactor.run()
    except ReactorNotRunning:
        logger.warn('shutdown')
    except:
        logger.warn('shutdown')

    exit(0)

# -----------------------------------------------------------------


TCFHOME = os.environ.get("TCF_HOME", "../../../../")

# -----------------------------------------------------------------
# -----------------------------------------------------------------


def parse_command_line(config, args):

    global bind_uri

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--logfile', help='Name of the log file, __screen__ for standard output', type=str)
    parser.add_argument('--loglevel', help='Logging level', type=str)
    parser.add_argument(
        '--bind_uri', help='URI to listen for requests ', type=str)

    options = parser.parse_args(args)

    if config.get('Logging') is None:
        config['Logging'] = {
            'LogFile': '__screen__',
            'LogLevel': 'INFO'
        }
    if options.logfile:
        config['Logging']['LogFile'] = options.logfile
    if options.loglevel:
        config['Logging']['LogLevel'] = options.loglevel.upper()
    if options.bind_uri:
        bind_uri = options.bind_uri


# -----------------------------------------------------------------
# -----------------------------------------------------------------
def main(args=None):
    import config.config as pconfig
    import utility.logger as plogger

    # parse out the configuration file first
    conffiles = ['tcs_config.toml']
    confpaths = [".", TCFHOME + "/config"]

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='configuration file', nargs='+')
    parser.add_argument('--config-dir', help='configuration folder', nargs='+')
    (options, remainder) = parser.parse_known_args(args)

    if options.config:
        conffiles = options.config

    if options.config_dir:
        confpaths = options.config_dir

    try:
        config = pconfig.parse_configuration_files(conffiles, confpaths)
    except pconfig.ConfigurationException as e:
        logger.error(str(e))
        sys.exit(-1)

    plogger.setup_loggers(config.get('Logging', {}))
    sys.stdout = plogger.stream_to_logger(
        logging.getLogger('STDOUT'), logging.DEBUG)
    sys.stderr = plogger.stream_to_logger(
        logging.getLogger('STDERR'), logging.WARN)

    parse_command_line(config, remainder)
    local_main(config)


main()
