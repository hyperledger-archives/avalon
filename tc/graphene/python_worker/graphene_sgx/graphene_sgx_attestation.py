#!/usr/bin/python3

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
import sys
import logging
import base64
from avalon_worker.attestation.sgx_attestation import SGXAttestation

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# -------------------------------------------------------------------------


class GrapheneSGXAttestation(SGXAttestation):
    """
    SGX Attestation implementation for Graphene.
    """

# -------------------------------------------------------------------------

    # Class variables

    # Graphene SGX TARGET INFO
    GRAPHENE_SGX_TARGET_INFO_FILE = "/dev/attestation/my_target_info"
    # Graphene SGX user report data
    GRAPHENE_SGX_USER_REPORT_DATA_FILE = "/dev/attestation/user_report_data"
    # Graphene SGX Quote file
    GRAPHENE_SGX_QUOTE_FILE = "/dev/attestation/quote"

# -------------------------------------------------------------------------

    def get_mrenclave(self):
        """
        Get mrenclave value of enclave.

        Returns :
            mrenclave value of enclave as hex string.
            If Intel SGX environment is not present returns empty string.
        """
        # Initialize mrenclave to empty string.
        mrencalve = ""
        try:
            # Read target info
            target_info_file = \
                GrapheneSGXAttestation.GRAPHENE_SGX_TARGET_INFO_FILE
            with open(target_info_file, 'rb') as fd:
                data = fd.read()
                mrencalve = data[:32].hex()
        except Exception:
            logger.warn("Graphene-SGX Environment not setup."
                        "Return empty mrencalve string.")
        return mrencalve

# -------------------------------------------------------------------------

    def write_user_report_data(self, user_data):
        """
        Write SGX user report data to be added in quote.
        This API is called before fetching the quote from SGX.

        Parameters :
            user_data: User report data in bytes.

        Returns :
            boolean True if user report data write is success.
                    False in case of error.
        """
        try:
            # Write user report data
            user_report_data_file = \
                GrapheneSGXAttestation.GRAPHENE_SGX_USER_REPORT_DATA_FILE
            with open(user_report_data_file, 'wb') as file:
                file.write(user_data)
                logger.debug("user_data hex = {}".format(user_data.hex()))
                return True
        except Exception:
            logger.warn("Graphene-SGX Environment not setup."
                        "Cannot write user report data.")
            return False

# -------------------------------------------------------------------------

    def get_quote(self):
        """
        Get quote of enclave.

        Returns :
            quote value of enclave as base64 encoded string.
            If Intel SGX environment is not present returns empty string.
        """
        # Initialize quote string to empty string.
        quote_str = ""
        try:
            # Read quote
            quote_file = GrapheneSGXAttestation.GRAPHENE_SGX_QUOTE_FILE
            with open(quote_file, 'rb') as fd:
                data = fd.read()
                logger.debug("quote hex = {}".format(data.hex()))
                quote = base64.b64encode(data)
                quote_str = quote.decode("UTF-8")
        except Exception:
            logger.warn("Graphene-SGX Environment not setup."
                        "Return empty quote string.")
        return quote_str

# -------------------------------------------------------------------------
