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

import logging
import os

from database.lmdb_helper_proxy import LMDBHelperProxy

logger = logging.getLogger(__name__)


def open(uri):
    """
    @dev open implements a generic API for opening connections to a LMDB
        database where it's local or remote
    @return (conn, type), where
        - conn is the connection helper to interact with db
        - type is 1 for the local LMDB, 2 for the remote LMDB
    """

    if uri is None:
        raise ValueError("lmdb data store uri missing")

    # employ the remote version if remote_url is set
    logger.info(f"connect to remote LMDB @{uri}")
    return LMDBHelperProxy(uri)
