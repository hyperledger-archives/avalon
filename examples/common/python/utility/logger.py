# Copyright 2018 Intel Corporation
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

"""
logger.py -- functions to create and configure logging
functions based on a configuration file.

NOTE: functions defined in this file are designed to be run
before logging is enabled.
"""

import logging
import logging.handlers
import os
import sys
import warnings

from colorlog import ColoredFormatter

__all__ = ['stream_to_logger', 'setup_loggers']


# -----------------------------------------------------------------
class stream_to_logger(object):
    """
    Simple class to redirect stdout/stderr to log files
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


# -----------------------------------------------------------------
def setup_loggers(config):
    loglevel = getattr(logging, config.get('LogLevel', 'WARN'))
    logger = logging.getLogger()
    logger.setLevel(loglevel)

    logfile = config.get('LogFile', '__screen__')
    if logfile != '__screen__':
        if not os.path.isdir(os.path.dirname(logfile)):
            warnings.warn(
                "Logging directory {0} does not exist".format(
                    os.path.abspath(os.path.dirname(logfile))))
            sys.exit(-1)

        flog = logging.handlers.RotatingFileHandler(
            logfile, maxBytes=2 * 1024 * 1024, backupCount=1000, mode='a')
        flog.setFormatter(
            logging.Formatter(
                '[%(asctime)s, %(levelno)d, %(name)s] %(message)s',
                "%H:%M:%S"))
        logger.addHandler(flog)
    else:
        clog = logging.StreamHandler()
        formatter = ColoredFormatter(
            "%(log_color)s[%(asctime)s " +
            "%(levelname)-8s%(name)s]%(reset)s %(white)s%(message)s",
            datefmt="%H:%M:%S",
            reset=True,
            log_colors={
                        'DEBUG': 'cyan',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'red',
                       })

        clog.setFormatter(formatter)
        logger.addHandler(clog)

    # Process all overrides
    logoverride = config.get("LogOverride", {})
    for modname, modlevel in logoverride.items():
        modlogger = logging.getLogger(modname)
        modlogger.setLevel(getattr(logging, modlevel))
