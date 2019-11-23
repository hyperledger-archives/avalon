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

"""enclave_helper.py

This file defines the Enclave class to simplify integration of the SGX
enclave module into the rest of the tcf flow. Typically, an application
will call the initialize_enclave function first, then will call create_enclave_signup_data.
"""

import random
import logging

import tcf_enclave_bridge as tcf_enclave
import utility.keys as keys

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------
def initialize_enclave(enclave_config):
    """initialize_enclave -- Call the initialization function on the
    enclave module
    """
    return tcf_enclave.initialize_with_configuration(enclave_config)


# -----------------------------------------------------------------
class EnclaveHelper(object):
    """
    Wraps calls to the client for symmetry with the enclave service client
    """

    # -------------------------------------------------------
    @classmethod
    def create_enclave_signup_data(cls, tcf_instance_keys=None):
        """create_enclave_signup_data -- Create enclave signup data

        :param tcf_instance_keys: Object of type TransactionKeys
        """

        if tcf_instance_keys is None:
            tcf_instance_keys = keys.TransactionKeys()

        nonce = '{0:016X}'.format(random.getrandbits(64))
        hashed_identity = tcf_instance_keys.hashed_identity
        logger.debug("tx hashed identity: %s", hashed_identity)
        try:
            enclave_data = tcf_enclave.create_signup_info(hashed_identity, nonce)
        except:
            raise Exception('failed to create enclave signup data')

        enclave_info = dict()
        enclave_info['nonce'] = nonce
        enclave_info['sealed_data'] = enclave_data.sealed_signup_data
        enclave_info['verifying_key'] = enclave_data.verifying_key
        enclave_info['encryption_key'] = enclave_data.encryption_key
        enclave_info['enclave_id'] = enclave_data.verifying_key
        enclave_info['proof_data'] = ''
        if not tcf_enclave.enclave.is_sgx_simulator():
            enclave_info['proof_data'] = enclave_data.proof_data

        return cls(enclave_info, tcf_instance_keys)

    # -------------------------------------------------------
    def __init__(self, enclave_info, tcf_instance_keys):

        # Initialize the keys that can be used later to
        # register the enclave
        self.tcf_instance_keys = tcf_instance_keys

        try:
            self.nonce = enclave_info['nonce']
            self.sealed_data = enclave_info['sealed_data']
            self.verifying_key = enclave_info['verifying_key']
            self.encryption_key = enclave_info['encryption_key']
            self.proof_data = enclave_info['proof_data']
            self.enclave_id = enclave_info['enclave_id']
        except KeyError as ke:
            raise Exception("missing enclave initialization parameter; {}".format(str(ke)))

        self.enclave_keys = keys.EnclaveKeys(self.verifying_key, self.encryption_key)

    # -------------------------------------------------------
    def send_to_sgx_worker(self, encrypted_request):
        """
        Submit workorder request to the SGX Worker enclave

        :param encrypted_request: base64 encoded encrypted workorder request
        """
        return tcf_enclave.send_to_sgx_worker(
            self.sealed_data,
            encrypted_request)

    # -------------------------------------------------------
    def get_enclave_public_info(self):
        """
        Return information about the enclave
        """
        return tcf_enclave.get_enclave_public_info(self.sealed_data)
    # -------------------------------------------------------
