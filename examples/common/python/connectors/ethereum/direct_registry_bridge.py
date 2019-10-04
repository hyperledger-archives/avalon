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

''' this Component acts as bridge between smart contract deployed in blockchain and KV storage'''


from shared_kv.shared_kv_interface import KvStorage
from connectors.ethereum.ethereum_worker_registry_list_impl import \
    EthereumWorkerRegistryListImpl as registry
from utility.tcf_types import RegistryStatus

import toml
from os.path import dirname, join, abspath
import logging
import json
import time
import argparse
from os import urandom, environ
import sys
import os

sys.path.insert(0, abspath(join(dirname(__file__), '..')) + '/tcf_connector/')


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def str_list_to_bytes_list(str_list):
    bytes_list = []
    for str in str_list:
        bytes_list.append(bytes.fromhex(str))
    return bytes_list


def bytes_list_to_str_list(bytes_list):
    str_list = []
    for byte in bytes_list:
        str_list.append(byte.hex())
    return str_list


def create_json_object(org_id, registry, status):
    logger.debug("create_json_object id: %s, registry: %s",
                 org_id.hex(), registry)
    registry_info = dict()
    # registry[0] contains registryType which symbolizes if registry present ( value equals to 1).
    registry_info["orgId"] = org_id.hex()
    registry_info["uri"] = registry[0]
    registry_info["scAddress"] = registry[1].hex()
    app_ids_bytes = registry[2]  # list of application ids
    logger.debug("app_ids_bytes %s", app_ids_bytes)
    app_ids_list = bytes_list_to_str_list(app_ids_bytes)
    registry_info["appTypeIds"] = app_ids_list
    registry_info["status"] = status.value
    logger.debug("registry_info %s", registry_info)

    json_registry = json.dumps(registry_info)
    logger.debug("JSON serialized registry %s is %s", org_id.hex(), json_registry)
    return json_registry


def deserialize_json_object(json_reg_info):
    reg_info = json.loads(json_reg_info)
    uri = reg_info["uri"]
    sc_address = bytes.fromhex(reg_info["scAddress"])
    app_ids_str = reg_info["appTypeIds"]

    # Convert list of appTypeIds of type string to bytes
    app_ids_bytes = str_list_to_bytes_list(app_ids_str)

    return uri, sc_address, app_ids_bytes


def sync_contract_and_lmdb(eth_direct_registry, kv_storage):
    # Check if all registries in smart contract are available in KvStorage, if not add them
    eth_lookup_result = eth_direct_registry.registry_lookup()
    # last value of lookup will be list of registry id's/org id's
    org_id_list = eth_lookup_result[-1]

    logger.info("Syncing registries from Contract to KvStorage")
    if not org_id_list:
        logger.info("No registries available in Direct registry contract")

    else:
        for org_id in org_id_list:
            eth_reg_info = eth_direct_registry.registry_retrieve(org_id)
            logger.debug("eth_reg_info: %s", eth_reg_info)
            # Check if registry entry present in KvStorage
            logger.info(
                "Check if registry with id %s present in KvStorage", org_id.hex())
            kv_reg_info = kv_storage.get("registries", org_id)
            if not kv_reg_info:
                logger.info(
                    "No matching registry found in KvStorage, ADDING it to KvStorage")
                # Create JSON registry object with status 0 equivalent to SUSPENDED
                json_registry = create_json_object(org_id, eth_reg_info, RegistryStatus.SUSPENDED)
                kv_storage.set("registries", org_id.hex(), json_registry)

            else:
                logger.info(
                    "Matching registry found in KvStorage, hence ADDING")
                # Set the status of registry to ACTIVE
                kv_registry = json.loads(kv_reg_info)
                kv_registry["status"] = 1      # status = 1 implies ACTIVE
                kv_storage.set("registries", org_id.hex(),
                               json.dumps(kv_registry))

    logger.info("Syncing registries from KvStorage to Contract")
    # Check if all registries present in KvStorage are available in Smart contract, if not add them
    kv_registry_list = kv_storage.lookup("registries")

    if not kv_registry_list:
        logger.info("No registries available in KvStorage")

    else:
        for kv_registry_id in kv_registry_list:
            kv_reg_info = kv_storage.get("registries", kv_registry_id)
            # Check if registry entry present in smart contract
            logger.debug(
                "found registry_retrieve: %s from kv store", kv_registry_id)
            retrieve_result = eth_direct_registry.registry_retrieve(
                bytes.fromhex(kv_registry_id))

            if retrieve_result[0] == 0:
                logger.info(
                    "Matching registry with id %s not found in Smart contract, hence ADDING", kv_registry_id)
                reg_info = deserialize_json_object(kv_reg_info)
                # Add registry to smart contract and set status to ACTIVE
                eth_direct_registry.registry_add(
                    bytes.fromhex(kv_registry_id), reg_info[0], reg_info[1], reg_info[2])
                eth_direct_registry.registry_set_status(
                    bytes.fromhex(kv_registry_id), RegistryStatus.ACTIVE)

            else:
                # Set status of registry to registry status in KvStorage
                logger.info(
                    "Matching registry %s found in Smart contract, CHANGING status", kv_registry_id)
                eth_direct_registry.registry_set_status(
                    bytes.fromhex(kv_registry_id), RegistryStatus.ACTIVE) # TODO

        logger.info(
            "-------------- Direct Registry bridge flow complete ------------------- ")
    return


def main(args=None):
    logger.info("Starting synchronization between Smart contract and KvStorage.")

    # Smart contract address is the address where smart contract is deployed.
    # TODO: Add mechanism to read the address from config file.
    tcf_home = environ.get("TCF_HOME", "../../")
    config_file = tcf_home + "/examples/common/python/connectors/" + "tcf_connector.toml"
    with open(config_file) as fd:
        config = toml.load(fd)
    eth_direct_registry = registry(config)
    kv_storage = KvStorage()
    kv_storage.open("kv_storage")

    while True:
        sync_contract_and_lmdb(eth_direct_registry, kv_storage)
        logger.info("Direct registry bridge is Sleeping off..")
        time.sleep(10)


if __name__ == '__main__':
    main()
