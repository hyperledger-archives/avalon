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
import sys
import argparse
from urllib.parse import urlparse
from twisted.web import server
from twisted.internet import reactor

from lmdb_request_handler import LMDBRequestHandler

import logging
logger = logging.getLogger(__name__)

TCFHOME = os.environ.get("TCF_HOME", "../../../../")

# -----------------------------------------------------------------


def local_main(config):

    root = LMDBRequestHandler(config)
    site = server.Site(root)
    reactor.listenTCP(bind_port, site)
    logger.info('LMDB Listener started on port %s', bind_port)

    try:
        reactor.run()
    except ReactorNotRunning:
        logger.warn('shutdown')
    except:
        logger.warn('shutdown')

    exit(0)

# -----------------------------------------------------------------


def parse_command_line(config, args):

    global bind_port

    if config.get("KvStorage") is None or config["KvStorage"].get("remote_url") is None:
        logger.warn("quit due to no suitable config for remote KvStorage")
        sys.exit(-1)

    # TODO: guard against None url_str
    url = urlparse(config["KvStorage"]["remote_url"])
    default_port = url.port
    logger.info(f"update default_port as {default_port} from TOML")

    parser = argparse.ArgumentParser()

    parser.add_argument('--logfile',
                        help='Name of the log file, __screen__ for standard output',
                        type=str)
    parser.add_argument('--loglevel',
                        help='Logging level',
                        type=str)
    parser.add_argument('--bind_port',
                        help='Port to listen for requests',
                        type=int,
                        default=default_port)

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
    if options.bind_port:
        bind_port = options.bind_port

# -----------------------------------------------------------------


def main(args=None):
    import config.config as pconfig
    import utility.logger as plogger

    # Parse out the configuration file first
    conffiles = ['tcs_config.toml']
    confpaths = [".", TCFHOME + "/config"]

    parser = argparse.ArgumentParser()
    parser.add_argument('--config',
                        help='configuration file',
                        nargs='+')
    parser.add_argument('--config-dir',
                        help='configuration folder',
                        nargs='+')
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
    sys.stdout = plogger.stream_to_logger(logging.getLogger('STDOUT'), logging.DEBUG)
    sys.stderr = plogger.stream_to_logger(logging.getLogger('STDERR'), logging.WARN)

    parse_command_line(config, remainder)
    local_main(config)


main()
