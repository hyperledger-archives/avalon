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
import os
import subprocess
import zmq
import json
import logging
import toml

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# -------------------------------------------------------------------------


# This is a test file to send work order.
def main(argv):
    if len(argv) >= 1:
        workload = argv[0]
    else:
        workload = None

    if len(argv) >= 2:
        params = argv[1]
    else:
        params = None

    # Read zmq url from config file.
    try:
        config = toml.load("test_config.toml")
    except Exception as e:
        logger.error("Unable to read test_config.toml" + str(e))
        sys.exit(1)
    zmq_url = config.get("zmq_url")
    if zmq_url is None:
        logger.error("Zmq url is not set in test_config.toml")
        sys.exit(1)
    req = {}
    req["workloadId"] = workload
    req["params"] = params
    logger.info("Send work order request: {}".format(json.dumps(req)))
    context = zmq.Context()
    _send_request_zmq(context, zmq_url, json.dumps(req))

# -------------------------------------------------------------------------


def _send_request_zmq(context, zmq_url, workload):
    """
    Send workload via ZMQ and returns the response string.

    @param zmq_url zmq url to send workload.
    @param workload workload id.
    @return Response string.
    """
    try:
        socket = context.socket(zmq.REQ)
        socket.connect(zmq_url)
        socket.send_string(workload, flags=0, encoding='utf-8')
        replymessage = socket.recv_string()
        logger.info(replymessage)
        socket.disconnect(zmq_url)
    except Exception as ex:
        logger.error("Error while processing work-order")
        logger.error("Exception: {} args {} details {}"
                     .format(type(ex), ex.args, ex))
        exit(1)

# -------------------------------------------------------------------------


if __name__ == '__main__':
    main(sys.argv[1:])
