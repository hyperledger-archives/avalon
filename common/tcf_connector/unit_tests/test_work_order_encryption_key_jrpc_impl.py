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

import logging
from encodings.hex_codec import hex_encode
import base64
import unittest

from tcf_connector.work_order_jrpc_impl import WorkOrderJRPCImpl

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

class TestWorkOrderEncryptionKeyJRPCImpl(unittest.TestCase):
    def __init__(self, listenerUri):
        super(TestWorkOrderEncryptionKeyJRPCImpl, self).__init__()
    
    def testencryption_key_get(self):
        req_id = 31
        workerId = "0x1234"
        logging.info("Calling encryption_key_get with workerId %s\n lastUsedKeyNonce %s\n \
            tag %s\n requesterId %s\n signatureNonce %s\n, signature %s\n",
            workerId, "", "", self.__work_order_submit_request["requesterId"], "","")
        res = self.__work_order_wrapper.encryption_key_get(workerId, "", "", 
            self.__work_order_submit_request["requesterId"], "","", req_id)
        logging.info("Result: %s\n", res)
        self.assertEqual(res['id'], req_id, "work_order_get_result Response id doesn't match")

    def test_encryption_key_set(self):
        req_id = 32
        workerId = "0x1234"
        logging.info("Calling encryption_key_set with workerId %s\n encryptionKey %s\n \
            encryptionKeyNonce %s\n tag %s\n signatureNonce %s\n signature %s\n",
            workerId, "0x123eff" , "0x1234", "", "", "")
        res = self.__work_order_wrapper.encryption_key_set(workerId, "0x123eff" , "0x1234", 
            "", "", "", req_id)
        logging.info("Result: %s\n", res)
        self.assertEqual(res['id'], req_id, "encryption_key_set Response id doesn't match")
