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
import random
import json
import avalon_enclave_manager.ias_client as ias_client

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

# -----------------------------------------------------------------

    def _connect_to_ias(self):
        """
        Connect to IAS
        """
        # IAS is not initialized in Intel SGX SIM mode. Need to check if SIM
        # mode or HW mode. Only then connect to IAS.
        self._ias = \
            ias_client.IasClient(
                IasServer=self._config['ias_url'],
                ApiKey=self._config['ias_api_key'],
                Spid=self._config['spid'],
                HttpsProxy=self._config.get('https_proxy', ""))

# -----------------------------------------------------------------

    def _generate_avr(self, quote):
        """
        Generate Attestation Verification Report by contacting IAS.

        Parameters:
            @param quote - Quote generated within this enclave
        Returns:
            @returns A dictionary of AVR, report signature and signing
                     certificate
        """
        ias_nonce = '{0:032X}'.format(random.getrandbits(128))
        self._connect_to_ias()

        logger.debug("About to post verification to IAS")
        response = self._ias.post_verify_attestation(
            quote=quote, nonce=ias_nonce)
        # check verification report
        if not self._ias.verify_report_fields(
                quote, response['verification_report']):
            logger.debug(
                "last error: " + self._ias.last_verification_error())
            if self._ias.last_verification_error() == "GROUP_OUT_OF_DATE":
                logger.warning(
                    "failure GROUP_OUT_OF_DATE " +
                    "(update your BIOS/microcode!!!) keep going")
            else:
                logger.error("Invalid report fields")
                return None
        # ALL checks have passed
        logger.info("Report fields verified")

        return json.dumps({
            'verification_report': response['verification_report'],
            'ias_report_signature': response['ias_signature'],
            'ias_report_signing_certificate': response['ias_certificate']
        })
