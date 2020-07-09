# Copyright 2020 Intel Corporation
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
import json
import argparse
import config.config as pconfig

from avalon_sdk.connector.blockchains.ethereum.ethereum_work_order \
    import EthereumWorkOrderProxyImpl
from avalon_sdk.connector.blockchains.ethereum.ethereum_worker_registry \
    import EthereumWorkerRegistryImpl
from avalon_sdk.connector.blockchains.ethereum.ethereum_wrapper \
    import EthereumWrapper

from ethereum_connector.ethereum_connector \
    import EthereumConnector

import logging

# -----------------------------------------------------------------
# -----------------------------------------------------------------

TCF_HOME = os.environ.get("TCF_HOME", "../../../")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# -----------------------------------------------------------------
# -----------------------------------------------------------------


def _parse_config_file(config_file):
    # Parse config file and return a config dictionary.
    if config_file:
        conf_files = [config_file]
    else:
        conf_files = [TCF_HOME +
                      "/sdk/avalon_sdk/tcf_connector.toml"]
    conf_paths = ["."]
    try:
        config = pconfig.parse_configuration_files(conf_files, conf_paths)
        json.dumps(config)
    except pconfig.ConfigurationException as e:
        logging.error(str(e))
        config = None

    return config

# -----------------------------------------------------------------
# -----------------------------------------------------------------


def main(args=None):

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config",
        help="The config file containing the Ethereum contract information",
        type=str)
    parser.add_argument(
        "-u", "--uri",
        help="Direct API listener endpoint",
        default="http://avalon-listener:1947",
        type=str)

    options = parser.parse_args(args)

    config = _parse_config_file(options.config)
    if config is None:
        logging.error("\n Error in parsing config file: {}\n".format(
            options.config
        ))
        sys.exit(-1)

    # Http JSON RPC listener uri
    uri = options.uri
    if uri:
        config["tcf"]["json_rpc_uri"] = uri

    logging.info("About to start Ethereum connector service")
    eth_client = EthereumWrapper(config)

    worker_reg_contract_file = TCF_HOME + "/" + \
        config["ethereum"]["worker_registry_contract_file"]
    worker_reg_contract_address = \
        config["ethereum"]["worker_registry_contract_address"]
    worker_reg_contract_instance,\
        worker_reg_contract_instance_evt = eth_client\
        .get_contract_instance(
            worker_reg_contract_file, worker_reg_contract_address)

    worker_registry = EthereumWorkerRegistryImpl(config)

    work_order_contract_file = TCF_HOME + "/" + \
        config["ethereum"]["work_order_contract_file"]
    work_order_contract_address = \
        config["ethereum"]["work_order_contract_address"]
    work_order_contract_instance,\
        wo_contract_instance_evt = eth_client\
        .get_contract_instance(
            work_order_contract_file, work_order_contract_address)

    work_order_proxy = EthereumWorkOrderProxyImpl(config)
    eth_connector_svc = EthereumConnector(
        config, None,
        worker_registry, work_order_proxy, None,
        wo_contract_instance_evt)
    eth_connector_svc.start()

# -----------------------------------------------------------------
# -----------------------------------------------------------------


main()
