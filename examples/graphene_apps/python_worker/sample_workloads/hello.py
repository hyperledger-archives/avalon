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
import sys
import logging
from avalon_worker.workload.workload import WorkLoad

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# -------------------------------------------------------------------------


class HelloWorkLoad(WorkLoad):
    """
    Hello workload class. This is an example workload.
    """

# -------------------------------------------------------------------------

    def execute(self, in_data_array):
        """
        Executes Hello workload.

        Parameters :
            in_data_array: Input data array containing data in plain bytes
        Returns :
            status as boolean and output result in bytes.
        """
        logger.info("Execute Hello workload")
        data_plain_bytes = in_data_array[0]["data"]
        try:
            data_str = data_plain_bytes.decode("UTF-8")
            out_msg = "Hello " + data_str
            out_msg_bytes = out_msg.encode("utf-8")
            result = True
        except Exception as e:
            out_msg = "Error processing Hello workload : " + str(e)
            out_msg_bytes = out_msg.encode("utf-8")
            logger.error(out_msg)
            result = False

        return result, out_msg_bytes

# -------------------------------------------------------------------------
