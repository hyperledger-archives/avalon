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

import time
import logging
import random
import json
import importlib

from ssl import SSLError
from requests.exceptions import HTTPError, Timeout
import avalon_enclave_manager.ias_client as ias_client
from avalon_enclave_manager.attestation.attestation import Attestation
from avalon_enclave_manager.enclave_type import EnclaveType

logger = logging.getLogger(__name__)


class EpidAttestation(Attestation):
    """
    Derived class for EPID attestation
    """
    _sig_rl_update_time = None
    _epid_group = None
    _ias = None
    _tcf_enclave_info = None
    SIG_RL_UPDATE_PERIOD = 8 * 60 * 60  # in seconds every 8 hours

    # -------------------------------------------------------

    def __init__(self, config, enclave_type):
        super().__init__(config)
        # Ensure that the required keys are in the configuration
        valid_keys = set(['spid', 'ias_url', 'ias_api_key'])
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

        logger.info("ENCLAVE_TYPE {}".format(enclave_type))
        if enclave_type == EnclaveType.KME:
            self.enclave_info = importlib.import_module(
                "avalon_enclave_manager.attestation.enclave_info_kme")
        elif enclave_type == EnclaveType.WPE:
            self.enclave_info = importlib.import_module(
                "avalon_enclave_manager.attestation.enclave_info_wpe")
        elif enclave_type == EnclaveType.SINGLETON:
            self.enclave_info = importlib.import_module(
                "avalon_enclave_manager.attestation.enclave_info_singleton")
        else:
            logger.exception('Unsupported enclave type passed in the config')
            raise Exception('Unsupported enclave type passed in the config')

        # IAS is not initialized in Intel SGX SIM mode
        if not self._ias and not self.enclave_info.is_sgx_simulator():
            self._ias = \
                ias_client.IasClient(
                    IasServer=config['ias_url'],
                    ApiKey=config['ias_api_key'],
                    Spid=config['spid'],
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
        if not self.enclave_info.is_sgx_simulator():
            logger.info("Running in Intel SGX HW mode")
            logger.debug("posting verification to IAS")
            ias_nonce = '{0:032X}'.format(random.getrandbits(128))
            response = self._ias.post_verify_attestation(
                quote=signup_data['enclave_quote'], nonce=ias_nonce)
            logger.debug("posted verification to IAS")

            # check verification report
            if not self._ias.verify_report_fields(
                    signup_data['enclave_quote'],
                    response['verification_report']):
                logger.debug(
                    "last error: " + self._ias.last_verification_error())
                if self._ias.last_verification_error() == "GROUP_OUT_OF_DATE":
                    logger.warning(
                        "failure GROUP_OUT_OF_DATE " +
                        "(update your BIOS/microcode!!!) keep going")
                else:
                    logger.error("invalid report fields")
                    return None
            # ALL checks have passed
            logger.info("report fields verified")

            # Now put the proof data into the dictionary
            signup_info['proof_data'] = json.dumps({
                'verification_report': response['verification_report'],
                'ias_report_signature': response['ias_signature'],
                'ias_report_signing_certificate': response['ias_certificate']
            })
            # Grab the EPID pseudonym and put it in the enclave-persistent
            # ID for the signup info
            verification_report_dict = \
                json.loads(response['verification_report'])
            signup_info['enclave_persistent_id'] = \
                verification_report_dict.get('epidPseudonym')

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
        if not self._tcf_enclave_info:
            self._tcf_enclave_info = self.enclave_info.tcf_enclave_info(
                signed_enclave, self._config['spid'], persisted_sealed_data,
                int(num_of_enclave))

        sig_rl_updated = False
        while not sig_rl_updated:
            try:
                self._update_sig_rl()
                sig_rl_updated = True
            except (SSLError, Timeout, HTTPError) as e:
                logger.warning(
                    "Failed to retrieve initial signature"
                    " revocation list from IAS: %s", str(e))
                logger.warning("Retrying in 60 sec")
                time.sleep(60)

        return self.get_enclave_basename(), self.get_enclave_measurement()

    # -----------------------------------------------------------------

    def get_enclave_measurement(self):
        """
        A getter for enclave measurement

        Returns :
            @returns mr_enclave - Enclave measurement for enclave
        """
        return self._tcf_enclave_info.mr_enclave \
            if self._tcf_enclave_info is not None else None

    # -----------------------------------------------------------------

    def get_enclave_basename(self):
        """
        A getter for enclave basename

        Returns :
            @returns basename - Basename of enclave
        """
        return self._tcf_enclave_info.basename \
            if self._tcf_enclave_info is not None else None

    # -----------------------------------------------------------------

    def _update_sig_rl(self):
        """
        Update the signature revocation lists for EPID group on IAS server
        """

        if self._epid_group is None:
            self._epid_group = self._tcf_enclave_info.get_epid_group()
        logger.info("EPID: " + self._epid_group)

        if not self._sig_rl_update_time \
                or ((time.time() - self._sig_rl_update_time)
                    > SIG_RL_UPDATE_PERIOD):
            sig_rl = ""
            if not self.enclave_info.is_sgx_simulator():
                sig_rl = self._ias.get_signature_revocation_lists(
                    self._epid_group)
                logger.debug("Received SigRl of {} bytes ".format(len(sig_rl)))

            self._tcf_enclave_info.set_signature_revocation_list(sig_rl)
            self._sig_rl_update_time = time.time()

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

    # -----------------------------------------------------------------
