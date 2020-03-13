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


class WorkerRegistryLmdbHelper:
    """
    WorkerRegistryDBHelper helps listener or other client facing modules
    to interact with the kv storage for queries related to worker registry.
    """
# ------------------------------------------------------------------------------------------------

    def __init__(self, kv_helper):
        """
        Function to perform init activity
        Parameters:
            - kv_helper is a object of lmdb database
        """

        self.kv_helper = kv_helper
# ------------------------------------------------------------------------------------------------

    def get_worker_with_id(self, worker_id):
        """
        Function to get worker corresponding to supplied worker id
        Parameters:
            - worker_id: id of worker being looked for
        Returns worker corresponding to key
        """
        return self.kv_helper.get("workers", worker_id)

# ------------------------------------------------------------------------------------------------

    def save_worker(self, worker_id, worker_details):
        """
        Function to save a worker with given id and details
        Parameters:
            - worker_id: id of worker to be saved
            - worker_details: Details of worker to be saved
        """
        self.kv_helper.set("workers", worker_id, worker_details)

# ------------------------------------------------------------------------------------------------
    def get_all_workers(self):
        """
        Function to retrieve all workers from database
        Returns a list of all workers in the 'workers' table
        """
        return self.kv_helper.lookup("workers")
# ------------------------------------------------------------------------------------------------

    def cleanup_registries(self):
        """
        Function to clean up all registries from the database
        """
        organisation_id = self.kv_helper.lookup("registries")
        for o_id in organisation_id:
            self.kv_helper.remove("registries", o_id)
# ------------------------------------------------------------------------------------------------

    def save_registry(self, reg_id, registry_details):
        """
        Function to save/create a new registry in the database
        Parameters:
            - reg_id: Id of registry to be saved/updated
            - registry_details: Details of new/updated registry
        """
        return self.kv_helper.set("registries", reg_id, registry_details)
