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
import logging
import nest_asyncio

import config.config as pconfig
from fabric_connector.fabric_connector \
    import FabricConnector
from avalon_sdk.connector.blockchains.fabric.fabric_worker_registry \
    import FabricWorkerRegistryImpl
from avalon_sdk.connector.blockchains.fabric.fabric_work_order \
    import FabricWorkOrderImpl

# -----------------------------------------------------------------
# -----------------------------------------------------------------

TCF_HOME = os.environ.get("TCF_HOME", "../../")

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
        help="The config file containing the Fabric network information",
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

    fabric_worker = FabricWorkerRegistryImpl(config)
    fabric_work_order = FabricWorkOrderImpl(config)

    nest_asyncio.apply()
    fabric_connector_svc = FabricConnector(
        config, None,
        fabric_worker, fabric_work_order, None)
    fabric_connector_svc.start()

# -----------------------------------------------------------------
# -----------------------------------------------------------------


main()
