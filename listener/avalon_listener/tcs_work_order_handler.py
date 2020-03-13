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

import json
import logging
from error_code.error_status import WorkOrderStatus
from error_code.enclave_error import EnclaveError
from avalon_sdk.direct.jrpc.jrpc_util import JsonRpcErrorCode
from avalon_sdk.work_order.work_order_request_validator \
    import WorkOrderRequestValidator
from utility.hex_utils import is_valid_hex_str
from connectors.common.db_helper.work_order_lmdb_helper \
    import WorkOrderLmdbHelper

from jsonrpc.exceptions import JSONRPCDispatchException

logger = logging.getLogger(__name__)

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


class TCSWorkOrderHandler:
    """
    TCSWorkOrderHandler processes Worker Order Direct API requests. It puts a
    new work order requests into the KV storage or it reads appropriate work
    order information from the KV storage when processing “getter” and
    enumeration requests. Actual work order processing is done by the SGX
    Enclave Manager within the enclaves its manages.
    All raised exceptions will be caught and handled by any
    jsonrpc.dispatcher.Dispatcher delegating work to this handler. In our case,
    the exact dispatcher will be the one configured by the TCSListener in the
    ./tcs_listener.py
    """
# ------------------------------------------------------------------------------------------------

    def __init__(self, kv_helper, max_wo_count):
        """
        Function to perform init activity
        Parameters:
            - kv_helper is a object of lmdb database
        """

        self.db_helper = WorkOrderLmdbHelper(kv_helper)
        self.workorder_count = 0
        self.max_workorder_count = max_wo_count
        self.workorder_list = []

        self.__work_order_handler_on_boot()

# ---------------------------------------------------------------------------------------------
    def __work_order_handler_on_boot(self):
        """
        Function to perform on-boot process of work order handler
        """

        self.workorder_list, self.workorder_count = \
            self.db_helper.cleanup_hindered_wo()

    # ---------------------------------------------------------------------------------------------
    def WorkOrderGetResult(self, **params):
        """
        Function to process work order get result
        This API corresponds to TCF API 6.1.4 Work Order Pull Request Payload
        Parameters:
            - params is variable-length arugment list containing work request
              as defined in EEA spec 6.1.4
        Returns jrpc response as defined in EEA spec 6.1.2
        """
        wo_id = params["workOrderId"]
        if not is_valid_hex_str(wo_id):
            logging.error("Invalid work order Id")
            raise JSONRPCDispatchException(
                JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid work order Id"
            )
        return self.db_helper.get_wo_result(wo_id)

# ---------------------------------------------------------------------------------------------
    def WorkOrderSubmit(self, **params):
        """
        Function to process work order request
        Parameters:
            - params is variable-length arugment list containing work request
              as defined in EEA spec 6.1.1
        Returns jrpc response as defined in EEA spec 6.1.3
        """

        wo_id = params["workOrderId"]
        input_json_str = params["raw"]
        input_value_json = json.loads(input_json_str)

        req_validator = WorkOrderRequestValidator()
        valid, err_msg = req_validator.validate_parameters(
            input_value_json["params"])
        if not valid:
            raise JSONRPCDispatchException(
                JsonRpcErrorCode.INVALID_PARAMETER,
                err_msg
            )

        if "inData" in input_value_json["params"]:
            valid, err_msg = req_validator.validate_data_format(
                input_value_json["params"]["inData"])
            if not valid:
                raise JSONRPCDispatchException(
                    JsonRpcErrorCode.INVALID_PARAMETER,
                    err_msg)
        else:
            raise JSONRPCDispatchException(
                JsonRpcErrorCode.INVALID_PARAMETER,
                "Missing inData parameter"
            )

        if "outData" in input_value_json["params"]:
            valid, err_msg = req_validator.validate_data_format(
                input_value_json["params"]["outData"])
            if not valid:
                raise JSONRPCDispatchException(
                    JsonRpcErrorCode.INVALID_PARAMETER,
                    err_msg)

        if((self.workorder_count + 1) > self.max_workorder_count):

            # if max count reached clear a processed entry
            removed_wo = self.db_helper.clear_a_processed_wo()
            if(removed_wo is not None):
                self.workorder_list.remove()
                self.workorder_count -= 1

            # If no work order is processed then return busy
            if((self.workorder_count + 1) > self.max_workorder_count):
                raise JSONRPCDispatchException(
                    WorkOrderStatus.BUSY,
                    "Work order handler is busy updating the result")

        self.db_helper.submit_wo(wo_id, input_json_str)

# ---------------------------------------------------------------------------------------------
