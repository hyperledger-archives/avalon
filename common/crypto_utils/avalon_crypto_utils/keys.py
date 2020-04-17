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

import hashlib
import avalon_crypto_utils.crypto.crypto as crypto

import logging
logger = logging.getLogger(__name__)


class EnclaveKeys(object):
    """
    Wrapper for managing the enclave's keys, the verifying_key is an
    ECDSA public key used to verify enclave signatures, the
    encryption_key is an RSA public key for encrypting message to the
    enclave.
    """

    # -------------------------------------------------------
    def __init__(self, verifying_key, encryption_key):
        """
        Initialize the object

        :param verifying_key: PEM encoded ECDSA verifying key
        :param encryption_key: PEM encoded RSA encryption key
        """
        self._verifying_key = crypto.SIG_PublicKey(verifying_key)
        self._encryption_key = crypto.PKENC_PublicKey(encryption_key)

    # -------------------------------------------------------
    @property
    def identity(self):
        return self._verifying_key.Serialize()

    # -------------------------------------------------------
    @property
    def hashed_identity(self):
        return hashlib.sha256(self.identity.encode('utf8')).hexdigest()[:16]
