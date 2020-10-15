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
import logging
from avalon_worker.base_work_order_processor import BaseWorkOrderProcessor

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# -------------------------------------------------------------------------


class WPEWorkOrderProcessor(BaseWorkOrderProcessor):
    """
    Graphene work order processing class.
    """

# -------------------------------------------------------------------------

    def __init__(self, workload_json_file):
        super().__init__(workload_json_file)

# -------------------------------------------------------------------------

    def _process_work_order(self, input_json_str):
        """
        Process Avalon work order and returns JSON RPC response

        Parameters :
            input_json_str: JSON formatted work order request string.
                            work order JSON is formatted as per
                            TC spec ver 1.1 section 6.
        Returns :
            JSON RPC response containing result or error.
        """
        pass

# -------------------------------------------------------------------------

    def _encrypt_and_sign_response(self, session_key,
                                   session_key_iv, output_json):
        """
        Encrypt outdata and compute worker signature.

        Parameters :
            session_key: Session key of the client which submitted
                        this work order
            session_key_iv: iv corresponding to teh session key
            output_json: Pre-populated response json
        Returns :
            JSON RPC response with worker signature

        """
        pass

# -------------------------------------------------------------------------


main()
