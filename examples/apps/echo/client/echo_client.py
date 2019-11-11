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
import base64
import secrets

import config.config as pconfig
import utility.logger as plogger
import utility.utility as utility
from utility.tcf_types import WorkerType
import worker.worker_details as worker
from work_order.work_order_params import WorkOrderParams
from connectors.direct.direct_json_rpc_api_connector \
	import DirectJsonRpcApiConnector
import crypto.crypto as crypto
from error_code.error_status import WorkOrderStatus
import utility.signature as signature
import utility.hex_utils as hex_utils
from error_code.error_status import SignatureStatus

# Remove duplicate loggers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logger = logging.getLogger(__name__)
TCFHOME = os.environ.get("TCF_HOME", "../../")

def ParseCommandLine(args) :

	global worker_obj
	global worker_id
	global message
	global config
	global off_chain
	global requester_signature
	global input_data_hash

	parser = argparse.ArgumentParser()
	use_service = parser.add_mutually_exclusive_group()
	parser.add_argument("-c", "--config", 
		help="the config file containing the Ethereum contract information", 
		type=str)
	use_service.add_argument("-r", "--registry-list", 
		help="the Ethereum address of the registry list", 
		type=str)
	use_service.add_argument("-s", "--service-uri", 
		help="skip URI lookup and send to specified URI", 
		type=str)
	use_service.add_argument("-o", "--off-chain", 
		help="skip URI lookup and use the registry in the config file", 
		action="store_true")
	parser.add_argument("-w", "--worker-id", 
		help="skip worker lookup and retrieve specified worker", 
		type=str)
	parser.add_argument("-m", "--message", 
		help='text message to be included in the JSON request payload', 
		type=str)
	parser.add_argument("-rs", "--requester-signature",
		help="Enable requester signature for work order requests",
		action="store_true")
	parser.add_argument("-dh", "--data-hash",
		help="Enable input data hash for work order requests",
		action="store_true")

	options = parser.parse_args(args)

	if options.config:
		conf_files = [options.config]
	else:
		conf_files = [ TCFHOME + \
			"/examples/common/python/connectors/tcf_connector.toml" ]
	confpaths = [ "." ]
	try :
		config = pconfig.parse_configuration_files(conf_files, confpaths)
		json.dumps(config)
	except pconfig.ConfigurationException as e :
		logger.error(str(e))
		sys.exit(-1)

	global direct_jrpc
	direct_jrpc = DirectJsonRpcApiConnector(conf_files[0])

	# Whether or not to connect to the registry list on the blockchain
	off_chain = False

	if options.registry_list:
		config["ethereum"]["direct_registry_contract_address"] = \
			options.registry_list

	if options.service_uri:
		config["tcf"]["json_rpc_uri"] = options.service_uri
		off_chain = True

	if options.off_chain:
		off_chain = True

	requester_signature = options.requester_signature
	input_data_hash = options.data_hash
	worker_id = options.worker_id
	message = options.message
	if options.message is None or options.message == "":
		message = "Test Message"

	# Initializing Worker Object
	worker_obj = worker.SGXWorkerDetails()

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

	# Connect to registry list and retrieve registry
	if not off_chain:
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
	worker_registry_instance = direct_jrpc.create_worker_registry(
		config
	)
	if not worker_id:
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
	worker_obj.load_worker(worker_retrieve_result)

	logger.info("**********Worker details Updated with Worker ID" + \
		"*********\n%s\n", worker_id)

	# Convert workloadId to hex
	workload_id = "echo-result".encode("UTF-8").hex()
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
	if input_data_hash:
		# Compute data hash for data params inData
		data_hash = utility.compute_data_hash(message)
		# Convert data_hash to hex
		data_hash = hex_utils.byte_array_to_hex_str(data_hash)
		wo_params.add_in_data(message, data_hash)
	else:
		wo_params.add_in_data(message)

	# Encrypt work order request hash
	wo_params.add_encrypted_request_hash()

	if requester_signature:
		private_key = utility.generate_signing_keys()
		# Add requester signature and requester verifying_key
		if wo_params.add_requester_signature(private_key) == False:
			logger.info("Work order request signing failed")
			exit(1)

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
		sig_obj = signature.ClientSignature()
		status = sig_obj.verify_signature(res, worker_obj.verification_key)
		try:
			if status == SignatureStatus.PASSED:
				logger.info("Signature verification Successful")
				decrypted_res = utility.decrypted_response(
					res, session_key, session_iv)
				logger.info("\nDecrypted response:\n {}".format(decrypted_res))
				if input_data_hash:
					decrypted_data = decrypted_res[0]["data"]
					data_hash_in_resp = (decrypted_res[0]["dataHash"]).upper()
					# Verify data hash in response
					if utility.verify_data_hash(decrypted_data, data_hash_in_resp) == False:
						sys.exit(1)
			else:
				logger.info("Signature verification Failed")
				sys.exit(1)
		except:
			logger.error("ERROR: Failed to decrypt response")
			sys.exit(1)
	else:
		logger.info("\n Work order get result failed {}\n".format(
			res
		))
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
