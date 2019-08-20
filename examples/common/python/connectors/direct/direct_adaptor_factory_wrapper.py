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

import json
import logging
import time
import sys
import utility.utility as enclave_helper
import utility.signature as signature
from service_client.generic import GenericServiceClient
from connectors.direct.direct_json_rpc_api_adaptor_factory \
	import DirectJsonRpcApiAdaptorFactory
from utility.hex_utils import hex_to_utf, pretty_ids
import json_rpc_request.json_rpc_request

logger = logging.getLogger(__name__)
# -----------------------------------------------------------------
class DirectAdaptorFactoryWrapper:
	# Contains the functions needed to submit and retrieve work orders in the Direct Model
	def __init__(self, config_file):
		self.adaptor_factory = DirectJsonRpcApiAdaptorFactory(config_file)
		self.worker_registry_list = None
		self.worker_registry = None
		self.work_order = None
		self.work_order_receipt = None

	def init_worker_registry_list(self, config):
		self.worker_registry_list = \
			self.adaptor_factory.create_worker_registry_list_adaptor(config)

	# Lookup worker registries in registry list
	def registry_lookup(self, app_type_id=None):
		if self.worker_registry_list == None:
			logger.error("ERROR: Worker registry list adaptor not initialized")
			sys.exit(1)
		if app_type_id:
			lookup_result = self.worker_registry_list.registry_lookup(
				app_type_id=app_type_id)
		else:
			lookup_result = self.worker_registry_list.registry_lookup()
		logger.info("Registry Lookup result: [%d, %s, %s]", 
			lookup_result[0], lookup_result[1], 
			pretty_ids(lookup_result[2]))
		return lookup_result

	# Retrieve worker registry URI
	def registry_retrieve(self, org_id):
		if self.worker_registry_list == None:
			logger.error("ERROR: Worker registry list adaptor not initialized")
			sys.exit(1)
		retrieve_result = self.worker_registry_list.registry_retrieve(org_id)
		logger.info("Registry retrieved: [%s, %s, %s, %d]", 
			retrieve_result[0], 
			hex_to_utf(retrieve_result[1]), 
			pretty_ids(retrieve_result[2]), 
			retrieve_result[3])
		return retrieve_result

	def init_worker_registry(self, config):
		self.worker_registry = \
			self.adaptor_factory.create_worker_registry_adaptor(config)

	# Lookup worker in worker registry
	def worker_lookup(self, worker_lookup_json):
		if self.worker_registry == None:
			logger.error("ERROR: Worker registry adaptor not initialized")
			sys.exit(1)

		logger.info("*********Request Json********* \n%s\n", 
			worker_lookup_json.get_json_str_indent())
		response = self.worker_registry.worker_lookup(
			worker_type=worker_lookup_json.get_worker_type(), 
			organization_id=worker_lookup_json.get_organization_id(), 
			application_type_id=worker_lookup_json.get_application_type_id(), 
			id=worker_lookup_json.get_id())
		logger.info("**********Received Response*********\n%s\n", 
			json.dumps(response, indent=4))

		return response

	# Retrieve worker from worker registry
	def worker_retrieve(self, worker_retrieve_json):
		if self.worker_registry == None:
			logger.error("ERROR: Worker registry adaptor not initialized")
			sys.exit(1)

		logger.info("*********Request Json********* \n%s\n", 
			worker_retrieve_json.get_json_str_indent())
		response = self.worker_registry.worker_retrieve(
			worker_retrieve_json.get_worker_id(), 
			id=worker_retrieve_json.get_id())
		logger.info("**********Received Response*********\n%s\n", 
			json.dumps(response, indent=4))

		if "result" in response:
			return response
		else:
			logger.error("ERROR: Failed to retrieve worker")
			sys.exit(1)

	def init_work_order(self, config):
		self.work_order = \
			self.adaptor_factory.create_work_order_adaptor(config)

	# Encrypt work order and submit
	def work_order_submit(self, wo_submit_json, encrypted_session_key, 
		worker_obj, private_key, session_iv):
		if self.work_order == None:
			logger.error("ERROR: Work order adaptor not initialized")
			sys.exit(1)

		input_json_str = wo_submit_json.get_json_str()
		sig_obj = signature.ClientSignature()
		input_json_str = sig_obj.generate_client_signature(
			input_json_str, worker_obj,
			private_key, session_iv, encrypted_session_key)
		wo_submit_json.load_from_str(input_json_str)

		logger.info("*********Request Json********* \n%s\n", 
			json.dumps(json.loads(input_json_str), indent=4))
		response = self.work_order.work_order_submit(
			wo_submit_json.get_params(), wo_submit_json.get_in_data(), 
			wo_submit_json.get_out_data(), id=wo_submit_json.get_id())
		logger.info("**********Received Response*********\n%s\n", 
			json.dumps(response, indent=4))

		# Return signed workorder json
		return input_json_str

	# Retrieve work order result and decrypt response
	def work_order_get_result(self, wo_get_result_json, encrypted_session_key):
		if self.work_order == None:
			logger.error("ERROR: Work order adaptor not initialized")
			sys.exit(1)

		logger.info("*********Request Json********* \n%s\n", 
			wo_get_result_json.get_json_str_indent())
		response = self.work_order.work_order_get_result(
			wo_get_result_json.get_work_order_id(), 
			wo_get_result_json.get_id())
		logger.info("**********Received Response*********\n%s\n", 
			json.dumps(response))

		# Poll for the "WorkOrderGetResult" and break when you get the result
		while("result" not in response):
			if response["error"]["code"] == 9:
				break
			response = self.work_order.work_order_get_result(
				wo_get_result_json.get_work_order_id(), 
				wo_get_result_json.get_id())
			if "result" not in response:
				logger.info(" Received Response : %s, \n \n ", response)
				time.sleep(3)
			else:
				logger.info(" Received Response : %s, \n \n ", 
					json.dumps(response, indent=4))

		return enclave_helper.decrypted_response(
			json.dumps(response), encrypted_session_key)

	def init_work_order_receipt(self, config):
		self.work_order_receipt = \
			self.adaptor_factory.create_work_order_receipt_adaptor(config)

	# Retrieve work order receipt
	def work_order_receipt_retrieve(self, wo_receipt_retrieve_json):
		if self.work_order_receipt == None:
			logger.error("ERROR: Work order adaptor not initialized")
			sys.exit(1)
	
		logger.info("*********Request Json********* \n%s\n", 
			wo_receipt_retrieve_json.get_json_str_indent())
		response = self.work_order_receipt.work_order_receipt_retrieve(
			wo_receipt_retrieve_json.get_work_order_id(), 
			wo_receipt_retrieve_json.get_id())
		logger.info("**********Received Response*********\n%s\n", 
			json.dumps(response, indent=4))
		return response
