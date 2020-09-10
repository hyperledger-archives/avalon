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


import sys
import json
import logging
import argparse
import schema_validation.validate as Validator

from urllib.parse import urlparse
from avalon_listener.tcs_work_order_handler import TCSWorkOrderHandler
from avalon_listener.tcs_work_order_handler_sync import TCSWorkOrderHandlerSync
from avalon_listener.tcs_worker_registry_handler \
    import TCSWorkerRegistryHandler
from avalon_listener.tcs_workorder_receipt_handler \
    import TCSWorkOrderReceiptHandler
from avalon_listener.tcs_worker_encryption_key_handler \
    import WorkerEncryptionKeyHandler
from database import connector
from listener.base_jrpc_listener \
    import BaseJRPCListener, parse_bind_url, get_config_dir
from jsonrpc import JSONRPCResponseManager
from error_code.error_status import JRPCErrorCodes

logger = logging.getLogger(__name__)

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


class TCSListener(BaseJRPCListener):
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
        if int(config["WorkloadExecution"]["sync_workload_execution"]) == 1:
            self.workorder_handler = TCSWorkOrderHandlerSync(
                self.kv_helper,
                config["Listener"]["max_work_order_count"],
                config["Listener"]["zmq_url"])
        else:
            self.workorder_handler = TCSWorkOrderHandler(
                self.kv_helper,
                config["Listener"]["max_work_order_count"])

        self.workorder_receipt_handler = TCSWorkOrderReceiptHandler(
            self.kv_helper)
        self.worker_encryption_key_handler = WorkerEncryptionKeyHandler(
            self.kv_helper)

        rpc_methods = [
            self.worker_encryption_key_handler.EncryptionKeyGet,
            self.worker_encryption_key_handler.EncryptionKeySet,
            self.worker_registry_handler.WorkerLookUp,
            self.worker_registry_handler.WorkerLookUpNext,
            self.worker_registry_handler.WorkerRetrieve,
            self.workorder_handler.WorkOrderSubmit,
            self.workorder_handler.WorkOrderGetResult,
            self.workorder_receipt_handler.WorkOrderReceiptCreate,
            self.workorder_receipt_handler.WorkOrderReceiptUpdate,
            self.workorder_receipt_handler.WorkOrderReceiptRetrieve,
            self.workorder_receipt_handler.WorkOrderReceiptUpdateRetrieve,
            self.workorder_receipt_handler.WorkOrderReceiptLookUp,
            self.workorder_receipt_handler.WorkOrderReceiptLookUpNext
        ]
        super().__init__(rpc_methods)

# -----------------------------------------------------------------

    def _process_request(self, input_json_str):
        """
        Overridden method to dispatch to appropriate rpc method with
        added schema and request validation

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
            valid, err_msg = \
                Validator.schema_validation("tc_methods", input_json)
            if not valid:
                raise ValueError(err_msg)
            valid, err_msg = \
                Validator.schema_validation(
                    input_json["method"],
                    input_json["params"])
            if not valid:
                raise ValueError(err_msg)
        except Exception as err:
            logger.error("Exception while processing Json: %s", str(err))
            response["error"]["message"] = \
                "{}".format(str(err))
            return response

        # save the full json for WorkOrderSubmit
        input_json["params"]["raw"] = input_json_str
        data = json.dumps(input_json).encode('utf-8')
        response = JSONRPCResponseManager.handle(data, self.dispatcher)
        return response.data

# -----------------------------------------------------------------
# -----------------------------------------------------------------


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
    parser.add_argument(
        '--sync_mode', help='Work order execution in synchronous mode',
        type=bool, default=False)
    parser.add_argument(
        '--zmq_url',
        help='ZMQ url to connect to enclave manager ', type=str)

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
            logger.error("Quit : no bind config found for Listener")
            sys.exit(-1)
        host_name, port = parse_bind_url(
            config["Listener"].get("bind"))
    if options.lmdb_url:
        config["KvStorage"]["remote_storage_url"] = options.lmdb_url
    else:
        if config.get("KvStorage") is None or \
                config["KvStorage"].get("remote_storage_url") is None:
            logger.error("Quit : remote_storage_url is not \
                            present in config for Listener")
            sys.exit(-1)
    # Check if listener is running in sync work order
    if options.sync_mode:
        is_sync = True
    else:
        is_sync = config["WorkloadExecution"]["sync_workload_execution"]

    if options.zmq_url:
        if not is_sync:
            logger.warn("Option zmq_url has no effect!"
                        "It is be supported "
                        "in work order sync mode ON")
        if config.get("Listener") is None or \
                config["Listener"].get("zmq_url") is None:
            logger.error("Quit : no zmq_url config found for Listener")
            sys.exit(-1)
        parse_res = urlparse(options.zmq_url)
        if parse_res.scheme != "tcp" or parse_res.port == "":
            logger.error("Invalid zmq url. It should be tcp://<host>:<port>")
            sys.exit(-1)
        config["Listener"]["zmq_url"] = options.zmq_url

    return host_name, port

# -----------------------------------------------------------------
# -----------------------------------------------------------------


def main(args=None):
    import config.config as pconfig
    import utility.logger as plogger

    # parse out the configuration file first
    conf_file = ['listener_config.toml']
    conf_path = [get_config_dir('listener/')]

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
    tcs_listener = TCSListener(config)
    tcs_listener.start(host_name, port)


main()
