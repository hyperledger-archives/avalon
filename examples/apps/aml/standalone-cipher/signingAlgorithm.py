# Copyright 2019 Banco Santander S.A.
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

from ellipticcurve.ecdsa import Ecdsa
from ellipticcurve.privateKey import PrivateKey
import signature
import base64


class signAlgorithm(object):

    def loadKey(self, key_str):
        self.privateKey = PrivateKey.fromPem(key_str)

    def getPublicKey(self):
        return self.privateKey.publicKey()

    def getPublicKeySerialized(self):
        return self.privateKey.publicKey().toPem()

    def sign_message(self, hash_t):

        # Bytearray to base64
        hash_b_arr = bytearray(list(hash_t))
        hash_b64 = base64.b64encode(hash_b_arr)
        hash_b64_str = str(hash_b64, 'utf-8')

        signed = Ecdsa.sign(hash_b64_str, self.privateKey)

        return signed

    def verify_signature(self, hash_b64_str, decoded_signature, verify_key):
        return Ecdsa.verify(
            hash_b64_str, decoded_signature, verify_key)
