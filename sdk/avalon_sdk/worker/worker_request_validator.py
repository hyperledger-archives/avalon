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

from utility.hex_utils import is_valid_hex_str


class WorkerRequestValidator():
    """
    WorkerRequestValidator validates worker related requests
    for proper parameter fields and valid data formats.
    """
    def __init__(self):
        """
        Initialize __param_key_map and __value_key_map,
        which are key-value pairs.
        The key is the field name and value is a boolean that
        indicates whether a field is mandatory (True) or optional (False).
        """
        self.__lookup_param_key_map = {
            "workerType": False,
            "organizationId": False,
            "applicationTypeId": False}

        self.__lookup_next_param_key_map = {
            "workerType": False,
            "organizationId": False,
            "applicationTypeId": False,
            "lookUpTag": False}

    def worker_lookup_validation(self, params):
        """
        Validate params dictionary for existence of
        fields and mandatory fields

        Parameters:
        params    Parameter dictionary to validate

        Returns:
        True and empty string on success and
        False and string with error message on failure.
        """
        if len(params) == 0:
            return False, "Empty params in the request"

        key_list = []
        for key in params.keys():
            if key not in self.__lookup_param_key_map.keys():
                return False, "Invalid parameter {}".format(key)
            else:
                key_list.append(key)

        if "workerType" in params.keys() and \
                type(params["workerType"]) != int:
            return False, "Invalid data format for workerType"

        if "organizationId" in params.keys() and \
                not is_valid_hex_str(params["organizationId"]):
            return False, "Invalid data format for organizationId"

        if "applicationTypeId" in params.keys() and \
                not is_valid_hex_str(params["applicationTypeId"]):
            return False, "Invalid data format for applicationTypeId"

        return True, ""

    def worker_lookup_next_validation(self, params):
        """
        Validate params dictionary for existence of
        fields and mandatory fields

        Parameters:
        params    Parameter dictionary to validate

        Returns:
        True and empty string on success and
        False and string with error message on failure.
        """

        if len(params) == 0:
            return False, "Empty params in the request"

        key_list = []
        for key in params.keys():
            if key not in self.__lookup_next_param_key_map.keys():
                return False, "Invalid parameter {}".format(key)
            else:
                key_list.append(key)

        if "workerType" in params.keys() and \
                type(params["workerType"]) != int:
            return False, "Invalid data format for workerType"

        if "organizationId" in params.keys() and \
                not is_valid_hex_str(params["organizationId"]):
            return False, "Invalid data format for organizationId"

        if "applicationTypeId" in params.keys() and \
                not is_valid_hex_str(params["applicationTypeId"]):
            return False, "Invalid data format for applicationTypeId"

        if "lookUpTag" in params.keys() and \
                type(params["lookUpTag"]) != str:
            return False, "Invalid data format for lookUpTag"

        return True, ""

    def worker_retrieve_validation(self, params):
        """
        Validate params dictionary for existence of
        fields and mandatory fields

        Parameters:
        params    Parameter dictionary to validate

        Returns:
        True and empty string on success and
        False and string with error message on failure.
        """
        if len(params) == 0:
            return False, "Worker Id not found"

        for key in params.keys():
            if key not in "workerId":
                return False, "Invalid parameter {}".format(key)

        if params["workerId"] == "" or \
                not is_valid_hex_str(params["workerId"]):
            return False, "Invalid data format for Worker id"

        return True, ""
