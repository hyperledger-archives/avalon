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
import importlib

import avalon_enclave_manager.attestation.dcap.pccs_client as pccs_client
from avalon_enclave_manager.attestation.attestation import Attestation
from avalon_enclave_manager.enclave_type import EnclaveType

logger = logging.getLogger(__name__)


class DcapAttestation(Attestation):
    """
    Derived class for EPID attestation
    """
    _pccs = None
    _dcap_enclave_info = None

    # -------------------------------------------------------

    def __init__(self, config, enclave_type):
        super().__init__(config)
        # Ensure that the required keys are in the configuration
        valid_keys = set(['pccs_url', 'pccs_api_key'])
        found_keys = set(config.keys())

        missing_keys = valid_keys.difference(found_keys)
        if missing_keys:
            raise ValueError(
                'Avalon enclave config file missing the following keys: '
                '{}'.format(
                    ', '.join(sorted(list(missing_keys)))))
        # Import the enclave info module based on
        # the enclave type because each swig module is dependent on
        # corresponding library enclave bridge library.

        if enclave_type == EnclaveType.KME:
            self.enclave_info = importlib.import_module(
                "avalon_enclave_manager.attestation.dcap."
                "dcap_enclave_info_kme")
        elif enclave_type == EnclaveType.WPE:
            self.enclave_info = importlib.import_module(
                "avalon_enclave_manager.attestation."
                "dcap.dcap_enclave_info_wpe")
        elif enclave_type == EnclaveType.SINGLETON:
            self.enclave_info = importlib.import_module(
                "avalon_enclave_manager.attestation.dcap."
                "dcap_enclave_info_singleton")
        else:
            logger.exception('Unsupported enclave type passed in the config')
            raise Exception('Unsupported enclave type passed in the config')

        # IAS is not initialized in Intel SGX SIM mode
        if not self._pccs and not self.is_sgx_simulator():
            self._pccs = \
                pccs_client.PccsClient(
                    PccsServer=config['pccs_url'],
                    ApiKey=config['pccs_api_key'],
                    HttpsProxy=config.get('https_proxy', ""))

    # -------------------------------------------------------

    def get_signup_info(self, signup_data):
        """
        Create and Initialize a Intel SGX enclave with passed config
        Parameters :
            @param signup_data - Signup data from the enclave
        Returns :
            @returns dict containing signup info data
        """
        signup_info = {
            'verifying_key': signup_data['verifying_key'],
            'encryption_key': signup_data['encryption_key'],
            'encryption_key_signature':
                signup_data['encryption_key_signature'],
            'proof_data': 'Not present',
            'enclave_persistent_id': 'Not present'
        }

        # If we are not running in the simulator, we are going to go and get
        # an attestation verification report for our signup data.
        if not self.is_sgx_simulator():
            logger.info("Running in Intel SGX HW mode")
            logger.debug("posting verification to IAS")
            response = self._pccs.post_verify_attestation(
                quote=signup_data['enclave_quote'])

            # check verification report
            if not self._pccs.verify_report_fields(
                    signup_data['enclave_quote'],
                    response['verification_report']):
                logger.error("invalid report fields")
                return None
            # ALL checks have passed
            logger.info("report fields verified")

            # Now put the proof data into the dictionary
            signup_info['proof_data'] = json.dumps({
                'verification_report': response['verification_report'],
                'report_signature': response['signature'],
                'report_signing_certificate': response['certificate']
            })
            signup_info['enclave_persistent_id'] = ''

        return signup_info

    # -----------------------------------------------------------------

    def init_enclave_info(self, signed_enclave, persisted_sealed_data,
                          num_of_enclave):
        """
        Parameters :
            @param signed_enclave - The enclave binary read from filesystem
            @param persisted_sealed_data - persisted sealed data file path
            @param num_of_enclave - number of enclave to create
        Returns :
            @returns True on success False on failure
        """
        if not self._dcap_enclave_info:
            self._dcap_enclave_info = self.enclave_info.DcapEnclaveInfo(
                signed_enclave, persisted_sealed_data,
                int(num_of_enclave))

        return self.get_enclave_basename(), self.get_enclave_measurement()

    # -----------------------------------------------------------------

    def get_enclave_measurement(self):
        """
        A getter for enclave measurement
        Returns :
            @returns mr_enclave - Enclave measurement for enclave
        """
        return self._dcap_enclave_info.mr_enclave \
            if self._dcap_enclave_info is not None else None

    # -----------------------------------------------------------------

    def get_enclave_basename(self):
        """
        A getter for enclave basename
        Returns :
            @returns basename - Basename of enclave
        """
        return self._dcap_enclave_info.basename \
            if self._dcap_enclave_info is not None else None

    # -----------------------------------------------------------------

    def is_sgx_simulator(self):
        """
        Function to check whether enclave is running
        in simulation mode or not.
        Returns :
            @returns True if it is simulation mode
                     False if it is SGX hardware mode
        """
        return self.enclave_info.is_sgx_simulator()
