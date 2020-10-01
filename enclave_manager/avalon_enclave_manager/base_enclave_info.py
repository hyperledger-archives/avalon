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

from abc import ABC, abstractmethod
from avalon_enclave_manager.enclave_attributes import EnclaveAttributes
from avalon_enclave_manager.attestation.epid_attestation import EpidAttestation

import logging
logger = logging.getLogger(__name__)

TCF_HOME = os.environ.get("TCF_HOME", "../../../")
SIG_RL_UPDATE_PERIOD = 8 * 60 * 60  # in seconds every 8 hours


class BaseEnclaveInfo(EnclaveAttributes):
    """
    Abstract base class to initialize enclave, signup enclave and hold
    data obtained post signup.
    """

    # -------------------------------------------------------
    def __init__(self, config, enclave_type):

        # Initialize the keys that can be used later to
        # register the enclave
        self._config = config.get("EnclaveModule")
        self._attestation = None
        if "attestation_type" in self._config:
            if self._config["attestation_type"] == "EPID":
                self._attestation = EpidAttestation(config.get(
                    "EpidAttestation"), enclave_type)
            else:
                raise ValueError('Invalid attestation type {}'.format(
                    self._config["attestation_type"]))
        else:
            raise ValueError('Missing attestation type in config')

    # -------------------------------------------------------

    def _initialize_enclave(self):
        """
        Create and Initialize a Intel SGX enclave with passed config

        Returns :
            @returns basename,measurement - A tuple of basename & measurement
        """

        signed_enclave = self._find_enclave_library()
        logger.debug("Attempting to load enclave at: %s", signed_enclave)
        self._tcf_enclave_info = self._init_enclave_with(
            signed_enclave)
        logger.debug("Basename: %s", self.get_enclave_basename())
        logger.info("MRENCLAVE: %s", self.get_enclave_measurement())

        return self.get_enclave_basename(), self.get_enclave_measurement()

    # -----------------------------------------------------------------

    @abstractmethod
    def _init_enclave_with(self, signed_enclave):
        """
        Initialize and return tcf_enclave_info that holds details about
        the specific enclave

        Parameters :
            @param signed_enclave - The enclave binary read from filesystem
        Returns :
            @returns tcf_enclave_info - An instance of the tcf_enclave_info
        """
        pass

    # -----------------------------------------------------------------

    def _get_signup_info(self, signup_data, signup_cpp_obj):
        """
        Start building up the signup info dictionary which would be persisted
        for use hereafter instead of going to enclave again.

        Parameters :
            @param signup_data - Signup data from the enclave
            @param signup_cpp_obj - CPP object to access signup APIs
        Returns :
            @returns signup_info - A dictionary of enhanced signup data
        """
        signup_info = self._attestation.get_signup_info(signup_data)
        if not self.is_sgx_simulator():
            mr_enclave = self.get_enclave_measurement()
            status = self._verify_enclave_info(
                json.dumps(signup_info), mr_enclave, signup_cpp_obj)
            if status != 0:
                logger.error("Verification of enclave signup info failed")
            else:
                logger.info("Verification of enclave signup info passed")

        return signup_info

    # -----------------------------------------------------------------

    def _find_enclave_library(self):
        """
        Find enclave library file from the parsed config

        Returns :
            @returns enclave_file - File path of enclave library
        """
        enclave_file_name = self._config.get('enclave_library')
        enclave_file_path = TCF_HOME + "/" + self._config.get(
                'enclave_library_path')
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
        return self._attestation.get_enclave_measurement()

    # -----------------------------------------------------------------

    def get_enclave_basename(self):
        """
        A getter for enclave basename

        Returns :
            @returns basename - Basename of enclave
        """
        return self._attestation.get_enclave_basename()

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

    def is_sgx_simulator(self):
        """
        Function to check whether enclave is running
        in simulation mode or not.
        Returns :
            @returns True if it is simulation mode or
                 False if it is SGX hardware mode.
        """
        return self._attestation.is_sgx_simulator()

    # -----------------------------------------------------------------
