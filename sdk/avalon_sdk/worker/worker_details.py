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

"""
Perform worker-related functions based on EEA Spec 1.0.
"""

import logging
import json
import hashlib

import config.config as pconfig
from enum import Enum, unique
from utility.hex_utils import is_valid_hex_str

logger = logging.getLogger(__name__)


@unique
class WorkerType(Enum):
    """
    Worker types are:
    1 = TEE-SGX: Intel SGX Trusted Execution Environment (hardware based)
    2 = MPC: Trusted Multi-Party Compute (software/hardware based)
    3 = ZK: Zero-knowledge proofs (software based)
    """
    TEE_SGX = 1
    MPC = 2
    ZK = 3


@unique
class WorkerStatus(Enum):
    """
    Worker status values:
    1 - worker is ACTIVE
    2 - worker is temporarily OFF_LINE
    3 - worker is DECOMMISSIONED
    4 - worker is COMPROMISED

    From EEA spec 5.2.
    """
    ACTIVE = 1
    OFF_LINE = 2
    DECOMMISSIONED = 3
    COMPROMISED = 4


class WorkerDetails():
    """Class to store the worker details
    """

    def __init__(self):
        """
        Set the member variables of this class with default
        values as per the EEA Spec.
        """
        tcs_worker = pconfig.read_config_from_toml("tcs_config.toml",
                                                   "WorkerConfig")
        self.work_order_sync_uri = ""
        self.work_order_async_uri = ""
        self.work_order_pull_uri = ""
        self.work_order_notify_ri = ""
        self.receipt_invocation_uri = ""
        self.work_oder_invocation_address = ""
        self.receipt_invocation_address = ""
        self.from_address = ""
        self.hashing_algorithm = tcs_worker['HashingAlgorithm']
        self.signing_algorithm = tcs_worker['SigningAlgorithm']
        self.key_encryption_algorithm = tcs_worker['KeyEncryptionAlgorithm']
        self.data_encryption_algorithm = tcs_worker['DataEncryptionAlgorithm']
        self.work_order_payload_formats = []

    def validate_worker_details(self, details):
        """
        Validate the details field of a worker.

        Parameters:
            Details is json formatted string
        Returns:
            None on success and error string on failure
        """
        details_dict = json.loads(details)
        worker_details_fields = [
            "workOrderSyncUri",
            "workOrderAsyncUri",
            "workOrderPullUri",
            "workOrderNotifyUri",
            "receiptInvocationUri",
            "workOrderInvocationAddress",
            "receiptInvocationAddress",
            "fromAddress",
            "hashingAlgorithm",
            "signingAlgorithm",
            "keyEncryptionAlgorithm",
            "dataEncryptionAlgorithm",
            "workOrderPayloadFormats",
            "workerTypeData"
        ]
        worker_type_fields = [
            "verificationKey",
            "extendedMeasurements",
            "proofDataType",
            "proofData",
            "encryptionKey",
            "encryptionKeyNonce",
            "encryptionKeySignature",
            "enclaveCertificate"
        ]

        for key in details_dict:
            if key not in worker_details_fields:
                return "Invalid argument {}".format(key)

        if "workerTypeData" in details_dict:
            for key in details_dict['workerTypeData']:
                if key not in worker_type_fields:
                    return "Invalid argument {}".format(key)

        if ("workOrderSyncUri" in details_dict.keys() and
                not is_valid_hex_str(details_dict['workOrderSyncUri'])):
            return "Invalid argument workOrderSyncUri"

        if ("workOrderAsyncUri" in details_dict.keys() and
                not is_valid_hex_str(details_dict['workOrderAsyncUri'])):
            return "Invalid argument workOrderAsyncUri"

        if ("workOrderPullUri" in details_dict.keys() and
                not is_valid_hex_str(details_dict['workOrderPullUri'])):
            return "Invalid argument workOrderPullUri"

        if ("workOrderNotifyUri" in details_dict.keys() and
                not is_valid_hex_str(details_dict['workOrderNotifyUri'])):
            return "Invalid argument workOrderNotifyUri"

        if ("receiptInvocationUri" in details_dict.keys() and
                not is_valid_hex_str(details_dict['receiptInvocationUri'])):
            return "Invalid argument receiptInvocationUri"

        if ("workOrderInvocationAddress" in details_dict.keys() and
                not is_valid_hex_str(
                details_dict['workOrderInvocationAddress'])):
            return "Invalid argument workOrderInvocationAddress"

        if ("receiptInvocationAddress" in details_dict.keys() and
                not is_valid_hex_str(
                details_dict['receiptInvocationAddress'])):
            return "Invalid argument receiptInvocationAddress"

        if ("fromAddress" in details_dict.keys() and
                not is_valid_hex_str(details_dict['fromAddress'])):
            return "Invalid argument fromAddress"

        if ("workOrderPayloadFormats" in details_dict.keys() and
                not is_valid_hex_str(
                    details_dict['workOrderPayloadFormats'])):
            return "Invalid argument workOrderPayloadFormats"

        if ("workerTypeData" in details_dict.keys()):
            if ("verificationKey" in details_dict["workerTypeData"].keys() and
                    details_dict["workerTypeData"]["verificationKey"] is None):
                return "Invalid argument verificationKey"

            if ("proofDataType" in details_dict["workerTypeData"].keys() and
                    details_dict["workerTypeData"]["proofDataType"] is None):
                return "Invalid argument proofDataType"

            if ("encryptionKey" in details_dict["workerTypeData"].keys() and
                    details_dict["workerTypeData"]["encryptionKey"] is None):
                return "Invalid argument encryptionKey"

        return None


class SGXWorkerDetails(WorkerDetails):
    """
    Contains Intel SGX TEE worker type data.
    """

    def __init__(self):
        super(SGXWorkerDetails, self).__init__()
        self.verification_key = ""
        self.extended_measurements = ""
        self.proof_data_type = ""
        self.proof_data = {}
        self.encryption_key = ""
        self.encryption_key_nonce = ""
        self.encryption_key_signature = ""
        self.enclave_certificate = ""

# -----------------------------------------------------------------------------
    def load_worker(self, worker_data):
        """
        Load member variables of this class
        based on worker-retrieved details.

        Parameters:
            worker_data Worker Data to load into the class
        """
        logger.info("*********Updating Worker Details*********")
        self.hashing_algorithm = worker_data['hashingAlgorithm']
        self.signing_algorithm = worker_data['signingAlgorithm']
        self.key_encryption_algorithm = worker_data['keyEncryptionAlgorithm']
        self.data_encryption_algorithm = worker_data['dataEncryptionAlgorithm']
        self.verification_key = \
            worker_data['workerTypeData']['verificationKey']
        self.encryption_key = worker_data['workerTypeData']['encryptionKey']
        self.encryption_key_signature = \
            worker_data['workerTypeData']['encryptionKeySignature']
        if 'proofData' in worker_data['workerTypeData'] and \
                worker_data['workerTypeData']['proofData']:
            # proofData will be initialized only in HW mode by the
            # tcf_enclave_bridge module when sign up info is obtained from
            # the worker.
            self.proof_data = json.loads(
                worker_data['workerTypeData']['proofData'])

        logger.info("Hashing Algorithm : %s", self.hashing_algorithm)
        logger.info("Signing Algorithm : %s", self.signing_algorithm)

# -----------------------------------------------------------------------------
