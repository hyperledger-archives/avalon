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

import os
import sys
from os.path import dirname, join, abspath
from os import urandom
import json
import logging

from shared_kv.shared_kv_interface import KvStorage
import connectors.ethereum.direct_registry_bridge as registry_helper

from connectors.ethereum.ethereum_worker_registry_list_impl \
    import EthereumWorkerRegistryListImpl as dir_registry

sys.path.insert(0, abspath(join(dirname(__file__), '../..')) + '/connectors/')

logger = logging.getLogger(__name__)


def create_json_object(org_id, uri, sc_address, app_type_ids, status):
    registry_info = dict()
    registry_info["orgId"] = org_id
    registry_info["uri"] = uri
    registry_info["scAddress"] = sc_address
    registry_info["appTypeIds"] = app_type_ids
    registry_info["status"] = status

    json_registry = json.dumps(registry_info)
    logger.debug("JSON serialized registry is %s", json_registry)

    return json_registry


def test_sync_to_lmdb(eth_direct_registry, kv_storage):
    org_id = "0x11223344".encode()
    uri = "http://registry-1:8008"
    sc_address = "0xABC123"
    app_type_ids = ["0x12AB".encode(), "0x34CD".encode()]

    # Add dummy registry to smart contract
    logger.info("Adding sample registry to Smart Contract")
    result = eth_direct_registry.RegistryAdd(org_id, uri, sc_address, app_type_ids)
    logger.info("Registry add status - %s", result)

    registry_helper.sync_contract_and_lmdb(eth_direct_registry, kv_storage)

    # Verify Registry status is set to SUSPENDED in KvStorage
    logger.info("Check if registry status is set to SUSPENDED in KvStorage")
    reg_info = kv_storage.get("registries", org_id.decode())
    logger.info("registry fetched from LMDB - %s", reg_info)
    if reg_info is not None:
        json_reg_info = json.loads(reg_info)
        if json_reg_info["status"] == 0:
            logger.info("Syncing Registry from smart contract to KvStorage SUCCESS..")
        else:
            logger.info("Syncing Registry from smart contract to KvStorage FAILED..")
    else:
        logger.info("Syncing Registry from smart contract to KvStorage FAILED...")


def test_sync_to_smart_contract(eth_direct_registry, kv_storage):
    org_id = "0x55667788"
    uri = "http://registry-2:8008"
    sc_address = "0x5678AB"
    app_type_ids = ["0xAB12", "0x34FF"]

    json_registry = create_json_object(org_id, uri, sc_address, app_type_ids, 1)
    logger.info("Adding sample registry to KvStorage")
    kv_storage.set("registries", org_id, json_registry)

    registry_helper.sync_contract_and_lmdb(eth_direct_registry, kv_storage)

    # Verify Registry is added to Smart contract and status is set to ACTIVE
    logger.info("Check if Registry is added to Contract and status set to ACTIVE")
    retrieve_result = eth_direct_registry.RegistryRetrieve(org_id.encode())
    if retrieve_result[0] == 1 and retrieve_result[4] == 1:
        logger.info("Syncing Registry from KvStorage to smart contract SUCCESS..")
    else:
        logger.info("Syncing Registry from KvStorage to smart contract FAILED..")


def main():
    logger.info("Testing Direct registry bridge functionality.")

    eth_direct_registry = dir_registry.EthereumDirectRegistry("0x8c99670a15047248403a3E5A38eb8FBE7a12533e",
                                                 '../contracts/WorkerRegistryList.sol')
    kv_storage = KvStorage()
    kv_storage.open("kv_storage")

    logger.info("------------------- test_sync_to_lmdb  ---------------------- \n")
    test_sync_to_lmdb(eth_direct_registry, kv_storage)
    logger.info("\n------------------- test_sync_to_smart_contract  ---------------------- \n")
    test_sync_to_smart_contract(eth_direct_registry, kv_storage)


if __name__ == '__main__':
    main()
