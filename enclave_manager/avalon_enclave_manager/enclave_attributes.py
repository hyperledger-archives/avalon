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
import json
import random
from abc import ABC, abstractmethod

import avalon_enclave_manager.attestation_common.ias_client as ias_client

logger = logging.getLogger(__name__)


class EnclaveAttributes(ABC):
    """
    Interface to be implemented by all enclaves that run within
    Intel SGX enclave.
    """

    # -----------------------------------------------------------------

    @abstractmethod
    def get_enclave_measurement(self):
        """
        A getter for enclave measurement

        Returns :
            @returns mr_enclave - Enclave measurement for enclave
        """
        pass

    # -----------------------------------------------------------------

    @abstractmethod
    def get_enclave_basename(self):
        """
        A getter for enclave basename

        Returns :
            @returns basename - Basename of enclave
        """
        pass

    # -----------------------------------------------------------------

    @abstractmethod
    def get_extended_measurements(self):
        """
        A getter for enclave extended measurements which is a tuple of enclave
        basename and enclave measurement

        Returns :
            @returns basename,measurement - A tuple of basename & measurement
        """
        pass

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
