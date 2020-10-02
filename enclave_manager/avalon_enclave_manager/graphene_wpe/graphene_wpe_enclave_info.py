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

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------


class GrapheneWPESignupInfo():
    """
    Signup Object that will be used by BaseEnclave Manager
    """

# -------------------------------------------------------------------------
    def __init__(self, worker_signup_json):
        """
        Constructor for SignupGraphene.
        Creates signup object.
        """
        self.sealed_data = worker_signup_json["sealed_data"]
        self.verifying_key = worker_signup_json["verifying_key"]
        self.encryption_key = worker_signup_json["encryption_key"]
        self.encryption_key_signature = \
            worker_signup_json["encryption_key_signature"]
        self.enclave_id = self.verifying_key
        # TODO: Generate IAS AVR
        self.proof_data = None
        self.extended_measurements = None

# -------------------------------------------------------------------------
