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
import base64
from utility.hex_utils import is_valid_hex_str
import crypto_utils.crypto.crypto as crypto
from error_code.error_status import ReceiptCreateStatus, SignatureStatus,\
    JRPCErrorCodes
import crypto_utils.signature as signature
from jsonrpc.exceptions import JSONRPCDispatchException

logger = logging.getLogger(__name__)


class TCSWorkOrderReceiptHandler:
    """
    TCSWorkOrderReceiptHandler processes Work Order Receipt Direct API
    requests. It reads appropriate work order information from the
    KV storage to create the response.
    Work order receipts are created and placed in the KV storage by the
    SGX Enclave Manager after the work order (successfully) completed.
    """
# -----------------------------------------------------------------------------

    def __init__(self, kv_helper):
        """
        Function to perform init activity
        Parameters:
            - kv_helper is a object of lmdb database
        """

        self.kv_helper = kv_helper
        self.__workorder_receipt_on_boot()
        # Special index 0xFFFFFFFF value to fetch last update to receipt
        self.LAST_RECEIPT_INDEX = 1 << 32
        # Supported hashing and signing algorithms
        self.SIGNING_ALGORITHM = "SECP256K1"
        self.HASHING_ALGORITHM = "SHA-256"

# -----------------------------------------------------------------------------

    def __workorder_receipt_on_boot(self):
        """
        Function to perform on-boot process of work order handler
        """
        # TODO: Boot time flow need to be implemented.
        pass

# -----------------------------------------------------------------------------

    def WorkOrderReceiptCreate(self, **params):
        """
        Function to process work order request
        Parameters:
            - params is variable-length arugment list containing work request
            as defined in EEA spec 7.2.2
        Returns jrpc response as defined in 4.1
        """
        wo_id = params["workOrderId"]
        input_json_str = params["raw"]
        input_value = json.loads(input_json_str)

        wo_request = self.kv_helper.get("wo-requests", wo_id)
        if wo_request is None:
            raise JSONRPCDispatchException(
                JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                "Work order id does not exist, "
                "hence invalid request"
            )
        else:
            wo_receipt = self.kv_helper.get("wo-receipts", wo_id)
            if wo_receipt is None:
                status, err_msg = \
                    self.__validate_work_order_receipt_create_req(
                        input_value, wo_request)
                if status is True:
                    self.kv_helper.set("wo-receipts", wo_id, input_json_str)
                    raise JSONRPCDispatchException(
                        JRPCErrorCodes.SUCCESS,
                        "Receipt created successfully"
                    )
                else:
                    raise JSONRPCDispatchException(
                        JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                        err_msg
                    )
            else:
                raise JSONRPCDispatchException(
                    JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                    "Work order receipt already exists. " +
                    "Hence invalid parameter"
                )

# -----------------------------------------------------------------------------

    def __validate_work_order_receipt_create_req(self, wo_receipt_req,
                                                 wo_request):
        """
        Function to validate the work order receipt create request parameters
        Parameters:
            - wo_receipt_req is work order receipt request as dictionary
            - wo_request is string containing jrpc work order request
        Returns - tuple containing validation status(Boolean) and
                  error message(string)
        """
        # Valid parameters list
        valid_params = [
            "workOrderId", "workerServiceId", "workerId",
            "requesterId", "receiptCreateStatus", "workOrderRequestHash",
            "requesterGeneratedNonce", "requesterSignature", "signatureRules",
            "receiptVerificationKey"]
        for key in wo_receipt_req["params"]:
            if key not in valid_params:
                return False, "Missing parameter " + key + " in the request"
            else:
                if key in ["workOrderId", "workerServiceId", "workerId",
                           "requesterId", "requesterGeneratedNonce"]:
                    if not is_valid_hex_str(wo_receipt_req["params"][key]):
                        return False, "invalid data parameter for " + key
                elif key in ["workOrderRequestHash", "requesterSignature"]:
                    try:
                        base64.b64decode(wo_receipt_req["params"][key])
                    except Exception as e:
                        return False, \
                            "Invalid data format for " + key
        receipt_type = wo_receipt_req["params"]["receiptCreateStatus"]
        try:
            receipt_enum_type = ReceiptCreateStatus(receipt_type)
        except Exception as err:
            return False, "Invalid receipt status type {}: {}".format(
                receipt_enum_type, str(err))

        # Validate signing rules
        signing_rules = wo_receipt_req["params"]["signatureRules"]
        rules = signing_rules.split("/")
        if len(rules) == 2 and (rules[0] != self.HASHING_ALGORITHM or
                                rules[1] != self.SIGNING_ALGORITHM):
            return False, "Unsupported the signing rules"

        signature_obj = signature.ClientSignature()
        # Verify work order request is calculated properly or not.
        wo_req_hash = \
            signature_obj.calculate_request_hash(json.loads(wo_request))
        if wo_req_hash != wo_receipt_req["params"]["workOrderRequestHash"]:
            return False, "Work order request hash does not match"
        # Verify requester signature with signing key in the request
        status = signature_obj.verify_create_receipt_signature(wo_receipt_req)
        if status != SignatureStatus.PASSED:
            return False, "Receipt create requester signature does not match"
        # If all parameters are verified in the request
        return True, ""

# -----------------------------------------------------------------------------

    def WorkOrderReceiptUpdate(self, **params):
        """
        Function to process update work order request
        Parameters:
            - params is variable-length arugment list containing work request
              as defined in EEA spec 7.2.3
        Returns jrpc response as defined in 4.1
        """

        wo_id = params["workOrderId"]
        input_json_str = params["raw"]
        input_value = json.loads(input_json_str)

        # Check if receipt for work order id is created or not
        value = self.kv_helper.get("wo-receipts", wo_id)

        if value:
            # Receipt is created, validate update receipt request
            status, err_msg = self.__validate_work_order_receipt_update_req(
                input_value)
            if status is True:
                # Load previous updates to receipt
                updates_to_receipt = \
                    self.kv_helper.get("wo-receipt-updates", wo_id)
                # If it is first update to receipt
                if updates_to_receipt is None:
                    updated_receipt = []
                else:
                    updated_receipt = json.loads(updates_to_receipt)
                # Get last update to receipt
                last_update = updated_receipt[len(updated_receipt) - 1]
                if last_update["updateType"] == \
                        ReceiptCreateStatus.COMPLETED.value:
                    raise JSONRPCDispatchException(
                        JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                        "Receipt update status is set to completed, "
                        "No further update allowed"
                    )
                # If last update to receipt is processed then below status
                # are invalid
                if last_update["updateType"] == \
                        ReceiptCreateStatus.PROCESSED.value:
                    if input_value["params"]["updateType"] in [
                        ReceiptCreateStatus.PENDING.value,
                        ReceiptCreateStatus.FAILED.value,
                        ReceiptCreateStatus.REJECTED.value
                    ]:
                        raise JSONRPCDispatchException(
                            JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                            "Current receipt status is set to processed, "
                            "setting it to status " +
                            str(input_value["params"]["updateType"]) +
                            " is not allowed"
                        )
                updated_receipt.append(input_value)
                self.kv_helper.set("wo-receipt-updates", wo_id,
                                   json.dumps(updated_receipt))
                raise JSONRPCDispatchException(
                    JRPCErrorCodes.SUCCESS,
                    "Receipt updated successfully"
                )
            else:
                # Receipt update request validation failed
                raise JSONRPCDispatchException(
                    JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                    err_msg
                )
        else:
            # Receipt for the work order is not created yet
            # Throw an exception
            raise JSONRPCDispatchException(
                JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                "Work order receipt with id {} is not created yet, "
                "hence invalid parameter".format(
                    wo_id
                )
            )

# -----------------------------------------------------------------------------

    def __validate_work_order_receipt_update_req(self, wo_receipt_req):
        """
        Function to validate the work order receipt create request parameters
        Parameters:
                - wo_receipt_req is work order receipt request as dictionary
        Returns - tuple containing validation status(Boolean) and error
                  message(string)
        """
        valid_params = ["workOrderId", "updaterId", "updateType", "updateData",
                        "updateSignature", "signatureRules",
                        "receiptVerificationKey"]
        for key in wo_receipt_req["params"]:
            if key not in valid_params:
                return False, "Missing parameter " + key + " in the request"
            else:
                if key in ["workOrderId", "updaterId"]:
                    if not is_valid_hex_str(wo_receipt_req[key]):
                        return False, "invalid data parameter for " + key
                elif key in ["updateData", "updateSignature"]:
                    try:
                        base64.b64decode(wo_receipt_req[key])
                    except Exception:
                        return False, "Invalid data format for " + key
        update_type = wo_receipt_req["params"]["updateType"]
        try:
            update_enum_value = ReceiptCreateStatus(update_type)
        except Exception as err:
            return False, "Invalid receipt update type {}: {}".format(
                update_enum_value, str(err))

        # If update type is completed or processed,
        # it is a hash value of the Work Order Response
        if wo_receipt_req["params"]["updateType"] in [
            ReceiptCreateStatus.PROCESSED.value,
            ReceiptCreateStatus.COMPLETED.value
        ]:
            wo_id = wo_receipt_req["params"]["workOrderId"]
            # Load the work order response and calculate it's hash
            wo_resp = self.kv_helper.get("wo-responses", wo_id)
            wo_resp_bytes = bytes(wo_resp, "UTF-8")
            wo_resp_hash = crypto.compute_message_hash(wo_resp_bytes)
            wo_resp_hash_str = crypto.byte_array_to_hex(wo_resp_hash)
            if wo_resp_hash_str != wo_receipt_req["params"]["updateData"]:
                return False, "Invalid Update data in the request"
        # If all validation is pass
        return True, ""

# -----------------------------------------------------------------------------

    def __lookup_basics(self, is_lookup_next, params):
        receipt_pool = self.kv_helper.lookup("wo-receipts")

        total_count = 0
        ids = []
        lookupTag = ""

        for wo_id in receipt_pool:
            if is_lookup_next:
                is_lookup_next = (wo_id != params["lastLookUpTag"])
                continue

            value = self.kv_helper.get("wo-receipts", wo_id)
            if not value:
                continue

            criteria = ["workerServiceId",
                        "workerId", "requesterId", "requestCreateStatus"]

            wo = json.loads(value)
            matched = True
            for c in criteria:
                if c not in params:
                    continue

                matched = (wo["params"][c] == params[c])
                if not matched:
                    break

            if matched:
                total_count = total_count + 1
                ids.append(wo_id)
                lookupTag = wo_id

        result = {
            "totalCount": total_count,
            "lookupTag": lookupTag,
            "ids": ids,
        }

        return result

# -----------------------------------------------------------------------------

    def WorkOrderReceiptLookUp(self, **params):
        """
        Function to look the set of work order receipts available
        Parameters:
            - params is variable-length arugment list containing work request
              as defined in EEA spec 7.2.8
        Returns jrpc response as defined EEA spec 7.2.9
        """

        return self.__lookup_basics(False, params)

# -----------------------------------------------------------------------------

    def WorkOrderReceiptLookUpNext(self, **params):
        """
        Function to look the set of work order receipt newly added
        Parameters:
            - params is variable-length arugment list containing work request
              as defined in EEA spec 7.2.10
        Returns jrpc response as defined EEA spec 7.2.9
        """

        return self.__lookup_basics(True, params)

# -----------------------------------------------------------------------------

    def WorkOrderReceiptRetrieve(self, **params):
        """
        Function to retrieve the details of worker
        Parameters:
            - params is variable-length arugment list containing work order
            receipt request request as defined in EEA spec 7.2.4
        Returns jrpc response as defined in 7.2.5
        """
        wo_id = params["workOrderId"]

        value = self.kv_helper.get("wo-receipts", wo_id)
        if value:
            receipt = json.loads(value)
            receipt_updates = self.kv_helper.get("wo-receipt-updates", wo_id)
            if receipt_updates is None:
                receipt["params"]["receiptCurrentStatus"] = \
                    receipt["params"]["receiptCreateStatus"]
            else:
                receipt_updates_json = json.loads(receipt_updates)
                # Get the recent update to receipt
                last_receipt = receipt_updates_json[len(receipt_updates_json)
                                                    - 1]
                receipt["params"]["receiptCurrentStatus"] = \
                    last_receipt["updateType"]
            return receipt["params"]
        else:
            raise JSONRPCDispatchException(
                JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                "Work order receipt for work order id {} not found in the "
                "database. Hence invalid parameter".format(
                    wo_id
                ))

# -----------------------------------------------------------------------------

    def WorkOrderReceiptUpdateRetrieve(self, **params):
        """
        Function to retrieve the update to work order receipt
        Parameters:
            - params is variable-length arugment list containing work order
            update retrieve request as defined in EEA spec 7.2.6
        Returns:
            Jrpc response as defined in EEA spec 7.2.7
        """
        wo_id = params["workOrderId"]
        input_json_str = params["raw"]
        input_json = json.loads(input_json_str)

        input_params = input_json["params"]
        updater_id = None
        if "updaterId" in input_params and input_params["updaterId"]:
            updater_id = input_params["updaterId"]
        # update_index is index to fetch the particular update
        # starts from 1
        update_index = input_params["updateIndex"]
        # Load list of updates to the receipt
        receipt_updates = self.kv_helper.get("wo-receipt-updates", wo_id)

        if receipt_updates:
            receipt_updates_json = json.loads(receipt_updates)
            total_updates = len(receipt_updates_json)
            if update_index <= 0:
                raise JSONRPCDispatchException(
                    JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                    "Update index should be positive non-zero number."
                    " Hence invalid parameter")
            elif update_index > total_updates:
                if update_index == self.LAST_RECEIPT_INDEX:
                    # set to the index of last update to receipt
                    update_index = total_updates - 1
                else:
                    raise JSONRPCDispatchException(
                        JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                        "Update index is larger than total update count."
                        " Hence invalid parameter")
            else:
                # If the index is less than total updates
                # then decrement by one since it is zero based array
                update_index = update_index - 1
            update_to_receipt = receipt_updates_json[update_index]
            # If updater id is present then check whether it matches
            if updater_id:
                if update_to_receipt["updaterId"] != updater_id:
                    raise JSONRPCDispatchException(
                        JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                        "Update index and updater id doesn't match"
                        " Hence invalid parameter")
            update_to_receipt["updateCount"] = total_updates
            return update_to_receipt
        else:
            raise JSONRPCDispatchException(
                JRPCErrorCodes.INVALID_PARAMETER_FORMAT_OR_VALUE,
                "There is no updates available to this receipt"
                " Hence invalid parameter")
