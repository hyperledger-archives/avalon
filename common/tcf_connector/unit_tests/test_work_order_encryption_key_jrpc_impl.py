import logging
from encodings.hex_codec import hex_encode
import base64
import unittest
from os import path, environ
import errno
import toml
import secrets


from tcf_connector.work_order_encryption_key_jrpc_impl import WorkOrderEncryptionKeyJrpcImpl

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class TestWorkOrderEncryptionKeyJRPCImpl(unittest.TestCase):
    def __init__(self, config_file):
        super(TestWorkOrderEncryptionKeyJRPCImpl, self).__init__()
        if not path.isfile(config_file):
            raise FileNotFoundError("File not found at path: {0}".format(path.realpath(config_file)))
        try:
            with open(config_file) as fd:
                self.__config = toml.load(fd)
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise Exception('Could not open config file: %s',e)
        self.__wo_enc_updater = WorkOrderEncryptionKeyJrpcImpl(self.__config)

    
    def test_encryption_key_get(self):
        req_id = 31
        self.__workerId = secrets.token_hex(32)
        self.__last_used_key_nonce = secrets.token_hex(32)
        self.__tag = secrets.token_hex(32)
        self.__requester_id = secrets.token_hex(32)
        self.__signature_nonce = secrets.token_hex(32)
        self.__signature = secrets.token_hex(32)

        logging.info("Calling encryption_key_get with workerId %s\n lastUsedKeyNonce %s\n \
            tag %s\n requesterId %s\n signatureNonce %s\n, signature %s\n",
            self.__workerId, self.__last_used_key_nonce, self.__tag,
            self.__requester_id, self.__signature_nonce, self.__signature)
        res = self.__wo_enc_updater.encryption_key_get(self.__workerId,
            self.__last_used_key_nonce,
            self.__tag, self.__requester_id,
            self.__signature_nonce,
            self.__signature,
            req_id
        )
        logging.info("Result: %s\n", res)
        self.assertEqual(res['id'], req_id, "work_order_get_result Response id doesn't match")

    def test_encryption_key_set(self):
        req_id = 32
        workerId = "0x1234"
        logging.info("Calling encryption_key_set with workerId %s\n encryptionKey %s\n \
            encryptionKeyNonce %s\n tag %s\n signatureNonce %s\n signature %s\n",
            self.__workerId, self.__last_used_key_nonce, self.__tag, self.__requester_id,
            self.__signature_nonce,self.__signature)

        res = self.__wo_enc_updater.encryption_key_set(self.__workerId,
            self.__last_used_key_nonce,
            self.__tag, self.__requester_id,
            self.__signature_nonce,
            self.__signature,
            req_id
        )
        logging.info("Result: %s\n", res)
        self.assertEqual(res['id'], req_id, "encryption_key_set Response id doesn't match")


def main():
    logging.info("Running test cases...\n")
    tcf_home = environ.get("TCF_HOME", "../../")
    test = TestWorkOrderEncryptionKeyJRPCImpl(tcf_home + "/common/tcf_connector/" + "tcf_connector.toml")
    test.test_encryption_key_get()
    test.test_encryption_key_set()


if __name__ == "__main__":
    main()

