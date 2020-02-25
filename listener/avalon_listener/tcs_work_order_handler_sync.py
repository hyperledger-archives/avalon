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

import time
import json
import logging
from error_code.error_status import WorkOrderStatus
from error_code.enclave_error import EnclaveError
from avalon_sdk.direct.jrpc.jrpc_util import JsonRpcErrorCode
from avalon_sdk.work_order.work_order_request_validator \
    import WorkOrderRequestValidator
from avalon_listener.tcs_work_order_handler import TCSWorkOrderHandler

from jsonrpc.exceptions import JSONRPCDispatchException

# ZeroMQ for sync workorder processing
import zmq
context = zmq.Context()
# -------------------------------------------

logger = logging.getLogger(__name__)

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


class TCSWorkOrderHandlerSync(TCSWorkOrderHandler):
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
    TCSWorkOrderHandlerSync derives from the TCSWorkOrderHandler
    and overrides the functions
    required for - Synchronous Work order execution.
    """
# ------------------------------------------------------------------------------------------------

    def __init__(self, kv_helper, max_wo_count, zmq_url, zmq_port):
        """
        Function to perform init activity
        Parameters:
            - kv_helper is a object of lmdb database
        """
        self.zmq_url = zmq_url
        self.zmq_port_number = zmq_port
        super(TCSWorkOrderHandlerSync, self).__init__(kv_helper, max_wo_count)

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
            work_orders = self.kv_helper.lookup("wo-timestamps")
            for id in work_orders:
                # If work order is processed then remove from table
                if(self.kv_helper.get("wo-processed", id) is not None):
                    self.kv_helper.remove("wo-processed", id)
                    self.kv_helper.remove("wo-requests", id)
                    self.kv_helper.remove("wo-responses", id)
                    self.kv_helper.remove("wo-receipts", id)
                    self.kv_helper.remove("wo-timestamps", id)

                    self.workorder_list.remove(id)
                    self.workorder_count -= 1
                    break

            # If no work order is processed then return busy
            if((self.workorder_count + 1) > self.max_workorder_count):
                raise JSONRPCDispatchException(
                    WorkOrderStatus.BUSY,
                    "Work order handler is busy updating the result")

        if(self.kv_helper.get("wo-timestamps", wo_id) is None):
            # Create a new work order entry.
            # Don't change the order of table updation.
            # The order is important for clean up if the TCS is restarted in
            # the middle.
            epoch_time = str(time.time())

            # Update the tables
            self.kv_helper.set("wo-timestamps", wo_id, epoch_time)
            self.kv_helper.set("wo-requests", wo_id, input_json_str)
            self.kv_helper.set("wo-scheduled", wo_id, input_json_str)
            # Add to the internal FIFO
            self.workorder_list.append(wo_id)
            self.workorder_count += 1
            # ZeroMQ for sync workorder processing
            try:
                socket = context.socket(zmq.REQ)
                socket.connect(self.zmq_url + self.zmq_port_number)
                socket.send_string(wo_id, flags=0, encoding='utf-8')
                replymessage = socket.recv()
                logger.info(replymessage)
                socket.disconnect(self.zmq_url + self.zmq_port_number)
                # Work order is processed. Fetch result from wo-respose table
                value = self.kv_helper.get("wo-responses", wo_id)
                if value:
                    response = json.loads(value)
                    if 'result' in response:
                        return response['result']

                    # response without result should have an error
                    # return error
                    err_code = response["error"]["code"]
                    err_msg = response["error"]["message"]
                    if err_code == EnclaveError.ENCLAVE_ERR_VALUE:
                        err_code = \
                            WorkOrderStatus.INVALID_PARAMETER_FORMAT_OR_VALUE
                    elif err_code == EnclaveError.ENCLAVE_ERR_UNKNOWN:
                        err_code = WorkOrderStatus.UNKNOWN_ERROR
                    else:
                        err_code = WorkOrderStatus.FAILED
                    raise JSONRPCDispatchException(err_code, err_msg)
            except Exception as er:
                raise JSONRPCDispatchException(
                    WorkOrderStatus.UNKNOWN_ERROR,
                    "Failed to connect with enclave-manager socket: " + er)

        # Workorder id already exists
        raise JSONRPCDispatchException(
            WorkOrderStatus.INVALID_PARAMETER_FORMAT_OR_VALUE,
            "Work order id already exists in the database. \
                Hence invalid parameter")

# ---------------------------------------------------------------------------------------------
