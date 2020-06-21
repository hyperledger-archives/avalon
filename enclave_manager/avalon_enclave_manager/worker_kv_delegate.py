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

import json
import time
import logging
import hashlib
import avalon_sdk.worker.worker_details as worker_details


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

    def cleanup_pool(self, worker_id):
        """
        Remove worker pool mapping from datastore. All workers need to
        register afresh to be a part of the pool.

        Parameters:
            @param worker_id - Id of worker representing the pool.
        """
        logger.info("Clearing worker pool mapping for %s", worker_id)
        return self._kv_helper.remove("worker-pool", worker_id)

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

    def get_worker_by_id(self, worker_id):
        """
        Get worker instance from database
        Parameters :
            @param worker_id - Id of worker to be retrieved
        Returns :
            @returns worker_obj - A worker retrieved from kv storage
        """
        worker_from_kv = None
        # Retry infinitely if worker is not found in KV storage
        while True:
            worker_from_kv = self._kv_helper.get("workers", worker_id)
            if worker_from_kv is None:
                logger.warn(
                    "Could not find worker in database. Will retry in 10s")
                time.sleep(10)
            else:
                break
        json_dict = json.loads(worker_from_kv)
        worker_obj = worker_details.SGXWorkerDetails()
        worker_obj.load_worker(json_dict['details'])

        return worker_obj

    def update_worker_map(self, worker_id, identity):
        """
        Function to register a worker in database. It effectively adds a
        new entry in the mapping of worker_id to workers in that pool.
        For a Singleton worker, this mapping is worker_id->worker_id. On
        the other hand, it is worker_id->enclave_id1,enclave_id2... (A
        list of enclave_id representing each WPE in the pool represented
        by worker_id).

        Parameters:
            @param worker_id - Worker id of the pool/singleton
            @param identity - worker_id of Singleton or enclave_id of a WPE
        """
        self._kv_helper.csv_append("worker-pool", worker_id, identity)
