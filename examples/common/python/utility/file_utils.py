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
file_utils.py -- file utility routines

NOTE: functions defined in this file are designed to be run
before logging is enabled.
"""

import os
import json
import errno
import logging

__all__ = [
           'find_file_in_paths',
           'read_json_file',
           'write_result_data_to_json_file'
          ]

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------
def find_file_in_paths(filename, search_paths):
    """General utility to search for a file name in a path

    :param str filename: name of the file to locate, absolute path ignores search_path
    :param list(str) search_path: list of directories where the files may be located
    """

    # os.path.abspath only works for full paths, not relative paths
    # This check should catch './abc'
    if os.path.split(filename)[0]:
        if os.path.isfile(filename):
            return filename
        raise FileNotFoundError(errno.ENOENT, "file does not exist", filename)

    for path in search_paths:
        full_filename = os.path.join(path, filename)
        if os.path.isfile(full_filename):
            return full_filename

    raise FileNotFoundError(errno.ENOENT, "unable to locate file in search path", filename)


# -----------------------------------------------------------------
def read_json_file(input_file, data_dir=['./', '../', '/']):
    """
    Utility function to read a JSON file
    """
    file_name = find_file_in_paths(input_file, data_dir)
    with open(file_name, "r") as input_json_file:
        input_lines = input_json_file.read().splitlines()
    return "".join(input_lines)


# -----------------------------------------------------------------------------
def write_result_data_to_json_file(file_name, input_data, data_dir='./'):
    """
    Function to store result data as json file
    Parameters:
        - file_name is the name in which the file should be stored
        - input_data is a JSON data which needs to be stored in a file( should have attribute 'result')
        - data_dir is the directory path to store the file
    """
    result_info = dict()
    try:
        result_info['Result'] = json.loads(input_data)['result']
    except:
        raise ValueError("Input data must have attribute 'result'")
    logger.debug('Data file is stored at %s with name %s.json', data_dir,
        file_name)
    extension = "" if file_name.lower().endswith(".json") else ".json"
    filename = os.path.realpath(os.path.join(data_dir, file_name + extension))
    logger.debug('Save result data to %s', filename)
    with open(filename, "w") as file:
        json.dump(result_info, file)
