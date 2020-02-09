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
import toml
from urllib.parse import urlsplit
from twisted.web import server
from twisted.internet import reactor
from twisted.internet.error import ReactorNotRunning

from kv_storage.remote_lmdb.lmdb_request_handler import LMDBRequestHandler

import logging
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------


def local_main(config, host_name, port):

    root = LMDBRequestHandler(config)
    site = server.Site(root)
    reactor.listenTCP(port, site, interface=host_name)
    logger.info('LMDB Listener started on port %s', port)

    try:
        reactor.run()
    except ReactorNotRunning:
        del root
        logger.warn('shutdown')
    except Exception:
        del root
        logger.warn('shutdown')

    exit(0)

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
        if (port is None or
            scheme is None or
                host_name is None) and scheme != 'http':
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

    parser.add_argument('--logfile',
                        help='Name of the log file, \
                              __screen__ for standard output',
                        type=str)
    parser.add_argument('--loglevel',
                        help='Logging level',
                        type=str)
    parser.add_argument('--bind',
                        help='identify host and port for \
                              lmdb server to run on',
                        type=str)

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
        if config.get("KvStorage") is None or \
                config["KvStorage"].get("bind") is None:
            logger.warn("quit due to no suitable config for remote KvStorage")
            sys.exit(-1)
        host_name, port = parse_bind_url(
            config["KvStorage"].get("bind"))
    return host_name, port
# -----------------------------------------------------------------


def get_config_dir():
    """Returns the avalon configuration directory based on the TCF__HOME
    environment variable (if set) or OS defaults."""
    if 'TCF_HOME' in os.environ:
        return os.path.join(os.environ['TCF_HOME'], 'shared_kv_storage/')

    return '/etc/avalon'


def main(args=None):
    # Parse out the configuration file first
    conffile = 'lmdb_config.toml'
    confpath = get_config_dir()

    parser = argparse.ArgumentParser()
    parser.add_argument('--config',
                        help='configuration file',
                        nargs='+')
    parser.add_argument('--config-dir',
                        help='configuration folder',
                        nargs='+')
    (options, remainder) = parser.parse_known_args(args)

    if options.config:
        conffile = options.config

    if options.config_dir:
        conffile = options.config_dir + options.config
    else:
        conffile = confpath + conffile
    try:
        config = toml.load(conffile)
    except TypeError as e:
        logger.error(str(e))
        sys.exit(-1)
    except toml.TomlDecodeError as e:
        logger.error(str(e))
        sys.exit(-1)

    logger.setLevel(config.get('Logging', {})['LogLevel'])

    host_name, port = parse_command_line(config, remainder)
    local_main(config, host_name, port)


main()
