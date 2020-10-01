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
import logging

from ssl import SSLError
from requests.exceptions import Timeout
from requests.exceptions import HTTPError
import utility.hex_utils as hex_utils
import utility.file_utils as file_utils
import avalon_enclave_manager.kme.kme_enclave as enclave
from avalon_enclave_manager.base_enclave_info import BaseEnclaveInfo

logger = logging.getLogger(__name__)


class KeyManagementEnclaveInfo(BaseEnclaveInfo):
    """
    KME info class to initialize enclave, signup enclave and hold
    data obtained post signup.
    """

    # -------------------------------------------------------
    def __init__(self, config, worker_id, enlcave_type):

        enclave._SetLogger(logger)
        super().__init__(config, enlcave_type)

        self._worker_id = worker_id
        self._initialize_enclave()
        enclave_info = self._create_enclave_signup_data()
        try:
            self.sealed_data = enclave_info['sealed_data']
            self.verifying_key = enclave_info['verifying_key']
            self.encryption_key = enclave_info['encryption_key']
            self.encryption_key_signature = \
                enclave_info['encryption_key_signature']
            self.proof_data = enclave_info['proof_data']
            self.enclave_id = enclave_info['enclave_id']
            self.extended_measurements = self.get_extended_measurements()
        except KeyError as ke:
            raise Exception("missing enclave initialization parameter; {}"
                            .format(str(ke)))

    # -------------------------------------------------------

    def _create_enclave_signup_data(self):
        """
        Create enclave signup data

        Returns :
            @returns enclave_info - A dictionary of enclave data
        """

        try:
            enclave_data = self._create_signup_info()
        except Exception as err:
            raise Exception('failed to create enclave signup data; {}'
                            .format(str(err)))

        enclave_info = dict()
        enclave_info['sealed_data'] = enclave_data.sealed_signup_data
        enclave_info['verifying_key'] = enclave_data.verifying_key
        enclave_info['encryption_key'] = enclave_data.encryption_key
        enclave_info['encryption_key_signature'] = \
            enclave_data.encryption_key_signature
        enclave_info['enclave_id'] = enclave_data.verifying_key
        enclave_info['proof_data'] = ''
        if not self.is_sgx_simulator():
            enclave_info['proof_data'] = enclave_data.proof_data

        return enclave_info

    # -----------------------------------------------------------------

    def _create_signup_info(self):
        """
        Create enclave signup data

        Returns :
            @returns signup_info_obj - Signup info data
        """

        signup_cpp_obj = enclave.SignupInfoKME()

        if "wpe_mrenclave" in self._config:
            self._wpe_mrenclave = self._config["wpe_mrenclave"]
        else:
            tcf_home = os.environ.get("TCF_HOME", '../../../')
            self._wpe_mrenclave = hex_utils.mrenclave_hex_string(
                tcf_home + "/"
                + self._config["wpe_mrenclave_read_from_file"])

        # @TODO : Passing in_ext_data_signature as empty string "" as of now
        signup_data = signup_cpp_obj.CreateEnclaveData(self._wpe_mrenclave, "")
        logger.info("WPE MRenclave value {}".format(self._wpe_mrenclave))
        if signup_data is None:
            return None

        signup_info = self._get_signup_info(
            signup_data, signup_cpp_obj)

        # Now we can finally serialize the signup info and create a
        # corresponding signup info object. Because we don't want the
        # sealed signup data in the serialized version, we set it separately.
        signup_info_obj = signup_cpp_obj.DeserializeSignupInfo(
            json.dumps(signup_info))
        signup_info_obj.sealed_signup_data = \
            signup_data['sealed_enclave_data']
        file_utils.write_to_file(signup_info_obj.sealed_signup_data,
                                 self._get_sealed_data_file_name(
                                     self._config["sealed_data_path"],
                                     self._worker_id))
        # Now we can return the real object
        return signup_info_obj

    # -----------------------------------------------------------------

    def get_enclave_public_info(self):
        """
        Return information about the enclave

        Returns :
            @returns A dict of sealed data
        """
        signup_cpp_obj = enclave.SignupInfoKME()
        return signup_cpp_obj.UnsealEnclaveData()

    # -----------------------------------------------------------------

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
        return signup_cpp_obj.VerifyEnclaveInfo(enclave_info,
                                                mr_enclave,
                                                self._wpe_mrenclave)

    # ----------------------------------------------------------------
    def _init_enclave_with(self, signed_enclave):
        """
        Initialize and return tcf_enclave_info that holds details about
        the KME enclave

        Parameters :
            @param signed_enclave - The enclave binary read from filesystem
        Returns :
            @returns tcf_enclave_info - An instance of the tcf_enclave_info
        """
        # Get sealed data if persisted from previous startup.
        persisted_sealed_data = file_utils.read_file(
            self._get_sealed_data_file_name(self._config["sealed_data_path"],
                                            self._worker_id))
        return self._attestation.init_enclave_info(
            signed_enclave, persisted_sealed_data,
            int(self._config['num_of_enclaves']))

    # -----------------------------------------------------------------
