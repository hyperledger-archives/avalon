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

"""
Provide rest api helper functions for communicating with IAS.
"""

import logging
logger = logging.getLogger(__name__)


class PccsClient(object):
    """
    Provide rest api helper functions for communicating with IAS.
    """

    def __init__(self, **kwargs):
        logger.info("PCCS settings:")
        self._proxies = {}
        if "HttpsProxy" in kwargs:
            self._proxies["https"] = kwargs["HttpsProxy"]
            logger.info("Proxy: %s", self._proxies["https"])
        if "PccsServer" in kwargs:
            self._pccs_url = kwargs["PccsServer"]
            logger.info("URL: %s", self._pccs_url)
        else:
            raise KeyError('Missing PCCS Server setting')
        if "ApiKey" in kwargs:
            self._pccs_api_key = kwargs["ApiKey"]
            logger.debug("PCCS ApiKey: %s", self._pccs_api_key)
        else:
            raise KeyError('Missing PCCS API key')
        self._timeout = 300

    def post_verify_attestation(self, quote):
        """
        @param quote: base64 encoded quote attestation
        @return: Dictionary of the response from ias.
        """

        # TODO: signature and certificate are part of quote. Corresponding
        # values need to be extracted and populated
        returnblob = {
            'verification_report': quote,
            'signature': '',
            'certificate': ''
        }
        return returnblob

    def verify_report_fields(self, original_quote, received_report):
        # TODO Parse and verify the quote fields
        # All checks passed
        return True
