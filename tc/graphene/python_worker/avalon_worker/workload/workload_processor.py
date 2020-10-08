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
import logging
import json
import importlib

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# -------------------------------------------------------------------------


class WorkLoadProcessor():
    """
    Graphene work load processing class.
    """

    def __init__(self, workload_json_file):
        """
        Constructor for work load processing class.

        Parameters :
            workloads_json_file: JSON file which has workload module details.
        """
        self.workload_json_file = workload_json_file
        # Create empty map of workload id and workload instance.
        # key: workload_id, value: workload class instance.
        self.workload_instance_map = dict()
        logger.info("Initialize Work load processor")

# -------------------------------------------------------------------------

    def execute_workload(self, workload_id, in_data_array):
        """
        Executes workloads based on workload id.

        Parameters :
            workload_id:  Workload ID to execute.
            in_data_array: Input data array containing data in plain bytes.
        Returns :
            status as boolean and outData dictionary.
        """
        wl_processor = self._create_workload_processor(workload_id)
        if not wl_processor:
            logger.error("unable to create workload processor")
            return False, None
        try:
            result, out_msg_bytes = wl_processor.execute(in_data_array)
            out_data = self._create_response_out_data(out_msg_bytes)
            return result, out_data
        except Exception as e:
            logger.error("Error executing workload: " + str(e))
            return False, None

# -------------------------------------------------------------------------

    def _create_workload_processor(self, workload_id):
        """
        Executes workloads based on workload id.

        Parameters :
            workload_id:  Workload id to execute.
            in_data_array: Input data array containing data in plain bytes.
        Returns :
            status as boolean and outData dictionary.
        """
        instance = None
        try:
            with open(self.workload_json_file, "rb") as file:
                workload_json = json.load(file)
        except Exception as e:
            logger.error("Work load processor creation failed" + str(e))
            return None

        if workload_id in workload_json:
            if "module" not in workload_json[workload_id]:
                err_msg = "Work load module not found in workloads.json"
                logger.error(err_msg)
                return None
            if "class" not in workload_json[workload_id]:
                err_msg = "Work load class not found in workloads.json"
                logger.error(err_msg)
                return None
            # Create a workload module class instance if it doesn't exist.
            if workload_id in self.workload_instance_map:
                instance = self.workload_instance_map[workload_id]
                if instance:
                    logger.debug("Use existing {} class instance".
                                 format(workload_id))
                    return instance
            try:
                module_name = workload_json[workload_id]["module"]
                class_name = workload_json[workload_id]["class"]
                module = importlib.import_module(module_name)
                class_ = getattr(module, class_name)
                instance = class_()
                logger.debug("Created new {} class instance".
                             format(workload_id))
                # Store the workload class instance in map.
                self.workload_instance_map[workload_id] = instance
            except Exception as e:
                logger.error("Work load processor creation failed: " + str(e))
                return None
        else:
            err_msg = "{} workload id not found".format(workload_id)
            logger.error(err_msg)
            return None

        return instance

# -------------------------------------------------------------------------

    def _create_response_out_data(self, out_data_plain_bytes):
        """
        Create output Work Order Data Format as per TC spec v1.1 section 6.5.

        Parameters :
            out_data_plain_bytes:  output data in plain bytes
        Returns :
            output Work Order Data Format as per TC spec v1.1 section 6.5.
        """
        out_data = dict()
        out_data["data"] = out_data_plain_bytes
        out_data["index"] = 0
        # Data hash is optional. Ignore it for now.
        # out_data["dataHash"] = ""
        out_data["encryptedDataEncryptionKey"] = "null"
        out_data["iv"] = ""
        return out_data

# -------------------------------------------------------------------------
