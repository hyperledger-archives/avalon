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
import sys

from abc import ABC, abstractmethod
from utility.jrpc_utility import create_error_response
from error_code.error_status import WorkOrderStatus

logger = logging.getLogger(__name__)


class WOProcessorEnclaveManagerHelper(ABC):

    def __init__(self):
        logger.info("Initializing WOProcessorEnclaveManagerHelper")


# -------------------------------------------------------------------------

    def _manager_on_boot(self):
        """
        Executes Boot flow of enclave manager
        """

        # Extended_measurements is a tuple, viz., basename and measurement
        # for the enclave
        logger.info("Executing boot flow for WPE")
        if self._wpe_requester\
            .register_wo_processor(self._unique_verification_key,
                                   self.encryption_key,
                                   self.proof_data,
                                   self.mr_enclave):
            logger.info("WPE registration successful")
            # Update mapping of worker_id to workers in a pool
            self._worker_kv_delegate.update_worker_map(
                self._worker_id, self._identity)
        else:
            logger.error("WPE registration failed. Cannot proceed further.")
            sys.exit(1)
# -------------------------------------------------------------------------

    def _execute_wo_in_trusted_enclave(self, input_json_str):
        """
        Submits workorder request to Worker enclave and retrieves the response

        Parameters :
            input_json_str - A JSON formatted str of the request to execute
        Returns :
            json_response - A JSON response received from the enclave. Errors
                            are also wrapped in a JSON str if exceptions have
                            occurred.
        """
        try:
            pre_proc_output = self._wpe_requester\
                .preprocess_work_order(input_json_str, self.encryption_key)
            if "error" in pre_proc_output:
                # If error in preprocessing response, skip workorder processing
                logger.error("Failed to preprocess at WPE enclave manager.")
                return pre_proc_output

            wo_response = self._send_wo_to_process(input_json_str,
                                                   pre_proc_output)
        except Exception as e:
            logger.error("failed to execute work order; %s", str(e))
            wo_response = create_error_response(WorkOrderStatus.FAILED,
                                                random.randint(0, 100000),
                                                str(e))
        return wo_response

    @abstractmethod
    def _send_wo_to_process(self, input_json_str, pre_proc_output):
        """
        Send work order request to be processed within enclave.

        Parameters :
            input_json_str - A JSON formatted str of the request to execute
            pre_proc_output - Preprocessing outcome of the work-order request
        Returns :
            response - Response as received after work-order execution
        """
        pass
