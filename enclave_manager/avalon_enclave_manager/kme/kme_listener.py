#!/usr/bin/env python3

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

import sys
import logging
import argparse

import config.config as pconfig
import utility.logger as plogger
from listener.base_jrpc_listener \
    import BaseJRPCListener, start_listener, parse_bind_url, get_config_dir

logger = logging.getLogger(__name__)


class KMEListener(BaseJRPCListener):
    """
    Listener to handle requests from WorkerProcessingEnclave(WPE)
    """

    # The isLeaf instance variable describes whether a resource will have
    # children and only leaf resources get rendered. KMEListener is a leaf
    # node in the derivation tree and hence isLeaf is required.
    isLeaf = True

    def __init__(self, config):

        self.kme_request_handler = None

        # TODO : Uncomment following statements after
        # a request handler is created
        '''
        rpc_methods = [self.kme_request_handler.RegisterWorkorderProcessor,
                          self.kme_request_handler.PreporocessWorkorder]
        super().__init__(rpc_methods)
        '''


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
        if config.get("KMEListener") is None or \
                config["KMEListener"].get("bind") is None:
            logger.error("Quit : no bind config found for KMEListener")
            sys.exit(-1)
        host_name, port = parse_bind_url(
            config["KMEListener"].get("bind"))

    return host_name, port

# -----------------------------------------------------------------
# -----------------------------------------------------------------


def main(args=None):

    # parse out the configuration file first
    conf_file = ['config.toml']
    conf_path = [get_config_dir('enclave_manager/avalon_enclave_manager/kme')]

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
    start_listener(host_name, port, KMEListener(config))


main()
