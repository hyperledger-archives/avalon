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
import os
from os.path import exists, realpath

# solcx has solidity compiler with 0.5.x and 0.6.x support
from solcx import compile_source
from web3 import HTTPProvider, Web3

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


class EthereumWrapper():
    """
    Ethereum wrapper class to interact with ethereum blockchain
    deploy compile contract code, deploy contract code, execute contract code
    """

    def __init__(self, config):
        if self.__validate(config):
            # Private key to sign the transaction
            self.__eth_private_key = os.environ["WALLET_PRIVATE_KEY"]
            # Ethereum account address to interact with ethereum network
            self.__eth_account_address = config['ethereum']['eth_account']
            http_provider = config["ethereum"]["eth_http_provider"]
            # Ethereum http provider is endpoint to submit the transaction
            self.__w3 = Web3(HTTPProvider(http_provider))
            # Chain id signifies the which ethereum network to use:
            # test net/main ethereum network
            self.__channel_id = config["ethereum"]["chain_id"]
            # Maximum amount of gas you’re willing to spend on
            # a particular transaction
            self.__gas_limit = config["ethereum"]["gas_limit"]
            # Amount of Ether you’re willing to pay for every unit of gas
            self.__gas_price = config["ethereum"]["gas_price"]
        else:
            raise Exception("Invalid configuration parameter")

    def __validate(self, config):
        """
        validates parameter from config parameters for existence.
        Returns false if validation fails and true if it success
        """
        if os.environ["WALLET_PRIVATE_KEY"] is None:
            logging.error("Ethereum account private key is not set!!")
            return False
        if config["ethereum"]["eth_account"] is None:
            logging.error("Missing ethereum account id!!")
            return False
        if config["ethereum"]["chain_id"] is None:
            logging.error("Missing chain id in config!!")
            return False
        if config["ethereum"]["eth_http_provider"] is None:
            logging.error("Missing ethereum http provider url!!")
            return False
        if config["ethereum"]["gas_limit"] is None:
            logging.error("Missing parameter gas limit")
            return False
        if config["ethereum"]["gas_price"] is None:
            logging.error("Missing parameter gas price")
            return False
        return True

    def compile_source_file(self, file_path):
        """
        Compile solidity contract file and returns contract instance object
        """
        if not exists(file_path):
            raise FileNotFoundError(
                "File not found at path: {0}".format(realpath(file_path)))
        with open(file_path, 'r') as f:
            source = f.read()
        return compile_source(source)

    def deploy_contract(self, contract_interface):
        """
        Deploys solidity contract to ethereum network identified by chain_id
        returns contract address
        """
        acct = self.__w3.eth.account.privateKeyToAccount(
            self.__eth_private_key)
        contract_object = self.__w3.eth.contract(
            abi=contract_interface['abi'],
            bytecode=contract_interface['bin'])
        nonce = self.__w3.eth.getTransactionCount(self.__eth_account_address,
                                                  'pending')
        tx_hash = contract_object.constructor().buildTransaction({
            'from': acct.address,
            'chainId': self.__channel_id,
            'gas': self.__gas_limit,
            'gasPrice': self.get_gas_price(),
            'nonce': nonce
        })
        address = \
            self.execute_transaction(tx_hash)['txn_receipt']['contractAddress']
        return address

    def execute_transaction(self, tx_dict):
        """
        Sign the raw transaction with private key, send it
        and wait for receipts
        Returns transaction receipt on success or None on error.
        """
        signed_txn = self.__w3.eth.account.signTransaction(
            tx_dict, private_key=self.__eth_private_key)
        tx_hash = self.__w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        tx_receipt = self.__w3.eth.waitForTransactionReceipt(
            tx_hash.hex(), 120)
        logging.info("executed transaction hash: %s, receipt: %s",
                     format(tx_hash.hex()), format(tx_receipt))
        return tx_receipt

    def get_channel_id(self):
        return self.__channel_id

    def get_gas_limit(self):
        return self.__gas_limit

    def get_gas_price(self):
        return self.__w3.toWei(self.__gas_price, "gwei")

    def get_contract_instance(self, contract_file_name, contract_address):
        compiled_sol = self.compile_source_file(contract_file_name)
        contract_id, contract_interface = compiled_sol.popitem()
        return self.__w3.eth.contract(address=contract_address,
                                      abi=contract_interface["abi"])

    def get_txn_nonce(self):
        return self.__w3.eth.getTransactionCount(self.__eth_account_address)

    def get_transaction_params(self):
        """
        Method to construct a dictionary with required parameters
        to submit the transaction
        Return dict containing chain id, gas, gas limit and nonce.
        """
        return {
            "chainId": self.get_channel_id(),
            "gas": self.get_gas_limit(),
            "gasPrice": self.get_gas_price(),
            "nonce": self.get_txn_nonce()
        }
