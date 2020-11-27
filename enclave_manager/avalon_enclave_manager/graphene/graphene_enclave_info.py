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
from avalon_enclave_manager.enclave_attributes import EnclaveAttributes

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------


class GrapheneEnclaveInfo(EnclaveAttributes):
    """
    Signup Object that will be used by GrapheneEnclaveManager
    """

# -------------------------------------------------------------------------
    def __init__(self, config, worker_signup_json):
        """
        Constructor for GrapheneEnclaveInfo.
        Creates signup object.
        """
        self._config = config['EnclaveModule']
        self.sealed_data = worker_signup_json["sealed_data"]
        self.verifying_key = worker_signup_json["verifying_key"]
        self.encryption_key = worker_signup_json["encryption_key"]
        self.encryption_key_signature = \
            worker_signup_json["encryption_key_signature"]
        self.enclave_id = self.verifying_key
        quote = worker_signup_json["quote"]
        if quote is None or len(quote) == 0:
            self.proof_data = None
        else:
            self.proof_data = self._generate_avr(quote)
        self.extended_measurements = None

# -------------------------------------------------------------------------

    def get_enclave_measurement(self):
        """
        A getter for enclave measurement

        Returns :
            @returns mr_enclave - Enclave measurement for enclave
        """
        # Return None as of now. Read from proof_data when enabled.
        return None

# -----------------------------------------------------------------

    def get_enclave_basename(self):
        """
        A getter for enclave basename

        Returns :
            @returns basename - Basename of enclave
        """
        return None

# -----------------------------------------------------------------

    def get_extended_measurements(self):
        """
        A getter for enclave extended measurements which is a tuple of enclave
        basename and enclave measurement

        Returns :
            @returns basename,measurement - A tuple of basename & measurement
        """
        return None
