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

from utility.hex_utils import is_valid_hex_str
import binascii
from os import environ

from avalon_client_sdk.interfaces.worker_registry_list_client \
    import WorkerRegistryListClient
from avalon_client_sdk.ethereum.ethereum_wrapper import EthereumWrapper
from avalon_client_sdk.utility.utils import construct_message
from avalon_client_sdk.utility.tcf_types import RegistryStatus

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class EthereumWorkerRegistryListClientImpl(WorkerRegistryListClient):
    """
    This class is to read worker registries entries from Ethereum.
    Implements WorkerRegistryListClient interface
    """
    lookup_page_size = 20 # Assigning a default size if config absent

    def __init__(self, config):
        if self.__validate(config):
            self.__initialize(config)
        else:
            raise Exception("Invalid or missing config parameter")

    def registry_add(self, org_id, uri, sc_addr, app_type_ids):
        if (self.__contract_instance is not None):
            if (is_valid_hex_str(binascii.hexlify(org_id).decode("utf8"))
                    is False):
                logging.info("Invalid Org id {}".format(org_id))
                return construct_message("failed", "Invalid Org id")
            if (sc_addr is not None and is_valid_hex_str(
                    binascii.hexlify(sc_addr).decode("utf8")) is False):
                logging.info("Invalid smart contract address {}")
                return construct_message(
                    "failed", "Invalid smart contract address")
            if (not uri):
                logging.info("Empty uri {}".format(uri))
                return construct_message("failed", "Empty uri")
            for aid in app_type_ids:
                if (is_valid_hex_str(binascii.hexlify(aid).decode("utf8"))
                        is False):
                    logging.info("Invalid application id {}".format(aid))
                    return construct_message(
                        "failed", "Invalid application id")

            txn_hash = self.__contract_instance.functions.registryAdd(
                org_id, uri, org_id, app_type_ids).buildTransaction(
                    {
                        "chainId": self.__eth_client.get_channel_id(),
                        "gas": self.__eth_client.get_gas_limit(),
                        "gasPrice": self.__eth_client.get_gas_price(),
                        "nonce": self.__eth_client.get_txn_nonce()
                    })
            tx = self.__eth_client.execute_transaction(txn_hash)
            return tx
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return construct_message(
                "failed",
                "direct registry contract instance is not initialized")

    def registry_update(self, org_id, uri, sc_addr, app_type_ids):
        if (self.__contract_instance is not None):
            if (is_valid_hex_str(binascii.hexlify(org_id).decode("utf8"))
                    is False):
                logging.error("Invalid Org id {}".format(org_id))
                return construct_message("failed", "Invalid Org id")
            if (sc_addr is not None and is_valid_hex_str(
                    binascii.hexlify(sc_addr).decode("utf8")) is False):
                logging.error(
                    "Invalid smart contract address {}".format(sc_addr))
                return construct_message(
                    "failed", "Invalid smart contract address")
            if (not uri):
                logging.error("Empty uri {}".format(uri))
                return construct_message("failed", "Empty uri")
            for aid in app_type_ids:
                if (is_valid_hex_str(binascii.hexlify(aid).decode("utf8"))
                        is False):
                    logging.error("Invalid application id {}".format(aid))
                    return construct_message(
                        "failed", "Invalid application id")

            txn_hash = self.__contract_instance.functions.registryUpdate(
                org_id, uri, sc_addr,
                app_type_ids).buildTransaction(
                {
                    "chainId": self.__eth_client.get_channel_id(),
                    "gas": self.__eth_client.get_gas_limit(),
                    "gasPrice": self.__eth_client.get_gas_price(),
                    "nonce": self.__eth_client.get_txn_nonce()
                })
            tx = self.__eth_client.execute_transaction(txn_hash)
            return tx
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return construct_message(
                "failed",
                "direct registry contract instance is not initialized")

    def registry_set_status(self, org_id, status):
        if (self.__contract_instance is not None):
            if (is_valid_hex_str(binascii.hexlify(org_id).decode("utf8"))
                    is False):
                logging.info("Invalid Org id {}".format(org_id))
                return construct_message("failed", "Invalid argument")
            if not isinstance(status, RegistryStatus):
                logging.info("Invalid registry status {}".format(status))
                return construct_message(
                    "failed", "Invalid worker status {}".format(status))
            txn_hash = self.__contract_instance.functions.registrySetStatus(
                org_id,
                status.value).buildTransaction(
                {"chainId": self.__eth_client.get_channel_id(),
                 "gas": self.__eth_client.get_gas_limit(),
                 "gasPrice": self.__eth_client.get_gas_price(),
                 "nonce": self.__eth_client.get_txn_nonce()})
            tx = self.__eth_client.execute_transaction(txn_hash)
            return tx
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return construct_message(
                "failed",
                "direct registry contract instance is not initialized")

    def registry_lookup(self, app_type_id=None):
        return self.__registry_lookup(app_type_id, None, False)

    def registry_lookup_next(self, app_type_id, lookup_tag):
        return self.__registry_lookup(app_type_id, lookup_tag, True)

    def __registry_lookup(self, app_type_id=None, lookup_tag=None, lookup_next=False):
        """
        This function handles both the lookup & lookup_next calls. It looks
        for the flag, lookup_next, which if enabled, it would discard all
        entries in the result set until the look_up tag. It paginates results
        post this and returns it as the next page.
        """

        if (self.__contract_instance is not None):
            if app_type_id is not None:
                if is_valid_hex_str(binascii.hexlify(app_type_id).decode(
                        "utf8")):
                    lookup_result = \
                        self.__contract_instance.functions.registryLookUp(
                            app_type_id).call()
                else:
                    logging.info(
                        "Invalid application type id {}".format(app_type_id))
                    return construct_message(
                        "failed", "Invalid application type id")
            else:
                lookup_result = \
                    self.__contract_instance.functions.registryLookUp(b"") \
                    .call()
            w_count, lookup_string, w_list = lookup_result
            if lookup_next:
                residue_list = []
                for reg in w_list:
                    # Keep iterating to look for ordId(from where next 
                    # pages commences) matching lookup_tag. Once a match
                    # is found, rest of the results are candidate for next
                    # page(including the match) 
                    if reg.orgId != lookup_tag:
                        w_count -= 1
                        continue
                    residue_list.append(reg)
                w_list = residue_list

            # Create a result_list of size lookup_page_size
            # and update lookup_string expected in next call
            # to registry_lookup_next
            result_list = []
            if w_count > self.lookup_page_size:
                count = 0;
                for reg in w_list:
                    if count == self.lookup_page_size:
                        lookup_string = reg.orgId
                        break
                    result_list.append(reg)
                    count += 1
            else:
                lookup_string = 0
            return (w_count, lookup_string, result_list)
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return construct_message(
                "failed",
                "direct registry contract instance is not initialized")

    def registry_retrieve(self, org_id):
        if (self.__contract_instance is not None):
            if (is_valid_hex_str(binascii.hexlify(org_id).decode("utf8"))
                    is False):
                logging.info("Invalid Org id {}".format(org_id))
                return construct_message("failed", "Invalid Org id")
            else:
                registryDetails = \
                    self.__contract_instance.functions.registryRetrieve(
                        org_id).call()
                return registryDetails
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return construct_message(
                "failed",
                "direct registry contract instance is not initialized")

    def __validate(self, config):
        """
        validates parameter from config parameters for existence.
        Returns false if validation fails and true if it success
        """
        if config["ethereum"]["direct_registry_contract_file"] is None:
            logging.error("Missing direct registry contract file path!!")
            return False
        if config["ethereum"]["direct_registry_contract_address"] is None:
            logging.error("Missing direct registry contract address!!")
            return False
        return True

    def __initialize(self, config):
        """
        Initialize the parameters from config to instance variables.
        """
        self.__eth_client = EthereumWrapper(config)
        tcf_home = environ.get("TCF_HOME", "../../../")
        contract_file_name = tcf_home + "/" + \
            config["ethereum"]["direct_registry_contract_file"]
        contract_address = \
            config["ethereum"]["direct_registry_contract_address"]
        self.__contract_instance = self.__eth_client.get_contract_instance(
            contract_file_name, contract_address
        )
        config_lookup_size = config["tcf"]["lookup_page_size"]
        if config_lookup_size is not None:
            self.lookup_page_size = config_lookup_size
