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

from abc import ABC, abstractmethod


class WorkOrderEncryptionKeyInterface(ABC):
    """
    WorkOrderRegistryInterface is an abstract base class that contains
    abstract APIs to manage work orders
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def encryption_key_get(self, worker_id, last_used_key_nonce, tag,
                           requester_id, signature_nonce, signature, id=None):
        """
        Get Encryption Key Request Payload
        Inputs
        1. worker_id is an id of the worker to retrieve an encryption key for.
        2. last_used_key_nonce is an optional nonce associated with the
        last key retrieved.
        If it is provided, the key retrieved should be newer than this one.
        Otherwise any key can be retrieved.
        3. tag is tag that should be associated with the returned key,
        e.g. requester id. This is an optional parameter. If it is not
        provided, requesterId below is used as a key.
        4. requester_id is an id of the requester that plans to use the
        returned key to submit one or more work orders using this key.
        5. signature_nonce is an optional parameter and is used only if
        the following signature is also provided.
        6. signature is an optional signature of concatenated workerId,
        lastUsedKeyNonce, tag, and signatureNonce.
        The hashing and signing algorithms are defined in hashingAlgorithm
        and encryptionAlgorithm for the Worker

        Output
        1. worker_id is an id of the worker that created the encryption key.
        2. encryption_key is an encryption key.
        3. encryption_key_nonce is a nonce associated with the key.
        4. tag is tag associated with the key.
        5. signature is a signature generated by the worker.
        The hashing and signing algorithms are defined in hashingAlgorithm and
        encryptionAlgorithm for the worker as defined in section
        Common Data for All Worker Types.
        The signature is calculated as follows:
            -> a hash is calculated over the concatenation of workerId,
               encryptionKey, encryptionKeyNonce, and tag.
            -> the hash is signed by the worker's signing key corresponding to
               verificationKey defined in Appendix A.
            -> the hash is formatted as BASE64 string.

        """
        pass

    @abstractmethod
    def encryption_key_get(self, worker_id, encryption_key,
                           encryption_key_nonce, tag, signature_nonce,
                           signature, id=None):
        """
        Set Encryption Key Request Payload
        input parameters are same as encryption_key_get.

        """
        pass
