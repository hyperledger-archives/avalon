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
from abc import ABC, abstractmethod

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
