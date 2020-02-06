#! /usr/bin/env python3

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

import toml
import errno
import logging
import os
from os.path import exists, realpath

from avalon_sdk.ethereum.ethereum_wrapper \
    import EthereumWrapper as ethereum_wrapper

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


class eth_cli:
    def __init__(self, config_file):
        if not os.path.isfile(config_file):
            raise FileNotFoundError(
                "File not found at path: {0}".format(realpath(config_file)))
        try:
            with open(config_file) as fd:
                self.__config = toml.load(fd)
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise Exception('Could not open config file: %s' % e)
        logging.info('config data %s', self.__config)
        if self.__config['ethereum']['direct_registry_contract_file'] is None:
            raise Exception("Missing direct registry contract file path!!")
        if self.__config['ethereum']['worker_registry_contract_file'] is None:
            raise Exception("Missing worker registry contract file path!!")
        self.__eth_client = ethereum_wrapper(self.__config)

    def deploy_contracts(self):
        tcf_home = os.environ.get("TCF_HOME", "../../")
        self.deploy_solidity_contract(
            tcf_home + "/" +
            self.__config['ethereum']['direct_registry_contract_file'])
        self.deploy_solidity_contract(
            tcf_home + "/" +
            self.__config['ethereum']['worker_registry_contract_file'])

    def deploy_solidity_contract(self, contract_file):
        if not exists(contract_file):
            raise FileNotFoundError("File not found at path: {0}".format(
                realpath(contract_file)))
        compiled_sol = self.__eth_client.compile_source_file(contract_file)
        contract_id, contract_interface = compiled_sol.popitem()
        address = self.__eth_client.deploy_contract(contract_interface)
        logging.info("Deployed %s to: %s\n", contract_id, address)
        return {"status": "success"}


def main():
    tcf_home = os.environ.get("TCF_HOME", "../../")
    eth = eth_cli(tcf_home +
                  "/sdk/avalon_sdk/" + "tcf_connector.toml")
    eth.deploy_contracts()

if __name__ == '__main__':
    main()
