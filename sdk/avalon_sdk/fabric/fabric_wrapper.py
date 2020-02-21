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

from avalon_sdk.fabric import base
from avalon_sdk.fabric import tx_committer
from avalon_sdk.fabric import event_listener
from hfc.protos.common import common_pb2 as common

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


class FabricWrapper():
    """
    Fabric wrapper class to interact with fabric blockchain
    It provides wrapper functions to invoke and query chain code.
    """

    def __init__(self, config):
        """
        Constructor to initialize wrapper with required parameter
        Params:
            config is dict containing parameters for fabric.
            These parameters are read from toml file.
        """
        if self.__validate(config):
            # Read network file path from fabric toml file.
            with open(self.__network_conf_file, 'r') as profile:
                self.__network_config = json.load(profile)
            self.__channel_name = config["fabric"]["channel_name"]
            self.__orgname = base.get_net_info(self.__network_config,
                                               'client', 'organization')
            logging.info("Org name choose: {}".format(self.__orgname))
            self.__peername = random.choice(base.get_net_info(
                self.__network_config, 'organizations', self.__orgname,
                'peers'))
            # Get a txn committer
            self.__txn_committer = tx_committer.TxCommitter(
                self.__network_conf_file,
                self.__channel_name, self.__orgname,
                self.__peername, 'Admin')
            with open(self.__tcf_home + '/sdk/avalon_sdk/fabric/' +
                      'methods.json', 'r') as all_methods:
                self.__valid_calls = json.load(all_methods)
        else:
            raise Exception("Invalid configuration parameter")

    def __validate(self, config):
        """
        validates parameter from config parameters for existence.
        Returns false if validation fails and true if it success
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
                    realpath(__network_conf_file)))
        if config["fabric"]["channel_name"] is None:
            logging.error("Channel name is not specified")
            return False
        return True

    def invoke_chaincode(self, chaincode_name, method_name, params):
        """
        This is wrapper method to invoke the chain code.
        Params:
            chaincode_name is name of the chain code
            method_name is chain code method name
            params is list of arguments to method
        Returns:
            If the call to chain code query then it
            returns the payload of chain code response
            on success or None on error.
            If the call is invoking chain code then it
            returns True on success and False on failure.
        """
        cc_methods = self.__valid_calls[chaincode_name]
        if cc_methods is None:
            logging.info("Invalid chain code name")
            return False
        the_call = cc_methods[method_name]
        if the_call is None:
            logging.info("Please specify a valid method name. \
                Valid ones for chaincode " +
                         chaincode_name + " are " +
                         ",".join(cc_methods.keys()))
            return False
        resp = self.__txn_committer.cc_invoke(params, chaincode_name,
                                              method_name, '',
                                              queryonly=the_call['isQuery'])
        logging.info("Response of chain code {} call: {}".format(
            method_name, resp[0]
        ))
        if len(resp) > 0:
            # In case query chain code call
            # it has response has status 200 and payload on success
            # status 500 on error
            if the_call['isQuery'] is True:
                if hasattr(resp[0], 'response') and \
                        hasattr(resp[0].response, 'status'):
                    if resp[0].response.status == 200 and \
                            hasattr(resp[0].response, 'payload'):
                        payload = json.loads(resp[0].response.payload)
                        logging.info(
                            "\nThe execution payload: %s\n ", payload)
                        result = []
                        for v in payload.values():
                            result.append(v)
                        logging.info(
                            "\nThe tuple created: %s\n ", result)
                        return result
                    else:
                        logging.info("\nThe execution result: %s\n",
                                     resp[0].response.message)
                        return None
            # If it is invoke chain code call then response
            # has status SUCCESS otherwise it is an error
            elif hasattr(resp[0], "status") and \
                    resp[0].status == common.Status.SUCCESS:
                return True
            else:
                return False

        return False

    def get_event_handler(self, event_name, chain_code, handler_func):
        """
        function to create event handler object
        params:
            event_name is string to identify the event name
            chain_code is chain code name as string
            handler_func is call back function name
        returns:
            event object
        """
        event_obj = event_listener.EventListener(
            self.__network_conf_file,
            self.__channel_name,
            self.__orgname,
            self.__peername,
            'Admin')
        event_obj.config = 'blockmark'
        event_obj.event = event_name
        event_obj.chaincode = chain_code
        event_obj.handler = handler_func
        return event_obj
