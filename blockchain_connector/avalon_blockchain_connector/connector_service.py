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

from avalon_blockchain_connector.ethereum.ethereum_connector \
    import EthereumConnector
from avalon_blockchain_connector.fabric.fabric_connector \
    import FabricConnector

import logging

# -----------------------------------------------------------------
# -----------------------------------------------------------------

FABRIC = 'fabric'
ETHEREUM = 'ethereum'
TCFHOME = os.environ.get("TCF_HOME", "../../")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# -----------------------------------------------------------------
# -----------------------------------------------------------------


def _parse_config_file(config_file):
    # Parse config file and return a config dictionary.
    if config_file:
        conf_files = [config_file]
    else:
        conf_files = [TCFHOME +
                      "/sdk/avalon_sdk/tcf_connector.toml"]
    conf_paths = ["."]
    try:
        config = pconfig.parse_configuration_files(conf_files, conf_paths)
        json.dumps(config)
    except pconfig.ConfigurationException as e:
        logger.error(str(e))
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
        '-b', '--blockchain', help='The target blockchain to use as proxy',
        choices={ETHEREUM, FABRIC},
        type=str, required=True)
    parser.add_argument(
        "-u", "--uri",
        help="Direct API listener endpoint",
        default="http://avalon-listener:1947",
        type=str)

    options = parser.parse_args(args)

    config = _parse_config_file(options.config)
    if config is None:
        logger.error("\n Error in parsing config file: {}\n".format(
            options.config
        ))
        sys.exit(-1)

    # Http JSON RPC listener uri
    uri = options.uri
    if uri:
        config["tcf"]["json_rpc_uri"] = uri

    proxy_blockchain = options.blockchain
    if proxy_blockchain:
        logging.info("Blockchain to be used as proxy : {}"
                     .format(proxy_blockchain))
        if proxy_blockchain == ETHEREUM:
            logging.info("About to start Ethereum connector service")
            eth_connector_svc = EthereumConnector(config)
            eth_connector_svc.start()
        else:
            logging.info("About to start Fabric connector service")
            fabric_connector_svc = FabricConnector(uri)
            fabric_connector_svc.start()
    else:
        logging.error("Could not parse command line arguments")
    sys.exit(-1)

# -----------------------------------------------------------------
# -----------------------------------------------------------------


main()
