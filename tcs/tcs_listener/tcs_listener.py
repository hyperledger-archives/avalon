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
import random
import json

import urllib.request
import urllib.error
from twisted.web import server, resource, http
from twisted.internet import reactor
from twisted.web.error import Error
from tcs_work_order_handler import TCSWorkOrderHandler
from tcs_worker_registry_handler import TCSWorkerRegistryHandler
from tcs_workorder_receipt_handler import TCSWorkOrderReceiptHandler
from tcs_worker_encryption_key_handler import WorkerEncryptionKeyHandler
from shared_kv.shared_kv_interface import KvStorage
from error_code.error_status import WorkorderError

import logging
logger = logging.getLogger(__name__)

## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
class TCSListener(resource.Resource):
    """
    TCSListener Class  is comprised of HTTP interface which listens for the end user requests, 
    Worker Registry Handler, Work Order Handler and Work Order Receipts Handler .
    """
    # The isLeaf instance variable describes whether or not a resource will have children and only leaf resources get rendered.
    # TCSListener is the most derived class hence isLeaf is required.

    isLeaf = True

     ## -----------------------------------------------------------------
    def __init__(self, config):

        if config.get('KvStorage') is None:
            logger.error("Kv Storage path is missing")
            sys.exit(-1)

        storage_path = TCFHOME + '/' + config['KvStorage']['StoragePath']
        self.kv_helper = KvStorage()
        if  not self.kv_helper.open(storage_path):
            logger.error("Failed to open KV Storage DB")
            sys.exit(-1)

        # Worker registry handler needs to be instantiated before Work order handler. Otherwise, LMDB operations don't operate on updated values.
        # TODO: Needs further investigation on what is causing the above behavior.

        self.worker_registry_handler = TCSWorkerRegistryHandler(self.kv_helper)
        self.workorder_handler = TCSWorkOrderHandler(self.kv_helper, config["Listener"]["max_work_order_count"])
        self.workorder_receipt_handler = TCSWorkOrderReceiptHandler(self.kv_helper)
        self.worker_encryption_key_handler = WorkerEncryptionKeyHandler(self.kv_helper)

    def _process_request(self, input_json_str):
        response = {}
        response['error'] = {}
        response['error']['code'] = WorkorderError.INVALID_PARAMETER_FORMAT_OR_VALUE

        try:
            input_json = json.loads(input_json_str)
        except:
            response['error']['message'] = 'Error: Improper Json. Unable to load'
            return response

        if ('jsonrpc' not in input_json or 'id' not in input_json
            or 'method' not in input_json or 'params' not in input_json):
            response['error']['message'] = 'Error: Json does not have the required field'
            return response

        if not isinstance(input_json['id'], int):
            response['error']['message'] = 'Error: Id should be of type integer'
            return response

        response['jsonrpc'] = input_json['jsonrpc']
        response['id'] = input_json['id']

        if not isinstance(input_json['method'], str):
            response['error']['message'] = 'Error: Method has to be of type string'
            return response

        if ( (input_json['method'] == "WorkOrderSubmit")     or
            (input_json['method'] == "WorkOrderGetResult")):
            return self.workorder_handler.process_work_order(input_json_str)
        elif("WorkOrderReceipt" in input_json['method']):
            return self.workorder_receipt_handler.workorder_receipt_handler(input_json_str)
        elif ("Worker" in input_json['method']):
            return self.worker_registry_handler.worker_registry_handler(input_json_str)
        elif ("EncryptionKey" in input_json['method']):
            return self.worker_encryption_key_handler.process_encryption_key(input_json_str)
        else:
            response['error']['message'] = 'Error: Invalid method field'
            return response

    def render_GET(self, request):
        response = {}
        response['error'] = {}
        response['error']['code'] = WorkorderError.INVALID_PARAMETER_FORMAT_OR_VALUE
        response['error']['message'] = 'Only POST request is supported'
        logger.error("GET request is not supported. Only POST request is supported")
        
        return response

    def render_POST(self, request):
        response = {}
        response['error'] = {}
        response['error']['code'] = WorkorderError.UNKNOWN_ERROR
       
        logger.info('Received a new request from the client')

        try :
            # process the message encoding
            encoding = request.getHeader('Content-Type')
            data = request.content.read()

            if encoding == 'application/json' :

                try:
                    input_json = json.loads(data.decode('utf-8'))
                    response = self._process_request(input_json)

                except AttributeError:
                    logger.error("Error while loading input json")
                    response['error']['message'] = 'UNKNOWN_ERROR: Error while loading the input JSON file'
                    return response

            else :
                response['error']['message'] = 'UNKNOWN_ERROR: unknown message encoding'
                return response

        except :
            logger.exception('exception while decoding http request %s', request.path)
            response['error']['message'] = 'UNKNOWN_ERROR: unable to decode incoming request '
            return response

        # send back the results
        try :
            if encoding == 'application/json' :
                response = json.dumps(response)

            logger.info('response[%s]: %s', encoding, response)
            request.setHeader('content-type', encoding)
            request.setResponseCode(http.OK)
            return response.encode('utf8')

        except :
            logger.exception('unknown exception while processing request %s', request.path)
            response['error']['message'] = 'UNKNOWN_ERROR: unknown exception processing http request {0}'.format(request.path)
            return response

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def local_main(config):

    root = TCSListener(config)
    site = server.Site(root)
    reactor.listenTCP(int(bind_uri), site)

    logger.info('TCS Listener started on port %s', bind_uri)

    try :
        reactor.run()
    except ReactorNotRunning:
        logger.warn('shutdown')
    except :
        logger.warn('shutdown')

    exit(0)

## -----------------------------------------------------------------

TCFHOME = os.environ.get("TCF_HOME", "../../../../")

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def parse_command_line(config, args) :

    global bind_uri

    parser = argparse.ArgumentParser()

    parser.add_argument('--logfile', help='Name of the log file, __screen__ for standard output', type=str)
    parser.add_argument('--loglevel', help='Logging level', type=str)
    parser.add_argument('--bind_uri', help='URI to listen for requests ',type=str)

    options = parser.parse_args(args)

    if config.get('Logging') is None :
        config['Logging'] = {
            'LogFile' : '__screen__',
            'LogLevel' : 'INFO'
        }
    if options.logfile :
        config['Logging']['LogFile'] = options.logfile
    if options.loglevel :
        config['Logging']['LogLevel'] = options.loglevel.upper()
    if options.bind_uri :
        bind_uri = options.bind_uri


# -----------------------------------------------------------------
# -----------------------------------------------------------------
def main(args=None) :
    import config.config as pconfig
    import utility.logger as plogger

    # parse out the configuration file first
    conffiles = [ 'tcs_config.toml' ]
    confpaths = [ ".", TCFHOME + "/config"]

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='configuration file', nargs = '+')
    parser.add_argument('--config-dir', help='configuration folder', nargs = '+')
    (options, remainder) = parser.parse_known_args(args)

    if options.config :
        conffiles = options.config

    if options.config_dir :
        confpaths = options.config_dir

    try :
        config = pconfig.parse_configuration_files(conffiles, confpaths)
        config_json_str = json.dumps(config, indent=4)
    except pconfig.ConfigurationException as e :
        logger.error(str(e))
        sys.exit(-1)

    plogger.setup_loggers(config.get('Logging', {}))
    sys.stdout = plogger.stream_to_logger(logging.getLogger('STDOUT'), logging.DEBUG)
    sys.stderr = plogger.stream_to_logger(logging.getLogger('STDERR'), logging.WARN)

    parse_command_line(config, remainder)
    local_main(config)

main()
