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
# ------------------------------------------------------------------------------

import os
import unittest
from utility.file_utils import (
    write_result_data_to_json_file,
    find_file_in_paths,
    read_json_file,
)

FILE_PATH = "./test_file_utils"


class FileUtilsTest(unittest.TestCase):
    def test_find_file_in_paths(self):
        """Tests to verify file_in_path(filename, search_paths) function
        """
        self.assertEqual(FILE_PATH + "/path_test_file",
                         find_file_in_paths("path_test_file", [FILE_PATH]))
        self.assertEqual(FILE_PATH + "/path_test_file",
                         find_file_in_paths("path_test_file",
                                            ["./", FILE_PATH]))
        pwd = os.getcwd()
        os.chdir(FILE_PATH)
        self.assertEqual("./path_test_file",
                         find_file_in_paths("./path_test_file", ["./"]))
        self.assertEqual("./path_test_file",
                         find_file_in_paths("path_test_file", ["./"]))
        os.chdir(pwd)
        self.assertRaises(FileNotFoundError, find_file_in_paths,
                          "path_test_file", ["./"])

    def test_read_json_file(self):
        """Tests to verify read_json_file(input_file,data_dir) function
        """
        input_json = read_json_file(
            "sample1.json", [FILE_PATH])  # positive case
        self.assertEqual(input_json, '{"field1": 1,"field2": 2}')

        input_json = read_json_file(
            "sample2.json", [FILE_PATH])  # positive case
        self.assertEqual(input_json, '{"field1":1,"field2":2}')

        input_json = read_json_file(
            "sample3.json", [FILE_PATH])  # positive case
        self.assertEqual(input_json,
                         '{1:"one",2:"two",3:["one","two","three"]}')

    def test_write_result_data_to_json_file(self):
        """Tests to verify function
           write_result_data_to_json_file(file_name,input_data, data_dir ='./')
        """
        input_data = '{"result":1,"field2":2}'
        file_name = "write_sample.json"
        write_result_data_to_json_file(file_name, input_data)
        read_json = read_json_file(
            "write_sample.json", ["./"])  # with extension case
        self.assertEqual('{"Result": 1}', read_json)
        try:
            os.remove(file_name)
        except OSError:
            pass

        file_name = "write_sample"
        write_result_data_to_json_file(file_name, input_data)
        read_json = read_json_file(
            "write_sample.json", ["./"])  # positive case
        self.assertEqual('{"Result": 1}', read_json)
        try:
            os.remove(file_name + ".json")
        except OSError:
            pass

        input_data = '{"field1":1,"field2":2}'  # No attribute 'result'
        file_name = "write_sample.json"
        self.assertRaises(ValueError, write_result_data_to_json_file,
                          file_name, input_data)
