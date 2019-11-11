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
Worker.py -- functions to perform worker related functions based on Spec 1.0 compatibility  

"""

import logging
import json
import utility.utility as utility
import utility.file_utils as futils
import config.config as pconfig

logger = logging.getLogger(__name__)


class WorkerDetails():
    """Class to store the worker details
    """
    def __init__(self):
        """
        Function to set the member variables of this class with default value as per TCf Spec
        """
        tcs_worker = pconfig.read_config_from_toml("tcs_config.toml","WorkerConfig")
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




class SGXWorkerDetails(WorkerDetails):
    """
    TEE SGX worker type data
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
        self.worker_id = ""

#-----------------------------------------------------------------------------------------------
    def load_worker(self,input_str):
        """
        Function to load the member variables of this class based on worker retrieved details
        """
        worker_data = input_str ['result']['details']
        logger.info("*********Updating Worker Details*********")
        self.hashing_algorithm = worker_data['hashingAlgorithm']
        self.signing_algorithm = worker_data['signingAlgorithm']
        self.key_encryption_algorithm = worker_data['keyEncryptionAlgorithm']
        self.data_encryption_algorithm = worker_data['dataEncryptionAlgorithm']
        self.verification_key = worker_data['workerTypeData']['verificationKey']
        self.encryption_key = worker_data['workerTypeData']['encryptionKey']
        if 'proofData' in worker_data['workerTypeData'] and worker_data['workerTypeData']['proofData']:
            # proofData will be initialized only in HW mode by tcf_enclave_bridge
            # module when signup info is obtained from worker.
            self.proof_data = json.loads(worker_data['workerTypeData']['proofData'])

        self.worker_id = utility.strip_begin_end_key(
                worker_data['workerTypeData']['verificationKey']).encode("UTF-8").hex()
        ''' worker_id - newline, BEGIN PUB KEY and END PUB KEY are removed
                        from worker's verification key and converted to hex '''
        logger.info("Hashing Algorithm : %s", self.hashing_algorithm)
        logger.info("Signing Algorithm : %s", self.signing_algorithm)

#-----------------------------------------------------------------------------------------------
