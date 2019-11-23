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
import time
import logging
from utility.hex_utils import is_valid_hex_str
from service_client.generic import GenericServiceClient
from connectors.interfaces.work_order_interface import WorkOrderInterface
from connectors.utils import create_jrpc_response
from utility.tcf_types import JsonRpcErrorCode
from error_code.error_status import WorkOrderStatus

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class WorkOrderJRPCImpl(WorkOrderInterface):
    def __init__(self, config):
        self.__uri_client = GenericServiceClient(config["tcf"]["json_rpc_uri"])

    def work_order_submit(self, params, in_data, out_data=None, id=None):
        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkOrderSubmit",
            "id": id
        }
        json_rpc_request["params"] = params
        json_rpc_request["params"]["inData"] = in_data

        if out_data is not None:
            json_rpc_request["params"]["outData"] = out_data

        logging.debug("Work order request %s", json.dumps(json_rpc_request))
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    def work_order_get_result_nonblocking(self, work_order_id, id=None):
        """
        Get the work order result in non-blocking way.
        It return json rpc response of dictionary type
        """
        if not is_valid_hex_str(work_order_id):
            logging.error("Invalid work order Id")
            return create_jrpc_response(id, JsonRpcErrorCode.INVALID_PARAMETER,
                "Invalid work order Id")

        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "WorkOrderGetResult",
            "id": id,
            "params": {
                "workOrderId": work_order_id
            }
        }
        response = self.__uri_client._postmsg(json.dumps(json_rpc_request))
        return response

    def work_order_get_result(self, work_order_id, id=None):
        """
        Get the work order result in blocking way until it get the result/error
        It return json rpc response of dictionary type
        """
        response = self.work_order_get_result_nonblocking(work_order_id, id)
        if "error" in response:
            if response["error"]["code"] != WorkOrderStatus.PENDING:
                return response
            else:
                while "error" in response and \
                        response["error"]["code"] == WorkOrderStatus.PENDING:
                    response = self.work_order_get_result_nonblocking(work_order_id, id)
                    # TODO: currently pooling after every 2 sec interval forever.
                    # We should implement feature to timeout after responseTimeoutMsecs in the request
                    time.sleep(2)
                return response
