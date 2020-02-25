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
from solcx import compile_source, set_solc_version, get_solc_version
from urllib.parse import urlparse
import web3
import json

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

PROVIDER_DICT = {
    'http':  web3.HTTPProvider,
    'https': web3.HTTPProvider,
    'ws':    web3.WebsocketProvider,
    'wss':   web3.WebsocketProvider,
    'ipc':   web3.IPCProvider,
}


class EthereumWrapper():
    """
    Ethereum wrapper class to interact with ethereum blockchain
    deploy compile contract code, deploy contract code, execute contract code
    """

    def __init__(self, config):
        if self.__validate(config):
            # Ethereum account address to interact with ethereum network
            self.__eth_account_address = config['ethereum']['eth_account']
            provider = config["ethereum"]["provider"]
            # Ethereum provider is endpoint to submit the transaction
            self.__w3 = self._get_provider_for_url(provider)
            event_provider = config["ethereum"]["event_provider"]
            # Ethereum provider is endpoint to submit the transaction
            self.__w3_event = self._get_provider_for_url(event_provider)
            self._is_ropsten_provider = self._is_ropsten(provider)
            # Private key to sign the transaction
            if self._is_ropsten_provider:
                self.__eth_private_key = config['ethereum']['acc_pvt_key']
            # Chain id signifies the which ethereum network to use:
            # test net/main ethereum network
            self._chain_id = config["ethereum"]["chain_id"]
            # Maximum amount of gas you’re willing to spend on
            # a particular transaction
            self.__gas_limit = config["ethereum"]["gas_limit"]
            # Amount of Ether you’re willing to pay for every unit of gas
            self.__gas_price = config["ethereum"]["gas_price"]
            set_solc_version(config['ethereum']['solc_version'])
            logging.info("Solidity compiler version being used : {}"
                         .format(get_solc_version()))
        else:
            raise Exception("Invalid configuration parameter")

    def _get_provider_for_url(self, url):
        return web3.Web3(PROVIDER_DICT[urlparse(url).scheme](url))

    def _is_ropsten(self, url):
        """
        This function checks if the url passed is one for ropsten network
        """
        loc = urlparse(url).netloc.lower()
        if "ropsten" in loc:
            return True
        else:
            return False

    def __validate(self, config):
        """
        validates parameter from config parameters for existence.
        Returns false if validation fails and true if it success
        """

        if config["ethereum"]["eth_account"] is None:
            logging.error("Missing ethereum account id!!")
            return False
        if config["ethereum"]["chain_id"] is None:
            logging.error("Missing chain id in config!!")
            return False
        if config["ethereum"]["provider"] is None:
            logging.error("Missing ethereum provider url!!")
            return False
        if config["ethereum"]["gas_limit"] is None:
            logging.error("Missing parameter gas limit")
            return False
        if config["ethereum"]["gas_price"] is None:
            logging.error("Missing parameter gas price")
            return False
        provider = config["ethereum"]["provider"]
        if self._is_ropsten(provider):
            try:
                config['ethereum']['acc_pvt_key']
            except KeyError:
                logging.error("Ethereum account private key is not set!!\
                    Cannot sign transactions.")
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
        tx_dict = contract_object.constructor().buildTransaction({
            'from': acct.address,
            'chainId': self._chain_id,
            'gas': self.__gas_limit,
            'gasPrice': self.get_gas_price(),
            'nonce': nonce
        })
        address = \
            self.sign_execute_raw_transaction(tx_dict)
        ['txn_receipt']['contractAddress']
        return address

    def sign_execute_raw_transaction(self, tx_dict):
        """
        Sign the raw transaction with private key, send it
        and wait for receipts
        Returns transaction receipt on success or None on error.
        """
        signed_tx = self.__w3.eth.account.signTransaction(
            tx_dict, private_key=self.__eth_private_key)
        tx_hash = self.__w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        tx_receipt = self.__w3.eth.waitForTransactionReceipt(
            tx_hash.hex(), 120)
        logging.info("executed transaction hash: %s, receipt: %s",
                     format(tx_hash.hex()), format(tx_receipt))
        return tx_receipt

    def execute_unsigned_transaction(self, tx_dict):
        """
        Send transaction to be executed only with account address
        and wait for receipts
        Returns transaction receipt on success or None on error.
        """
        tx_hash = self.__w3.eth.sendTransaction(tx_dict)
        tx_receipt = self.__w3.eth.waitForTransactionReceipt(tx_hash)
        logging.info("executed transaction hash: %s, receipt: %s",
                     format(tx_hash.hex()), format(tx_receipt))
        return tx_receipt

    def execute_transaction(self, tx_dict):
        """
        Wrapper function to choose appropriate function to execute
        transaction based on provider(ropsten vs other)
        """
        if self._is_ropsten_provider:
            return self.sign_execute_raw_transaction(tx_dict)
        else:
            return self.execute_unsigned_transaction(tx_dict)

    def get_chain_id(self):
        return self._chain_id

    def get_gas_limit(self):
        return self.__gas_limit

    def get_gas_price(self):
        return self.__w3.toWei(self.__gas_price, "gwei")

    def get_account_address(self):
        return self.__eth_account_address

    def get_contract_instance(self, contract_file_name, contract_address):
        """
        This function returns 2 contract instances, first meant for committing
        transactions or reading from blockchain. The second one is specifically
        meant for event listening.
        """
        compiled_sol = self.compile_source_file(contract_file_name)
        contract_id, contract_interface = compiled_sol.popitem()

        return self.__w3.eth.contract(address=contract_address,
                                      abi=contract_interface["abi"]),\
            self.__w3_event.eth.contract(address=contract_address,
                                         abi=contract_interface["abi"])

    def get_contract_instance_from_json(self, json_file_name,
                                        contract_address):
        """
        Method to get contract ABI from a JSON file
        """
        return self.__w3.eth.contract(
            address=contract_address,
            abi=json.load(open(json_file_name)).get('abi'),
            ContractFactoryClass=web3.contract.Contract)

    def get_txn_nonce(self):
        return self.__w3.eth.getTransactionCount(web3.Web3.toChecksumAddress(
            self.__eth_account_address))

    def get_transaction_params(self):
        """
        Method to construct a dictionary with required parameters
        to submit the transaction
        Return dict containing chain id, gas, gas limit and nonce.
        """
        # Ropsten accepts only raw transactions & chain id is fixed
        if self._is_ropsten_provider:
            return {
                "from": self.get_account_address(),
                "chainId": self.get_chain_id(),
                "gas": self.get_gas_limit(),
                "gasPrice": self.get_gas_price(),
                "nonce": self.get_txn_nonce()
            }
        else:
            return {
                "from": web3.Web3.toChecksumAddress(
                    self.get_account_address()),
                "gas": self.get_gas_limit(),
                "gasPrice": self.get_gas_price(),
                "nonce": self.get_txn_nonce()
            }

    def get_bytes_from_hex(self, hex_str):
        """
        Method to convert hex string to bytes
        """
        return web3.Web3.toBytes(hexstr=hex_str)


def get_keccak_for_text(method_sign):
    """
    Method to get the keccak hash of a method signature.
    The HexBytes is converted to str and returned.
    """
    return web3.Web3.keccak(text=method_sign).hex()
