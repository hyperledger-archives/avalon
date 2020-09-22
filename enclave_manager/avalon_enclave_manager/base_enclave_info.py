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

import os
import json
import time

from ssl import SSLError
from requests.exceptions import Timeout
from requests.exceptions import HTTPError
from abc import abstractmethod
from avalon_enclave_manager.enclave_attributes import EnclaveAttributes
import avalon_enclave_manager.ias_client as ias_client

import logging
logger = logging.getLogger(__name__)

TCF_HOME = os.environ.get("TCF_HOME", "../../../")
SIG_RL_UPDATE_PERIOD = 8 * 60 * 60  # in seconds every 8 hours


class BaseEnclaveInfo(EnclaveAttributes):
    """
    Abstract base class to initialize enclave, signup enclave and hold
    data obtained post signup.
    """

    _ias = None
    _epid_group = None
    _tcf_enclave_info = None
    _sig_rl_update_time = None

    # -------------------------------------------------------
    def __init__(self, is_sgx_simulator):

        # Initialize the keys that can be used later to
        # register the enclave
        self._is_sgx_simulator = is_sgx_simulator

    # -------------------------------------------------------

    def _initialize_enclave(self, config):
        """
        Create and Initialize a Intel SGX enclave with passed config

        Parameters :
            @param config - A dictionary of configurations
        Returns :
            @returns basename,measurement - A tuple of basename & measurement
        """

        # Ensure that the required keys are in the configuration
        valid_keys = set(['spid', 'ias_url', 'ias_api_key'])
        found_keys = set(config.keys())

        missing_keys = valid_keys.difference(found_keys)
        if missing_keys:
            raise \
                ValueError(
                    'Avalon enclave config file missing the following keys: '
                    '{}'.format(
                        ', '.join(sorted(list(missing_keys)))))
        # IAS is not initialized in Intel SGX SIM mode
        if not self._ias and not self._is_sgx_simulator:
            self._ias = \
                ias_client.IasClient(
                    IasServer=config['ias_url'],
                    ApiKey=config['ias_api_key'],
                    Spid=config['spid'],
                    HttpsProxy=config.get('https_proxy', ""))

        if not self._tcf_enclave_info:
            signed_enclave = self._find_enclave_library(config)
            logger.debug("Attempting to load enclave at: %s", signed_enclave)
            self._tcf_enclave_info = self._init_enclave_with(
                signed_enclave, config)
            logger.debug("Basename: %s", self.get_enclave_basename())
            logger.info("MRENCLAVE: %s", self.get_enclave_measurement())

        sig_rl_updated = False
        while not sig_rl_updated:
            try:
                self._update_sig_rl()
                sig_rl_updated = True
            except (SSLError, Timeout, HTTPError) as e:
                logger.warning(
                    "Failed to retrieve initial sig rl from IAS: %s", str(e))
                logger.warning("Retrying in 60 sec")
                time.sleep(60)

        return self.get_enclave_basename(), self.get_enclave_measurement()

    # -----------------------------------------------------------------

    @abstractmethod
    def _init_enclave_with(self, signed_enclave, config):
        """
        Initialize and return tcf_enclave_info that holds details about
        the specific enclave

        Parameters :
            @param signed_enclave - The enclave binary read from filesystem
            @param config - A dictionary of configurations
        Returns :
            @returns tcf_enclave_info - An instance of the tcf_enclave_info
        """
        pass

    # -----------------------------------------------------------------

    def _get_signup_info(self, signup_data, signup_cpp_obj, ias_nonce):
        """
        Start building up the signup info dictionary which would be persisted
        for use hereafter instead of going to enclave again.

        Parameters :
            @param signup_data - Signup data from the enclave
            @param signup_cpp_obj - CPP object to access signup APIs
            @param ias_nonce - Used in IAS request to verify attestation
                               as a distinguishing factor
        Returns :
            @returns signup_info - A dictionary of enhanced signup data
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
        if not self._is_sgx_simulator:
            logger.info("Running in Intel SGX HW mode")
            logger.debug("posting verification to IAS")
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

            mr_enclave = self.get_enclave_measurement()
            status = self._verify_enclave_info(
                json.dumps(signup_info), mr_enclave, signup_cpp_obj)
            if status != 0:
                logger.error("Verification of enclave signup info failed")
            else:
                logger.info("Verification of enclave signup info passed")

        return signup_info

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
            if (not self._is_sgx_simulator):
                sig_rl = self._ias.get_signature_revocation_lists(
                    self._epid_group)
                logger.debug("Received SigRl of {} bytes ".format(len(sig_rl)))

            self._tcf_enclave_info.set_signature_revocation_list(sig_rl)
            self._sig_rl_update_time = time.time()

    # -----------------------------------------------------------------

    def _find_enclave_library(self, config):
        """
        Find enclave library file from the parsed config

        Parameters :
            @param config - A dictionary of configurations
        Returns :
            @returns enclave_file - File path of enclave library
        """
        enclave_file_name = config.get('enclave_library')
        enclave_file_path = TCF_HOME + "/" + config.get('enclave_library_path')
        logger.info("Enclave Lib: %s", enclave_file_name)

        if enclave_file_path:
            enclave_file = os.path.join(enclave_file_path, enclave_file_name)
            if os.path.exists(enclave_file):
                logger.info("Enclave Lib Exists")
                return enclave_file
        else:
            script_directory = os.path.abspath(
                os.path.dirname(os.path.realpath(__file__)))
            logger.info("Script directory - %s", script_directory)
            search_path = [
                script_directory,
                os.path.abspath(os.path.join(script_directory, '..', 'lib')),
            ]

            for path in search_path:
                enclave_file = os.path.join(path, enclave_file_name)
                if os.path.exists(enclave_file):
                    logger.info("Enclave Lib Exits")
                    return enclave_file

        raise IOError("Could not find enclave shared object")

    # -----------------------------------------------------------------

    @abstractmethod
    def _verify_enclave_info(self, enclave_info, mr_enclave, signup_cpp_obj):
        """
        Verifies enclave signup info

        Parameters :
            @param enclave_info - A JSON serialised enclave signup info
                                  along with IAS attestation report
            @param mr_enclave - enclave measurement value
            @param signup_cpp_obj - CPP object to access signup APIs
        Returns :
            @returns 0 - If verification passed
                     1 - Otherwise
        """
        pass

    # ----------------------------------------------------------------

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

    def get_extended_measurements(self):
        """
        A getter for enclave extended measurements which is a tuple of enclave
        basename and enclave measurement

        Returns :
            @returns basename,measurement - A tuple of basename & measurement
        """
        return self.get_enclave_basename(), self.get_enclave_measurement()

    # -----------------------------------------------------------------

    def _get_sealed_data_file_name(self, relative_path, worker_id):
        """
        Helper function to construct sealed data path

        Parameters :
            @param relative_path - Relative path of sealed data
            @param worker_id - Worker id to use as part of filename
        Returns :
            @returns file_name - Fully qualified file name for sealed data
        """
        return os.path.join(TCF_HOME, relative_path + "." + worker_id)

    # -----------------------------------------------------------------
