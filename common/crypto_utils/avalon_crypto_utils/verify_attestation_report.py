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
import uuid
import logging
from http_client.http_jrpc_client import HttpJrpcClient
logger = logging.getLogger(__name__)


def verify_attestation_report(enclave_info, uri):
    '''
    Function to verify quote status, signature of IAS attestation report
    @params enclave_info - dict containing attestation report
    @params uri is end point of avalon attestation service
    '''

    uri_client = HttpJrpcClient(uri)
    # uuid4 generates random uuid and fetching
    # field time_hi_version which is 16bits length
    verify_report_req = {
        "jsonrpc": "2.0",
        "id": uuid.uuid4().fields[2],
        "params": enclave_info,
        "method": "VerifyIASAttestationReport"
    }
    json_request_str = json.dumps(verify_report_req)
    try:
        response = uri_client._postmsg(json_request_str)
    except Exception as err:
        logger.error(
            "Exception occurred in communication with Attestation Service")
        raise err
    logger.info("Response from Attestation service %s", response)

    if "result" in response:
        # Response has jrpc code is 0 on success and 1 on failure
        if response["result"]["code"]:
            return False
        else:
            return True
    else:
        return False
