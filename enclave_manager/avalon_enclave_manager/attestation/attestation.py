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

from abc import ABC, abstractmethod


class Attestation(ABC):
    """
    Abstract base class for attestation(EPID and DCAP)
    """
    _config = None
    # -------------------------------------------------------

    def __init__(self, config):
        self._config = config

    # -------------------------------------------------------
    @abstractmethod
    def get_signup_info(self, signup_data):
        """
        Create and Initialize a Intel SGX enclave with passed config
        Parameters :
            @param signup_data - Signup data from the enclave
        Returns :
            @returns dict containing signup info data
        """
        pass

    # -----------------------------------------------------------------

    @abstractmethod
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
        pass

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
