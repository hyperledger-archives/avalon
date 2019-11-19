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
import json
import unittest
import time

from lmdb_helper_proxy import LMDBHelperProxy

import logging
logger = logging.getLogger(__name__)

TCFHOME = os.environ.get("TCF_HOME", "../../../../")
# -----------------------------------------------------------------


class TestRemoteLMDB(unittest.TestCase):
    def __init__(self):
        super(TestRemoteLMDB, self).__init__()
        self.proxy = LMDBHelperProxy(bind_uri)
        self.table = "\\ndtable"
        self.key = "\ndk\\y"
        self.value = "d\\\nvalue\n"
        self.key2 = "dke\\\\y2"
        self.value2 = "dvalue2"

    def test_set(self):
        set_result = self.proxy.set(self.table, self.key, self.value)
        logger.info(set_result)
        self.assertTrue(set_result, "set Failed")

    def test_set2(self):
        set_result2 = self.proxy.set(self.table, self.key2, self.value2)
        logger.info(set_result2)
        self.assertTrue(set_result2, "set Failed")

    def test_lookup(self):
        lookup_result = self.proxy.lookup(self.table)
        logger.info(lookup_result)
        self.assertEqual(lookup_result, [self.key, self.key2],
                         "lookup Returned wrong keys")

    def test_get_value(self):
        get_value_result = self.proxy.get(self.table, self.key)
        logger.info(get_value_result)
        self.assertEqual(get_value_result, self.value,
                         "get_value Retrieved incorrect value")

    def test_get_value2(self):
        get_value_result2 = self.proxy.get(self.table, self.key2)
        logger.info(get_value_result2)
        self.assertEqual(get_value_result2, self.value2,
                         "get_value Retrieved incorrect value")

    def test_remove(self):
        remove_result = self.proxy.remove(self.table, self.key)
        logger.info(remove_result)
        self.assertTrue(remove_result, "remove Failed")

    def test_get_none(self):
        get_none_result = self.proxy.get(self.table, self.key)
        logger.info(get_none_result)
        self.assertIsNone(get_none_result,
                          "get_none Did not return None for empty value")

    def test_remove2(self):
        remove_result2 = self.proxy.remove(self.table, self.key2)
        logger.info(remove_result2)
        self.assertTrue(remove_result2, "remove Failed")

    def test_lookup_none(self):
        lookup_none_result = self.proxy.lookup(self.table)
        logger.info(lookup_none_result)
        self.assertEqual(lookup_none_result, [],
                         "lookup_none Did not return empty array")

# -----------------------------------------------------------------


def local_main():
    result = unittest.TestResult()
    result.startTestRun()
    test = TestRemoteLMDB()
    test.test_set()
    test.test_set2()
    test.test_lookup()
    test.test_get_value()
    test.test_get_value2()
    test.test_remove()
    test.test_get_none()
    test.test_remove2()
    test.test_lookup_none()
    result.stopTestRun()
    if result.wasSuccessful():
        logger.info("All tests passed!")
    else:
        logger.info("Some tests failed.")
    exit(0)

# -----------------------------------------------------------------


def parse_command_line(config, args):

    global bind_uri

    parser = argparse.ArgumentParser()

    parser.add_argument('--logfile',
                        help='Name of the log file, __screen__ for standard output',
                        type=str)
    parser.add_argument('--loglevel',
                        help='Logging level',
                        type=str)
    parser.add_argument('--bind_uri',
                        help='URI to send requests to',
                        type=str,
                        default='http://localhost:9091')

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

    # Parse out the configuration file first
    conffiles = ['tcs_config.toml']
    confpaths = [".", TCFHOME + "/config"]

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='configuration file',
                        nargs='+')
    parser.add_argument('--config-dir', help='configuration folder',
                        nargs='+')
    (options, remainder) = parser.parse_known_args(args)

    if options.config:
        conffiles = options.config

    if options.config_dir:
        confpaths = options.config_dir

    try:
        config = pconfig.parse_configuration_files(conffiles, confpaths)
        json.dumps(config, indent=4)
    except pconfig.ConfigurationException as e:
        logger.error(str(e))
        sys.exit(-1)

    plogger.setup_loggers(config.get('Logging', {}))
    sys.stdout = plogger.stream_to_logger(
        logging.getLogger('STDOUT'), logging.DEBUG)
    sys.stderr = plogger.stream_to_logger(
        logging.getLogger('STDERR'), logging.WARN)

    parse_command_line(config, remainder)
    local_main()


main()
