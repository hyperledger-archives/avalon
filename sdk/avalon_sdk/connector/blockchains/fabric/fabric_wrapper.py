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

import logging
from os import environ
from os.path import exists, realpath
import json
import random

from avalon_sdk.connector.blockchains.common.contract_response \
    import ContractResponse
from avalon_sdk.connector.blockchains.fabric import base
from avalon_sdk.connector.blockchains.fabric import tx_committer
from avalon_sdk.connector.blockchains.fabric import event_listener
from avalon_sdk.connector.blockchains.fabric.chaincode_methods \
    import ValidChainCodeMethods
from hfc.protos.common import common_pb2 as common

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


class FabricWrapper():
    """
    Fabric wrapper class to interact with Fabric blockchain.
    It provides wrapper functions to invoke and query chain code.
    """

    # Class variable
    network_config = None

    @classmethod
    def init_network_config(cls, net_config_file):
        # Read network file path from fabric toml file.
        # Initialize the class variable network_config
        if FabricWrapper.network_config is None:
            logging.info("INITIALIZING network_config")
            with open(net_config_file, 'r') as profile:
                FabricWrapper.network_config = json.load(profile)

    def __init__(self, config):
        """
        Constructor to initialize wrapper with required parameter.

        Parameters:
        config    Dictionary containing parameters for Fabric.
                  These parameters are read from a .toml file
        """
        if self.__validate(config):
            FabricWrapper.init_network_config(self.__network_conf_file)
            self.__channel_name = config["fabric"]["channel_name"]
            self.__orgname = base.get_net_info(FabricWrapper.network_config,
                                               'client', 'organization')
            logging.debug("Org name choose: {}".format(self.__orgname))
            self.__peername = random.choice(base.get_net_info(
                FabricWrapper.network_config, 'organizations', self.__orgname,
                'peers'))
            # Get a txn committer
            self.__txn_committer = tx_committer.TxCommitter(
                self.__network_conf_file,
                self.__channel_name, self.__orgname,
                self.__peername, 'Admin')
            cc_methods = ValidChainCodeMethods()
            self.__valid_calls = cc_methods.get_valid_cc_methods()
        else:
            raise Exception("Invalid configuration parameter")

    def __validate(self, config):
        """
        Validate a parameter from the config parameters for existence.

        Parameters:
        config    Configuration parameter

        Returns:
        True if validation succeeds or false if validation fails.
        """
        if config["fabric"]["fabric_network_file"] is None:
            logging.error("Fabric network configuration is not set!!")
            return False
        self.__tcf_home = environ.get("TCF_HOME", "../../../")
        self.__network_conf_file = self.__tcf_home + "/" + \
            config["fabric"]["fabric_network_file"]
        if not exists(self.__network_conf_file):
            raise FileNotFoundError(
                "File not found at path: {0}".format(
                    realpath(self.__network_conf_file)))
        if config["fabric"]["channel_name"] is None:
            logging.error("Channel name is not specified")
            return False
        return True

    def invoke_chaincode(self, chaincode_name, method_name, params):
        """
        This is wrapper method to invoke chain code.

        Parameters:
        chaincode_name Name of the chain code
        method_name    Chain code method name
        params         List of arguments to method

        Returns:
        If the call to chain code query, then it
        returns the payload of the chain code response
        on success or None on error.
        If the call is invoking chain code, then it
        returns ContractResponse.SUCCESS on success
        and ContractResponse.ERROR on failure.
        """
        cc_methods = self.__valid_calls[chaincode_name]
        if cc_methods is None:
            logging.error("Invalid chain code name")
            return False
        the_call = cc_methods[method_name]
        if the_call is None:
            logging.error("Please specify a valid method name. \
                Valid ones for chaincode " +
                          chaincode_name + " are " +
                          ",".join(cc_methods.keys()))
            return False
        resp = self.__txn_committer.cc_invoke(params, chaincode_name,
                                              method_name, '',
                                              queryonly=the_call['isQuery'])
        logging.debug("Response of chain code {} call: {}".format(
            method_name, resp
        ))

        # In case query chain code call
        # it has response in dictionary format
        # convert it to tuple with values.
        if the_call['isQuery'] is True:
            if resp:
                result = []
                for v in resp.values():
                    result.append(v)
                logging.debug(
                    "\nThe tuple created: %s\n ", result)
                return result
            else:
                return None
        elif len(resp) > 0:
            # If it is invoke chain code call then response
            # has status SUCCESS otherwise it is an error
            if hasattr(resp[0], "status") and \
                    resp[0].status == common.Status.SUCCESS:
                return ContractResponse.SUCCESS
            else:
                return ContractResponse.ERROR

        else:
            return ContractResponse.ERROR

    def get_event_handler(self, event_name, chain_code, handler_func):
        """
        Create event handler object.

        Parameters:
        event_name   String to identify the event name
        chain_code   Chain code name as string
        handler_func Callback function name

        Returns:
        Event object
        """
        event_obj = event_listener.EventListener(
            self.__network_conf_file,
            self.__channel_name,
            self.__orgname,
            self.__peername,
            'Admin')
        event_obj.event = event_name
        event_obj.chaincode = chain_code
        event_obj.handler = handler_func
        return event_obj
