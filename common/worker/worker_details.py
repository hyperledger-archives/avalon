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
import utils.utility as utility

logger = logging.getLogger(__name__)

class WorkerDetails(object):
    """Class to store the worker details
    """
    def __init__(self):
        """
        Function to set the member variables of this class with default value as per TCf Spec
        """
        tcs_worker = utility.read_toml_file("tcs_config.toml","WorkerConfig")
        self.hashing_algorithm = tcs_worker['HashingAlgorithm']
        self.signing_algorithm = tcs_worker['SigningAlgorithm']
        self.keyEncryptionAlgorithm = tcs_worker['KeyEncryptionAlgorithm']
        self.data_encryption_algorithm = tcs_worker['DataEncryptionAlgorithm']
        self.worker_typedata_verification_key = ""
        self.worker_encryption_key = ""
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
        self.worker_typedata_verification_key = worker_data['workerTypeData']['verificationKey']
        self.worker_encryption_key = worker_data['workerTypeData']['encryptionKey']
        # worker_id - newline, BEGIN PUB KEY and END PUB KEY are removed from worker's verification key
        self.worker_id = utility.strip_begin_end_key(worker_data['workerTypeData']['verificationKey'])
        logger.info("Hashing Algorithm : %s", self.hashing_algorithm)
        logger.info("Signing Algorithm : %s", self.signing_algorithm)

#-----------------------------------------------------------------------------------------------


