#!/usr/bin/env python3

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
from listener.base_jrpc_listener import BaseJRPCListener

logger = logging.getLogger(__name__)


class KMEListener(BaseJRPCListener):
    """
    Listener to handle requests from WorkerProcessingEnclave(WPE)
    """

    # The isLeaf instance variable describes whether a resource will have
    # children and only leaf resources get rendered. KMEListener is a leaf
    # node in the derivation tree and hence isLeaf is required.
    isLeaf = True

    def __init__(self, rpc_methods):
        """
        Constructor for KMEListener. Pass through the rpc methods to the
        constructor of the BaseJRPCListener.
        Parameters :
            rpc_methods - An array of RPC methods to which requests will
                          be dispatched.
        """
        super().__init__(rpc_methods)
