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
import time
import argparse
import random
import json
from builtins import bytes
import hashlib

from service_client.generic import GenericServiceClient
import crypto.crypto as crypto
from shared_kv.shared_kv_interface import KvStorage
import utility.tcf_helper as enclave_helper
import logging
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def LocalMain(config) :

    if config.get('KvStorage') is None:
        logger.error("Kv Storage path is missing")
        sys.exit(-1)

    KvHelper = KvStorage()
    KvHelper.open((TCFHOME + '/' + config['KvStorage']['StoragePath']))
    
    if not input_json_str and not input_json_dir:
       logger.error("JSON input file is not provided")
       exit(1)
    
    if not output_json_file_name:
        logger.error("JSON output file is not provided")
        exit(1)
    
    if not server_uri:
        logger.error("Server URI is not provided")
        exit(1)
        
    logger.info('execute work order')
    uri_client = GenericServiceClient(server_uri) 
    
    if input_json_dir:
        directory = os.fsencode(input_json_dir)
        files = os.listdir(directory)
            
        for file in sorted(files) :
            logger.info("------------------Input file name: %s ---------------\n",file.decode("utf-8"))
            input_json_str1 = enclave_helper.read_json_file((directory.decode("utf-8") + file.decode("utf-8")))
            logger.info("*********Request Json********* \n%s\n", input_json_str1)
            response = uri_client._postmsg(input_json_str1)
            logger.info("**********Received Response*********\n%s\n", response)
            
    else :
        j=json.loads(input_json_str)
        
        if(j['method'] == "WorkOrderGetResult"):
            response = {}
            response['id'] =  j['params']['workOrderId']
            response["outData"] = "Processed response"
            KvHelper.set("wo-responses", str(j['params']['workOrderId']), json.dumps(response))
            input_str = json.dumps(j)
            logger.info('input str %s', input_str)
            response = uri_client._postmsg(input_str)
            logger.info("Received Response : %s , \n \n ", response)
            
            j['params']['workOrderId'] = "101"
            input_str = json.dumps(j)
            logger.info('input str %s', input_str)
            response = uri_client._postmsg(input_str)
            logger.info("Received Response : %s , \n \n ", response)
            
            j['params']['workOrderId'] = "121"
            input_str = json.dumps(j)
            logger.info('input str %s', input_str)
            response = uri_client._postmsg(input_str)
            logger.info("Received Response : %s , \n \n ", response)
            
        else:
            id = 100
            logger.info("time stamp lookup  : %s", KvHelper.lookup("wo-timestamps"))
            logger.info("Test adding new time stamps entries")
            for x in range(5):
                j['params']['workOrderId'] = id + x
                input_str = json.dumps(j)
                logger.info('input str %s', input_str)
                response = uri_client._postmsg(input_str)
                logger.info("Received Response : %s , \n \n ", response)
            
                logger.info("time stamp lookup  : %s", KvHelper.lookup("wo-timestamps"))
                
            logger.info("Work order id exists")
            id = 100    
            for x in range(5):
                j['params']['workOrderId'] = id + x
                input_str = json.dumps(j)
                logger.info('input str %s', input_str)
                response = uri_client._postmsg(input_str)
                logger.info("Received Response : %s , \n \n ", response);
            
            logger.info("time stamp lookup  : %s", KvHelper.lookup("wo-timestamps"))
                
            logger.info("Test max count reached and buys status")
            id = 105
            for x in range(10):
                j['params']['workOrderId'] = id + x
                input_str = json.dumps(j)
                logger.info('input str %s', input_str)
                response = uri_client._postmsg(input_str)
                logger.info("Received Response : %s , \n \n ", response);
                
            logger.info("time stamp lookup  : %s", KvHelper.lookup("wo-timestamps"))
            
            logger.info("Adding a work order id 109 into processed table")
            KvHelper.set("wo-processed", "109", "109")
            
            logger.info("Sending a new request with work order id %s", id + x)
            j['params']['workOrderId'] = id + x
            input_str = json.dumps(j)
            logger.info('input str %s', input_str)
            response = uri_client._postmsg(input_str)
            logger.info("Received Response : %s , \n \n ", response);
            
            logger.info("time stamp lookup  : %s", KvHelper.lookup("wo-timestamps"))
            
            work_orders = KvHelper.lookup("wo-scheduled")
            for wo_id in work_orders:
                KvHelper.remove("wo-scheduled", wo_id)
            
            logger.info("adding 3 entries into processing scheduled and processed table to test boot flow")
            KvHelper.set("wo-scheduled", "100", input_str)
            KvHelper.set("wo-processing", "101", input_str)
            KvHelper.set("wo-processed", "102", input_str)
            
            logger.info("restart tcf listener and verify it adds to its internal list during boot up")

    exit(0)

TCFHOME = os.environ.get("TCF_HOME", "../../")

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def ParseCommandLine(config, args) :
    logger.info('entering parse')
    global input_json_str
    global input_json_dir
    global server_uri
    global output_json_file_name
    global verify_key
    global consensus_file_name

    parser = argparse.ArgumentParser()
    parser.add_argument('--logfile', help='Name of the log file, __screen__ for standard output', type=str)
    parser.add_argument('-v', '--verify_key',help="Verification key PEM file name", type=str, default=None)
    parser.add_argument('--loglevel', help='Logging level', type=str)
    parser.add_argument('-i', '--input_file', help='JSON input file name', type=str, default='input.json')
    parser.add_argument('--input_dir', help='Logging level', type=str, default=[])
    parser.add_argument(
        '-c', '--connect_uri', help='URI to send requests to', type=str, default=[])
    parser.add_argument(
        'output_file',
        help='JSON output file name',
        type=str,
        default='output.json',
        nargs='?')

    options = parser.parse_args(args)

    if config.get('Logging') is None :
        config['Logging'] = {
            'LogFile' : '__screen__',
            'LogLevel' : 'INFO'
        }
    if options.logfile :
        config['Logging']['LogFile'] = options.logfile
    if options.loglevel :
        config['Logging']['LogLevel'] = options.loglevel.upper()
    
    input_json_str = None
    input_json_dir = None
    verify_key = None
	
    if options.verify_key:
        verify_key = options.verify_key
    
    if options.connect_uri:
        server_uri = options.connect_uri
    else:
        logger.error("ERROR: Please enter the server URI")
    
    if options.input_dir:
        logger.info('Load Json Directory from %s',options.input_dir)
        input_json_dir = options.input_dir
    elif options.input_file:
        try:
            logger.info('load JSON input from %s', options.input_file)

            with open(options.input_file, "r") as file:
                input_json_str = file.read()
        except:
            logger.error("ERROR: Failed to read from file %s", options.input_file)
    else :
        logger.info('No input found')

    if options.output_file:
        output_json_file_name = options.output_file
    else:
        output_json_file_name = None

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def Main(args=None) :
    import config.config as pconfig
    import utility.logger as plogger

    # parse out the configuration file first
    conffiles = [ 'tcs_config.toml' ]
    confpaths = [ ".", TCFHOME + "/" + "config", "../../etc"]
  
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='configuration file', nargs = '+')
    parser.add_argument('--config-dir', help='configuration folder', nargs = '+')
    (options, remainder) = parser.parse_known_args(args)

    if options.config :
        conffiles = options.config
    
    if options.config_dir :
        confpaths = options.config_dir

    try :
        config = pconfig.parse_configuration_files(conffiles, confpaths)
        config_json_str = json.dumps(config, indent=4)
    except pconfig.ConfigurationException as e :
        logger.error(str(e))
        sys.exit(-1)

    plogger.setup_loggers(config.get('Logging', {}))
    sys.stdout = plogger.stream_to_logger(logging.getLogger('STDOUT'), logging.DEBUG)
    sys.stderr = plogger.stream_to_logger(logging.getLogger('STDERR'), logging.WARN)

    ParseCommandLine(config, remainder)
    LocalMain(config)

Main()
