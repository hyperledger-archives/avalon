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

logger = logging.getLogger(__name__)


class WorkerEncryptionKeyLmdbHelper:
    """
    WorkerEncryptionKeyDBHelper helps listener or other client
    facing modules to interact with the kv storage for queries
    related to encryption key. It implements all low level db
    calls which aides in the logical flows for getting/setting
    encryption keys.
    """
# ------------------------------------------------------------------------------------------------

    def __init__(self, kv_helper):
        """
        Function to perform init activity
        Parameters:
            - kv_helper is a object of lmdb database
        """
        self.kv_helper = kv_helper

# ---------------------------------------------------------------------------------------------
    def get_worker_with_id(self, worker_id):
        """
        Function to get worker corresponding to supplied worker id
        Parameters:
            - worker_id: id of worker being looked for
        Returns worker corresponding to key
        """

        return self.kv_helper.get_worker("workers", worker_id)
