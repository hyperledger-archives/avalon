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

import os
import sys
import json
import argparse
import logging
import secrets

import config.config as pconfig
import utility.logger as plogger
import utility.utility as utility
from utility.tcf_types import WorkerType
import worker.worker_details as worker_details
from work_order.work_order_params import WorkOrderParams
from connectors.direct.direct_json_rpc_api_connector \
	import DirectJsonRpcApiConnector
from error_code.error_status import WorkOrderStatus

# Remove duplicate loggers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logger = logging.getLogger(__name__)
TCFHOME = os.environ.get("TCF_HOME", "../../")

def ParseCommandLine(args) :

	global worker_obj
	global worker_id
	global workload_id
	global in_data
	global config
	global mode
	global uri
	global address

	parser = argparse.ArgumentParser()
	mutually_excl_group = parser.add_mutually_exclusive_group()
	parser.add_argument("-c", "--config",
		help="The config file containing the Ethereum contract information",
		type=str)
	mutually_excl_group.add_argument("-u", "--uri",
		help="Direct API listener endpoint",
		type=str)
	mutually_excl_group.add_argument("-a", "--address",
		help="an address (hex string) of the smart contract (e.g. Worker registry listing)",
		type=str)
	parser.add_argument("-m", "--mode",
		help="should be one of listing or registry",
		type=str)
	parser.add_argument("-w", "--worker_id",
		help="worker id (hex string) to use to submit a work order",
		type=str)
	parser.add_argument("-l", "--workload_id",
		help='workload id (hex string) for a given worker',
		type=str)
	parser.add_argument("-i", "--in_data",
		help='Input data',
		type=str)

	options = parser.parse_args(args)

	if options.config:
		conf_files = [options.config]
	else:
		conf_files = [TCFHOME + \
			"/examples/common/python/connectors/tcf_connector.toml"]
	confpaths = [ "." ]
	try :
		config = pconfig.parse_configuration_files(conf_files, confpaths)
		config_json_str = json.dumps(config)
	except pconfig.ConfigurationException as e :
		logger.error(str(e))
		sys.exit(-1)

	mode = options.mode

	uri = options.uri
	if uri:
		config["tcf"]["json_rpc_uri"] = uri

	address = options.address
	if address:
		if mode == "listing":
			config["ethereum"]["direct_registry_contract_address"] = \
				address
		elif mode == "registry":
			logger.error("\n Only Worker registry listing address is supported." +
                                "Worker registry address is unsupported \n");
			sys.exit(-1)
		else:
			logger.error("Mode should be either registry or listing")

	else:
		if not mode:
			logger.error("Address needs to be passed with mode option")

	worker_id = options.worker_id

	workload_id = options.workload_id
	if not workload_id:
		logger.info("\nWorkload id is mandatory\n");
		sys.exit(-1)

	in_data = options.in_data



def Main(args=None):
	ParseCommandLine(args)

	config["Logging"] = {
		"LogFile" : "__screen__",
		"LogLevel" : "INFO"
	}

	plogger.setup_loggers(config.get("Logging", {}))
	sys.stdout = plogger.stream_to_logger(
		logging.getLogger("STDOUT"), logging.DEBUG)
	sys.stderr = plogger.stream_to_logger(
		logging.getLogger("STDERR"), logging.WARN)

	logger.info("***************** TRUSTED COMPUTE FRAMEWORK (TCF)" +
		" *****************")

	global direct_jrpc
	direct_jrpc = DirectJsonRpcApiConnector(config_file=None,config=config)

	global address
	if mode == "registry" and address:
		logger.info("\n Worker registry contract address is unsupported \n");
		sys.exit(-1)

	# Connect to registry list and retrieve registry
	global uri
	if not uri and mode == "listing":
		registry_list_instance = direct_jrpc.create_worker_registry_list(
			config
		)
		# Lookup returns tuple, first element is number of registries and
		# second is element is lookup tag and third is list of organization ids.
		registry_count, lookup_tag, registry_list = registry_list_instance.registry_lookup()
		logger.info("\n Registry lookup response: registry count: {} lookup tag: {} registry list: {}\n".format(
			registry_count, lookup_tag, registry_list
		))
		if (registry_count == 0):
			logger.warn("No registries found")
			sys.exit(1)
		# Retrieve the fist registry details.
		registry_retrieve_result = registry_list_instance.registry_retrieve(registry_list[0])
		logger.info("\n Registry retrieve response: {}\n".format(
			registry_retrieve_result
		))
		config["tcf"]["json_rpc_uri"] = registry_retrieve_result[0]

	# Prepare worker
	req_id = 31
	global worker_id
	if not worker_id:
		worker_registry_instance = direct_jrpc.create_worker_registry(
			config
		)
		worker_lookup_result = worker_registry_instance.worker_lookup(
			worker_type=WorkerType.TEE_SGX, id=req_id
		)
		logger.info("\n Worker lookup response: {}\n".format(
			json.dumps(worker_lookup_result, indent=4)
		))
		if "result" in worker_lookup_result and \
			"ids" in worker_lookup_result["result"].keys():
			if worker_lookup_result["result"]["totalCount"] != 0:
				worker_id = worker_lookup_result["result"]["ids"][0]
			else:
				logger.error("ERROR: No workers found")
				sys.exit(1)
		else:
			logger.error("ERROR: Failed to lookup worker")
			sys.exit(1)

	req_id += 1
	worker_retrieve_result = worker_registry_instance.worker_retrieve(
		worker_id,req_id
	)
	logger.info("\n Worker retrieve response: {}\n".format(
		json.dumps(worker_retrieve_result, indent=4)
	))

	if "error" in worker_retrieve_result:
		logger.error("Unable to retrieve worker details\n")
		sys.exit(1)

    # Initializing Worker Object
	worker_obj = worker_details.SGXWorkerDetails()
	worker_obj.load_worker(worker_retrieve_result)

	logger.info("**********Worker details Updated with Worker ID" + \
		"*********\n%s\n", worker_id)

	# Convert workloadId to hex
	global workload_id
	workload_id = workload_id.encode("UTF-8").hex()
	work_order_id = secrets.token_hex(32)
	requester_id = secrets.token_hex(32)
	session_iv = utility.generate_iv()
	session_key = utility.generate_key()
	requester_nonce = secrets.token_hex(16)
	# Create work order
	wo_params = WorkOrderParams(
		work_order_id, worker_id, workload_id, requester_id,
		session_key, session_iv, requester_nonce,
		result_uri=" ", notify_uri=" ",
		worker_encryption_key=worker_obj.encryption_key,
		data_encryption_algorithm="AES-GCM-256"
	)
	# Add worker input data
	global in_data
	wo_params.add_in_data(in_data)

	# Sign work order
	private_key = utility.generate_signing_keys()
	wo_params.add_encrypted_request_hash()
	wo_params.add_requester_signature(private_key)
	# Submit work order
	logger.info("Work order submit request : %s, \n \n ",
        wo_params.to_string())
	work_order_instance = direct_jrpc.create_work_order(
		config
	)
	req_id += 1
	response = work_order_instance.work_order_submit(
		wo_params.get_params(),
		wo_params.get_in_data(),
		wo_params.get_out_data(),
		id=req_id
	)
	logger.info("Work order submit response : {}\n ".format(
		json.dumps(response, indent=4)
	))

	if "error" in response and response["error"]["code"] != WorkOrderStatus.PENDING:
		sys.exit(1)
	# Retrieve result
	req_id += 1
	res = work_order_instance.work_order_get_result(
		work_order_id,
		req_id
	)

	logger.info("Work order get result : {}\n ".format(
		json.dumps(res, indent=4)
	))
	if "result" in res:
		decrypted_res = utility.decrypted_response(
			json.dumps(res), session_key, session_iv)
		logger.info("\nDecrypted response:\n {}".format(decrypted_res))
	else:
		sys.exit(1)

	# Retrieve receipt
	wo_receipt_instance = direct_jrpc.create_work_order_receipt(
		config
	)
	req_id += 1
	receipt_res = wo_receipt_instance.work_order_receipt_retrieve(
		work_order_id,
		id=req_id
	)
	logger.info("\Retrieve receipt response:\n {}".format(
		json.dumps(receipt_res, indent= 4)
	))
#------------------------------------------------------------------------------
Main()
