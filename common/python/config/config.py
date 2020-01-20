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
config.py -- Functions to load configuration files with support for
variable expansion.

NOTE: Functions defined in this file are designed to be run
before logging is enabled.
"""

import os
import sys
import warnings
import logging
import re
import toml
from string import Template
from utility.file_utils import find_file_in_paths

__all__ = ["ConfigurationException",
           "parse_configuration_files",
           "parse_configuration_file",
           "read_config_from_toml"]

logger = logging.getLogger(__name__)

try:
    TCFHOME = os.environ["TCF_HOME"]
except KeyError:
    raise KeyError("'TCF_HOME' environment variable not set.")


# -----------------------------------------------------------------
class ConfigurationException(Exception):
    """
    A class to capture configuration exceptions.
    """

    def __init__(self, filename, message):
        super().__init__(
            self, "Error in configuration file {0}: {1}".format(
                filename, message))


# -----------------------------------------------------------------
def parse_configuration_files(cfiles, search_path, variable_map=None):
    """
    Locate and parse a collection of configuration files stored in a
    TOML format.

    :param list(str) cfiles: list of configuration files to load
    :param list(str) search_path: list of directories where the files may
           be located
    :param dict variable_map: a set of substitutions for variables in the files
    :return dict:an aggregated dictionary of configuration information
    """
    config = {}
    files_found = []

    try:
        for cfile in cfiles:
            files_found.append(find_file_in_paths(cfile, search_path))
    except FileNotFoundError as e:
        raise ConfigurationException(e.filename, e.strerror)

    for filename in files_found:
        try:
            config.update(parse_configuration_file(filename, variable_map))
        except IOError as detail:
            raise ConfigurationException(
                filename, "IO error; {0}".format(str(detail)))
        except ValueError as detail:
            raise ConfigurationException(
                filename, "Value error; {0}".format(str(detail)))
        except NameError as detail:
            raise ConfigurationException(
                filename, "Name error; {0}".format(str(detail)))
        except KeyError as detail:
            raise ConfigurationException(
                filename, "Key error; {0}".format(str(detail)))
        except Exception as detail:
            raise ConfigurationException(
                filename, "Unknown error; {0}".format(str(detail)))

    return config

# -----------------------------------------------------------------
# -----------------------------------------------------------------


def parse_configuration_file(filename, variable_map):
    """
    Parse a configuration file expanding variable references
    using the Python Template library (variables are $var format)

    :param string filename: name of the configuration file
    :param dict variable_map: dictionary of expansions to use
    :returns dict: dictionary of configuration information
    """

    cpattern = re.compile('##.*$')

    with open(filename) as fp:
        lines = fp.readlines()

    text = ""
    for line in lines:
        text += re.sub(cpattern, '', line) + ' '

    if variable_map:
        text = Template(text).substitute(variable_map)

    return toml.loads(text)


# -----------------------------------------------------------------
def read_config_from_toml(input_file, config_name=None,
                          confpaths=[".", TCFHOME + "/" + "config"]):
    """
    Function to read toml file and returns the toml content as a list
    Parameters:
        - input_file is any toml file which need to be read
        - config_name is particular configuration to pull
        - confpaths is the directory structure in which the toml file exists
    """
    conf_files = [input_file]
    config = parse_configuration_files(conf_files, confpaths)
    if config_name is None:
        return config
    else:
        result = config.get(config_name)
        if result is None:
            logger.error(
                "%s is missing in toml file %s", config_name, input_file)
        return result
