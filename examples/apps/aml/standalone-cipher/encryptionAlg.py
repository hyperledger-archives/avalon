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

from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes


class encAlgorithm(object):

    def encrypt_data(self, data, encryption_key, iv):

        cipher = AES.new(bytes(encryption_key), AES.MODE_GCM, bytes(iv))
        ciphered_data, tag = cipher.encrypt_and_digest(bytes(data))

        ciphered_data_list = []
        tag_list = []

        for i in range(0, len(ciphered_data)):
            ciphered_data_list.append(ciphered_data[i])

        for j in range(0, len(tag)):
            tag_list.append(tag[j])

        return_list = ciphered_data_list + tag_list

        return tuple(return_list)

    def generateKey(self):
        self.key = get_random_bytes(32)

        key_list = []

        for i in range(0, len(self.key)):
            key_list.append(self.key[i])

        return tuple(key_list)
