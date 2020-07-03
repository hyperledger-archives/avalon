# Copyright 2019 Intel Corporation
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
import verify_report.verify_report as verify_report_util
from error_code.error_status import QuoteStatus

logger = logging.getLogger(__name__)


def verify_attestation_report(enclave_info):
    '''
    Function to verify quote status, signature of IAS attestation report
    '''

    verification_report = \
        json.dumps(enclave_info["proof_data"]["verification_report"])
    ias_report_cert = \
        enclave_info["proof_data"]["ias_report_signing_certificate"]
    proof_signature = enclave_info["proof_data"]["ias_report_signature"]

    quote_status = verify_report_util.verify_quote(
                       verification_report,
                       QuoteStatus.GROUP_OUT_OF_DATE_OK.value)
    if quote_status is False:
        logger.error("Enclave quote verification failed")
        return quote_status
    logger.info("Enclave quote verification passed")

    report_sig_status = verify_report_util.verify_ias_report_signature(
        ias_report_cert,
        verification_report,
        proof_signature)
    if report_sig_status is False:
        logger.error("Enclave IAS report signature verification failed")
        return report_sig_status
    logger.info("Enclave IAS report signature verification passed")
    return True
