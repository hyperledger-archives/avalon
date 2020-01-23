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

from urllib.parse import urlsplit
from twisted.web import server, resource, http
from twisted.internet import reactor
from avalon_listener.tcs_work_order_handler import TCSWorkOrderHandler
from avalon_listener.tcs_worker_registry_handler \
        import TCSWorkerRegistryHandler
from avalon_listener.tcs_workorder_receipt_handler \
        import TCSWorkOrderReceiptHandler
from avalon_listener.tcs_worker_encryption_key_handler \
        import WorkerEncryptionKeyHandler
from database import connector
from error_code.error_status import WorkOrderStatus
import utility.jrpc_utility as jrpc_utility

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
    # The isLeaf instance variable describes whether or not a resource will
    # have children and only leaf resources get rendered.
    # TCSListener is the most derived class hence isLeaf is required.

    isLeaf = True

    # -----------------------------------------------------------------
    def __init__(self, config):
        try:
            self.kv_helper = \
                    connector.open(config['KvStorage']['remote_storage_url'])
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
        response['error']['code'] = \
            WorkOrderStatus.INVALID_PARAMETER_FORMAT_OR_VALUE

        try:
            input_json = json.loads(input_json_str)
        except Exception as err:
            logger.exception("exception loading Json: %s", str(err))
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
        response = jrpc_utility.create_error_response(
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
                    response = jrpc_utility.create_error_response(
                        WorkOrderStatus.UNKNOWN_ERROR,
                        jrpc_id,
                        "UNKNOWN_ERROR: Error while loading input JSON file")
                    return response

            else:
                # JRPC response with 0 as id is returned because id can't be
                # fetched from a request with unknown encoding.
                response = jrpc_utility.create_error_response(
                    WorkOrderStatus.UNKNOWN_ERROR,
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

        except Exception as err:
            logger.exception(
                'unknown exception while processing request %s: %s',
                request.path, str(err))
            response = jrpc_utility.create_error_response(
                WorkOrderStatus.UNKNOWN_ERROR,
                jrpc_id,
                "UNKNOWN_ERROR: unknown exception processing http " +
                "request {0}: {1}".format(request.path, str(err)))
            return response

# -----------------------------------------------------------------
# -----------------------------------------------------------------


def local_main(config, host_name, port):

    root = TCSListener(config)
    site = server.Site(root)
    reactor.listenTCP(port, site, interface=host_name)

    logger.info('TCS Listener started on port %s', port)

    try:
        reactor.run()
    except ReactorNotRunning:
        logger.warn('shutdown')
    except Exception as err:
        logger.warn('shutdown: %s', str(e))

    exit(0)

# -----------------------------------------------------------------


TCFHOME = os.environ.get("TCF_HOME", "../../../../")

# -----------------------------------------------------------------
# -----------------------------------------------------------------


def parse_bind_url(url):
    """
    Parse the url and validate against supported format
    params:
        url is string
    returns:
        returns tuple containing hostname and port,
        both are of type string
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


def parse_command_line(config, args):

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--logfile',
        help='Name of the log file, __screen__ for standard output', type=str)
    parser.add_argument('--loglevel', help='Logging level', type=str)
    parser.add_argument(
        '--bind', help='URI to listen for requests ', type=str)
    parser.add_argument(
        '--lmdb_url', help='DB url to connect to LMDB ', type=str)

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
    if options.bind:
        host_name, port = parse_bind_url(options.bind)
    else:
        if config.get("Listener") is None or \
                config["Listener"].get("bind") is None:
                    logger.warn("quit due to no suitable config for Listener")
                    sys.exit(-1)
        host_name, port = parse_bind_url(
            config["Listener"].get("bind"))
    if options.lmdb_url:
        config["KvStorage"]["remote_storage_url"] = options.lmdb_url
    else:
        if config.get("KvStorage") is None or \
                config["KvStorage"].get("remote_storage_url") is None:
                    logger.warn("quit because remote_storage_url is not \
                            present in config for Listener")
                    sys.exit(-1)

    return host_name, port

# -----------------------------------------------------------------
# -----------------------------------------------------------------


def get_config_dir():
    """
    Returns the avalon configuration directory based on the
    TCF_HOME environment variable (if set) or OS defaults.
    """
    if 'TCF_HOME' in os.environ:
        return os.path.join(os.environ['TCF_HOME'], 'listener/')
    else:
        logger.warn("quit because TCF_HOME is not defined in your environment")
        sys.exit(-1)


def main(args=None):
    import config.config as pconfig
    import utility.logger as plogger

    # parse out the configuration file first
    conf_file = ['listener_config.toml']
    conf_path = [get_config_dir()]

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='configuration file', nargs='+')
    parser.add_argument('--config-dir', help='configuration folder', nargs='+')
    (options, remainder) = parser.parse_known_args(args)

    if options.config:
        conf_file = options.config

    if options.config_dir:
        conf_path = options.config_dir

    try:
        config = pconfig.parse_configuration_files(conf_file, conf_path)
    except pconfig.ConfigurationException as e:
        logger.error(str(e))
        sys.exit(-1)

    plogger.setup_loggers(config.get('Logging', {}))
    sys.stdout = plogger.stream_to_logger(
        logging.getLogger('STDOUT'), logging.DEBUG)
    sys.stderr = plogger.stream_to_logger(
        logging.getLogger('STDERR'), logging.WARN)

    host_name, port = parse_command_line(config, remainder)
    local_main(config, host_name, port)


main()
