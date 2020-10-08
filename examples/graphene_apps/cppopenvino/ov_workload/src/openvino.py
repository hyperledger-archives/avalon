#!/usr/bin/python3

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

import os
import sys
import logging
import json
import toml
from avalon_worker.workload.workload import WorkLoad
from avalon_worker.utility.zmq_comm import ZmqCommunication

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# -------------------------------------------------------------------------


class OpenVinoWorkLoad(WorkLoad):
    """
    OpenVino workload class. This is an example workload.
    """
    def __init__(self):
        """
        Constructor for OpenVinoWorkLoad.
        """
        # Zmq socket used for communicating with Openvino C++ workload.
        # Read zmq url from config file.
        try:
            dir_path = os.path.dirname(os.path.abspath(__file__))
            toml_file = os.path.join(dir_path, "ov_workload_config.toml")
            config = toml.load(toml_file)
        except Exception as e:
            logger.error("Unable to read ov_workload_config.toml" + str(e))
            raise
        zmq_url = config.get("zmq_url")
        self.zmq_socket = ZmqCommunication(zmq_url)
        self.zmq_socket.connect()
        super().__init__()

# -------------------------------------------------------------------------

    def execute(self, in_data_array):
        """
        Executes OpenVino workload.

        Parameters :
            in_data_array: Input data array containing data in plain bytes
        Returns :
            status as boolean and output result in bytes.
        """
        logger.info("Execute OpenVino workload")
        data_plain_bytes = in_data_array[0]["data"]
        try:
            data_str = data_plain_bytes.decode("UTF-8")
            json_request = {}
            json_request["workloadId"] = "ov-inference"
            json_request["params"] = data_str
            out_msg = self.zmq_socket.send_request_zmq(
                                            json.dumps(json_request))
            out_msg_bytes = out_msg.encode("utf-8")
            result = True
        except Exception as e:
            out_msg = "Error processing OpenVino workload : " + str(e)
            out_msg_bytes = out_msg.encode("utf-8")
            logger.error(out_msg)
            result = False

        return result, out_msg_bytes

# -------------------------------------------------------------------------
