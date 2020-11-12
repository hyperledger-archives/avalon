#!/usr/bin/env python3

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
import json
import sys
import argparse
from listener.base_jrpc_listener import BaseJRPCListener, parse_bind_url
import verify_report.verify_attestation_report as attestation_util
from jsonrpc.exceptions import JSONRPCDispatchException

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s",
                    level=logging.INFO)


class VerificationService(BaseJRPCListener):
    """
    Listener to handle requests from Clients to verify
    attestion verification request to verify report/quote
    """

    # The isLeaf instance variable describes whether a resource will have
    # children and only leaf resources get rendered. VerificationService
    # Listeneris a leaf.
    # node in the derivation tree and hence isLeaf is required.
    isLeaf = True

    def __init__(self):
        """
        Pass through the rpc methods to the
        constructor of the BaseJRPCListener.
        Parameters :
            rpc_methods - An array of RPC methods to which requests will
                          be dispatched.
        """
        self.VERIFICATION_SUCCESS = 0 
        self.VERIFICATION_FAILED = 1
        rpc_methods = [
            self.VerifyIASAttestationReport,
            self.VerifyDCAPQuote
        ]
        super().__init__(rpc_methods)

    def VerifyIASAttestationReport(self, **params):
        """
        RPC handler method registered with attestation
        verification service to verify IAS AVR.
        Parameters :
            @param params - variable-length argument list
        Returns :
            @returns response - A jrpc response
        """
        try:
            input_json_str = params["raw"]
            input_value_json = json.loads(input_json_str)
            status = attestation_util.verify_ias_attestation_report(
                input_value_json["params"])
            if status:
                msg = "IAS attestation report verification success"
                logging.info(msg)
                code = self.VERIFICATION_SUCCESS
            else:
                msg = "IAS attestation report verification failed"
                logging.error(msg)
                code = self.VERIFICATION_FAILED
        except Exception as ex:
            msg = "Verifying attestation report FAILED with " + \
                str(ex)
            logging.error(msg)
            code = self.VERIFICATION_FAILED

        if code:
            raise JSONRPCDispatchException(
                code,
                msg
            )
        else:
            return {
                "code": code,
                "message": msg
            }

    def VerifyDCAPQuote(self, **params):
        """
        RPC handler method registered with attestation
        verification service to verify DCAP quote.
        Parameters :
            @param params - variable-length argument list
        Returns :
            @returns response - A jrpc response
        """
        #TODO: To be implemented
        return None


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument( '-b',
        '--bind', help='URI to listen for requests ', type=str)
    options = parser.parse_args(args)
    if options.bind:
        host_name, port = parse_bind_url(options.bind)
    else:
        logging.error("Missing bind parameter!")
        sys.exit(-1)
    listener = VerificationService()
    listener.start(host_name, port)
    logging.info("Started attestation verification service listener")

main()
