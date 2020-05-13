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
import random
import logging

from ssl import SSLError
from requests.exceptions import Timeout
from requests.exceptions import HTTPError
import avalon_crypto_utils.keys as keys
import avalon_enclave_manager.ias_client as ias_client
import avalon_enclave_manager.kme.kme_enclave as enclave
from avalon_enclave_manager.base_enclave_info import BaseEnclaveInfo

logger = logging.getLogger(__name__)

TCF_HOME = os.environ.get("TCF_HOME", "../../../")
SIG_RL_UPDATE_PERIOD = 8 * 60 * 60  # in seconds every 8 hours


class KeyManagementEnclaveInfo(BaseEnclaveInfo):
    """
    Abstract base class to initialize enclave, signup enclave and hold
    data obtained post signup.
    """

    _ias = None
    _epid_group = None
    _tcf_enclave_info = None
    _sig_rl_update_time = None

    # -------------------------------------------------------
    def __init__(self, config):

        # Initialize the keys that can be used later to
        # register the enclave

        enclave._SetLogger(logger)

        self._initialize_enclave(config)
        enclave_info = self._create_enclave_signup_data()
        try:
            self.nonce = enclave_info['nonce']
            self.sealed_data = enclave_info['sealed_data']
            self.verifying_key = enclave_info['verifying_key']
            self.encryption_key = enclave_info['encryption_key']
            self.encryption_key_signature = \
                enclave_info['encryption_key_signature']
            self.proof_data = enclave_info['proof_data']
            self.enclave_id = enclave_info['enclave_id']
        except KeyError as ke:
            raise Exception("missing enclave initialization parameter; {}"
                            .format(str(ke)))

        self.enclave_keys = \
            keys.EnclaveKeys(self.verifying_key, self.encryption_key)

    # -------------------------------------------------------

    def _create_enclave_signup_data(self):
        """
        Create enclave signup data
        """

        nonce = '{0:032X}'.format(random.getrandbits(128))
        try:
            enclave_data = self._create_signup_info(nonce)
        except Exception as err:
            raise Exception('failed to create enclave signup data; {}'
                            .format(str(err)))

        enclave_info = dict()
        enclave_info['nonce'] = nonce
        enclave_info['sealed_data'] = enclave_data.sealed_signup_data
        enclave_info['verifying_key'] = enclave_data.verifying_key
        enclave_info['encryption_key'] = enclave_data.encryption_key
        enclave_info['encryption_key_signature'] = \
            enclave_data.encryption_key_signature
        enclave_info['enclave_id'] = enclave_data.verifying_key
        enclave_info['proof_data'] = ''
        if not enclave.is_sgx_simulator():
            enclave_info['proof_data'] = enclave_data.proof_data

        return enclave_info

    # -----------------------------------------------------------------

    def _create_signup_info(self, nonce):
        """
        Create enclave signup data
        @param nonce - nonce is used in IAS request to verify attestation
                    as distinguishing factor
        """

        # Part of what is returned with the signup data is an enclave quote, we
        # want to update the revocation list first.
        self._update_sig_rl()
        # Now, let the enclave create the signup data

        signup_cpp_obj = enclave.SignupInfoSingleton()
        signup_data = signup_cpp_obj.CreateEnclaveData()
        if signup_data is None:
            return None

        # We don't really have any reason to call back down into the enclave
        # as we have everything we need.
        #
        # Start building up the signup info dictionary and we will serialize
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
        if not enclave.is_sgx_simulator():
            logger.debug("posting verification to IAS")
            response = self._ias.post_verify_attestation(
                quote=signup_data['enclave_quote'], nonce=nonce)
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

        # Now we can finally serialize the signup info and create a
        # corresponding signup info object. Because we don't want the
        # sealed signup data in the serialized version, we set it separately.
        signup_info_obj = signup_cpp_obj.DeserializeSignupInfo(
            json.dumps(signup_info))
        signup_info_obj.sealed_signup_data = \
            signup_data['sealed_enclave_data']
        # Now we can return the real object
        return signup_info_obj

    # -----------------------------------------------------------------

    def _initialize_enclave(self, config):
        """
        Create and Initialize a Intel SGX enclave with passed config
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
        if not self._ias and not enclave.is_sgx_simulator():
            self._ias = \
                ias_client.IasClient(
                    IasServer=config['ias_url'],
                    ApiKey=config['ias_api_key'],
                    Spid=config['spid'],
                    HttpsProxy=config.get('https_proxy', ""))

        if not self._tcf_enclave_info:
            signed_enclave = self._find_enclave_library(config)
            logger.debug("Attempting to load enclave at: %s", signed_enclave)
            self._tcf_enclave_info = enclave.tcf_enclave_info(
                signed_enclave, config['spid'], int(config['num_of_enclaves']))
            logger.info("Basename: %s", self.get_enclave_basename())
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
            if (not enclave.is_sgx_simulator()):
                sig_rl = self._ias.get_signature_revocation_lists(
                    self._epid_group)
                logger.debug("Received SigRl of {} bytes ".format(len(sig_rl)))

            self._tcf_enclave_info.set_signature_revocation_list(sig_rl)
            self._sig_rl_update_time = time.time()

    # -----------------------------------------------------------------

    def _find_enclave_library(self, config):
        """
        Find enclave library file from the parsed config
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

    def _verify_enclave_info(self, enclave_info, mr_enclave, signup_cpp_obj):
        """
        Verifies enclave signup info
        @param enclave_info is a JSON serialised enclave signup info
        along with IAS attestation report
        @param mr_enclave - enclave measurement value
        @param signup_cpp_obj - CPP object to access signup APIs
        """
        return signup_cpp_obj.VerifyEnclaveInfo(enclave_info, mr_enclave)

    # ----------------------------------------------------------------

    def get_enclave_measurement(self):
        """
        Returns enclave measurement if enclave_info is populated
        else returns None
        """
        return self._tcf_enclave_info.mr_enclave \
            if self._tcf_enclave_info is not None else None

    # -----------------------------------------------------------------

    def get_enclave_basename(self):
        """
        Returns enclave basename if enclave_info is populated
        else returns None
        """
        return self._tcf_enclave_info.basename \
            if self._tcf_enclave_info is not None else None

    # -----------------------------------------------------------------

    def get_extended_measurements(self):
        """
        Returns enclave extended measurements which is a tuple of enclave
        basename and enclave measurement
        """
        return self.get_enclave_basename(), self.get_enclave_measurement()

    # -----------------------------------------------------------------

    def get_enclave_public_info(self):
        """
        Return information about the enclave
        """
        signup_cpp_obj = enclave.SignupInfoSingleton()
        return signup_cpp_obj.UnsealEnclaveData()

    # -------------------------------------------------------
