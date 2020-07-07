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
import zmq
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# -------------------------------------------------------------------------


class ZmqSocket():
    """
    ZMQ socker to receive Work Order Request and send Response.
    """

# -------------------------------------------------------------------------

    def __init__(self, zmq_url, wo_processor):
        """
        Constructor for ZmqSocket.
        """
        self.wo_processor = wo_processor
        self.zmq_url = zmq_url

# -------------------------------------------------------------------------

    def start_zmq_listener(self):
        """
        This function binds to the port configured for zmq and
        then indefinitely processes work order requests received
        over the zmq connection. It terminates only when an
        exception occurs.
        """
        # Binding with ZMQ Port
        try:
            context = zmq.Context()
            socket = context.socket(zmq.REP)
            socket.bind(self.zmq_url)
            logger.info("Bind to zmq port")
        except Exception as ex:
            logger.exception("Failed to bind socket" +
                             "shutting down: " + str(ex))
        # Process requests
        while True:
            try:
                # Wait for the next request
                logger.info("waiting for next request")
                msg = socket.recv_string(flags=0, encoding='utf-8')
                logger.info("Received request: {}".format(msg))
                result = self.wo_processor.process_work_order(msg)
                if result:
                    logger.info("Sent response: {}".format(result))
                    socket.send_string(result, flags=0, encoding='utf-8')
                else:
                    msg = "Work order result is empty"
                    logger.info("Sent response: {}".format(msg))
                    socket.send_string(msg, flags=0, encoding='utf-8')
            except Exception as ex:
                logger.error("Error while processing work-order: " + str(ex))
                break

# -------------------------------------------------------------------------
