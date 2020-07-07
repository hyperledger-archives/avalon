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


class ZmqCommunication():
    """
    Class to communicate using ZMQ socket.
    """

    def __init__(self, zmq_url):
        """
        Constructor for ZMQ socket communication.

        Parameters :
            zmq_url:  ZMQ url used for communication.
        """
        self.zmq_url = zmq_url

# -------------------------------------------------------------------------

    def send_request_zmq(self, data):
        """
        Send request string via ZMQ and returns the response string.

        Parameters :
            data: Data request string send via ZMQ.
        Returns :
            Response string.
        """
        logger.info("Send request\n")
        try:
            self.socket.send_string(data, flags=0, encoding='utf-8')
            replymessage = self.socket.recv_string(flags=0, encoding='utf-8')
            logger.info(replymessage)
        except Exception as ex:
            logger.error("Error while sending request: " + str(ex))
            return None

        return replymessage

# -------------------------------------------------------------------------

    def connect(self):
        """
        Establish ZMQ socket communication channel.

        """
        try:
            self.zmq_context = zmq.Context()
            self.socket = self.zmq_context.socket(zmq.REQ)
            self.socket.connect(self.zmq_url)
        except Exception as ex:
            logger.error("Error establishing zmq channel: " + str(ex))
            raise

# -------------------------------------------------------------------------

    def disconnect(self):
        """
        Disconnect ZMQ communication channel.

        """
        try:
            # Disconnect socket if required.
            if self.socket:
                self.socket.disconnect(self.zmq_url)
            # Destroy zmq context if required.
            if self.zmq_context:
                self.zmq_context.destroy()
        except Exception as ex:
            logger.error("Error disconnecting zmq channel: " + str(ex))
            raise

# -------------------------------------------------------------------------
