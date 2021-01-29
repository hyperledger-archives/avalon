# Copyright 2018 Intel Corporation
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

import requests
import urllib
import json

import logging
logger = logging.getLogger(__name__)


class IasClient(object):
    """
    Provide rest api helper functions for communicating with IAS.
    """

    def __init__(self, **kwargs):
        logger.info("IAS settings:")
        self._proxies = {}
        if "HttpsProxy" in kwargs:
            self._proxies["https"] = kwargs["HttpsProxy"]
            logger.info("Proxy: %s", self._proxies["https"])
        if "Spid" in kwargs:
            self._spid = kwargs["Spid"]
            logger.debug("SPID: %s", self._spid)
        else:
            raise KeyError('Missing Spid setting')
        if "IasServer" in kwargs:
            self._ias_url = kwargs["IasServer"]
            logger.info("URL: %s", self._ias_url)
        else:
            raise KeyError('Missing IasServer setting')
        if "ApiKey" in kwargs:
            self._ias_api_key = kwargs["ApiKey"]
            logger.debug("IAS ApiKey: %s", self._ias_api_key)
        else:
            raise KeyError('Missing SpidCert setting')
        self._timeout = 300

    def get_signature_revocation_lists(self,
                                       gid='',
                                       path='/attestation/v3/sigrl/'):
        """
        @param gid: Hex, base16 encoded
        @param path: URL path for sigrl request
        @return: Base 64-encoded SigRL for EPID
                group identified by {gid} parameter.
        """

        url = self._ias_url + path + gid[0:8]
        logger.debug("Fetching SigRL from: %s", url)

        req_header = {"Ocp-Apim-Subscription-Key": self._ias_api_key}
        result = requests.get(url, proxies=self._proxies,
                              headers=req_header, verify=False)
        if result.status_code != requests.codes.ok:
            logger.error("get_signature_revocation_lists HTTP Error code : %d",
                         result.status_code)
            result.raise_for_status()

        return str(result.text)

    def post_verify_attestation(self, quote, manifest=None, nonce=None):
        """
        @param quote: base64 encoded quote attestation
        @return: Dictionary of the response from ias.
        """

        path = '/attestation/v3/report'

        url = self._ias_url + path
        json = {"isvEnclaveQuote": quote}
        if nonce is not None:
            json['nonce'] = nonce

        logger.debug("Posting attestation verification request to: %s", url)
        req_header = {"Ocp-Apim-Subscription-Key": self._ias_api_key}
        result = requests.post(url,
                               json=json,
                               proxies=self._proxies,
                               headers=req_header,
                               timeout=self._timeout)
        logger.debug("result headers: %s", result.headers)
        logger.info("received attestation result code: %d", result.status_code)
        if result.status_code != requests.codes.ok:
            logger.debug(
                "post_verify_attestation HTTP Error code : %d",
                result.status_code)
            result.raise_for_status()

        returnblob = {
            'verification_report': result.text,
            'ias_signature': result.headers.get('x-iasreport-signature'),
            'ias_certificate': urllib.parse.unquote(
                result.headers.get('x-iasreport-signing-certificate'))
        }
        return returnblob

    def verify_report_fields(self, original_quote, received_report):
        logger.debug("checking report fields from " + self._ias_url)
        self._spurious = self._ias_url
        verification_report_dict = json.loads(received_report)

        if 'id' not in verification_report_dict:
            logger.error('AVR does not contain id field')
            return False

        if 'revocationReason' in verification_report_dict:
            logger.error('AVR indicates the EPID group has been revoked')
            return False

        isv_enclave_quote_status = \
            verification_report_dict.get('isvEnclaveQuoteStatus')
        if isv_enclave_quote_status is None:
            logger.error('AVR does not include an enclave quote status')
            return False

        if 'isvEnclaveQuoteBody' not in verification_report_dict:
            logger.error('AVR does not contain quote body')
            return False

        if verification_report_dict['isvEnclaveQuoteBody'] not in \
                original_quote:
            logger.error('isvEnclaveQuoteBody field not in original quote')
            return False

        if 'epidPseudonym' not in verification_report_dict:
            logger.error('AVR does not contain an EPID pseudonym')
            return False

        if 'nonce' not in verification_report_dict:
            logger.error('AVR does not contain a nonce')
            return False

        # Leave the status check for last
        if isv_enclave_quote_status.upper() != 'OK':
            self._last_verification_error = isv_enclave_quote_status.upper()
            logger.debug(
                "enclave quote status error: " + self._last_verification_error)
            return False

        # All checks passed
        return True

    def last_verification_error(self):
        """
        Errno-like procedure to provide details about where the verification
        failed. Mostly used for GROUP_OUT_OF_DATE verification report failure.
        """
        return self._last_verification_error
