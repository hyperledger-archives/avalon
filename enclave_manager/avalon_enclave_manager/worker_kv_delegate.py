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
import hashlib


logger = logging.getLogger(__name__)


class WorkerKVDelegate:
    """
    Delegate class for enclave managers to make worker
    specific changes in the KV storage.
    """

    def __init__(self, kv_helper):
        self._kv_helper = kv_helper

    def cleanup_worker(self, worker_ids=None):
        """
        Remove workers(if any found) from the KV Store
        Parameters :
            worker_ids - List of Worker id to be cleaned up. By default
            all will be cleaned up
        Returns :
            True - If all workers are removed successfully
            False - Otherwise
        """
        # @TODO : Enable cleanup for worker_ids passed in argument.
        # As of now a blanket cleanup is being done.
        workers_list = self._kv_helper.lookup("workers")

        result = True
        if len(workers_list) == 0:
            logger.info("No worker entries available in workers table; " +
                        "skipping cleanup")
            return True
        else:
            logger.info("Clearing entries in workers table")
            for worker in workers_list:
                result &= self._kv_helper.remove("workers", worker)
        return result

    def add_new_worker(self, worker_id, worker_info):
        """
        Add a new worker to the KV Store

        Parameters :
            worker_id - Id of the worker to be added
            worker_info - Serialized JSON of the worker details

        Returns :
            True - If worker is added successfully
            False - Otherwise
        """
        logger.info("Adding enclave workers to workers table")

        return self._kv_helper.set("workers", worker_id, worker_info)
