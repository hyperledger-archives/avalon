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

import json
import logging
import verify_dcap_quote.dcap_verify_report as dcap_report_util

logger = logging.getLogger(__name__)


def verify_dcap_quote(enclave_info):
    '''
    Function to verify quote status, signature of DCAP quote
    '''

    verification_report = \
        json.dumps(enclave_info["proof_data"]["verification_report"])
    report_cert = \
        enclave_info["proof_data"]["report_signing_certificate"]
    proof_signature = enclave_info["proof_data"]["report_signature"]

    quote_status = dcap_report_util.verify_dcap_quote(
        verification_report)
    if quote_status is False:
        logger.error("Enclave quote verification failed")
        return quote_status
    else:
        logger.info("Enclave quote verification passed")

    report_sig_status = dcap_report_util.verify_dcap_quote_signature(
        report_cert,
        verification_report,
        proof_signature)
    if report_sig_status is False:
        logger.error("Enclave DCAP quote signature verification failed")
    else:
        logger.info("Enclave DCAP quote signature verification passed")
    return report_sig_status
