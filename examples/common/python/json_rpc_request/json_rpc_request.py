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
import random
import sys
from utility.tcf_types import WorkerType

class JsonRpcRequest:
	def __init__(self, id, method):
		self.json_obj = json.loads(
			'{"jsonrpc":"2.0","method":"","id":"","params":{ } }')
		self.set_id(id)
		self.set_method(method)

	def set_method(self, method):
		self.json_obj["method"] = method

	def get_id(self):
		return self.json_obj["id"]

	def set_id(self, id):
		self.json_obj["id"] = id

	def get_json_str(self):
		return json.dumps(self.json_obj)

	def get_json_str_indent(self):
		return json.dumps(self.json_obj, indent=4)

	def load_from_str(self, json_str):
		self.json_obj = json.loads(json_str)

class WorkerLookupJson(JsonRpcRequest):
	def __init__(self, id, worker_type=None, organization_id=None, 
		application_type_id=None):
		super().__init__(id, "WorkerLookUp")
		if worker_type:
			self.set_worker_type(worker_type)
		if organization_id:
			self.set_organization_id(organization_id)
		if application_type_id:
			self.set_application_type_id(application_type_id)

	def set_worker_type(self, worker_type):
		self.json_obj["params"]["workerType"] = worker_type

	def get_worker_type(self):
		if "workerType" in self.json_obj["params"]:
			return WorkerType(self.json_obj["params"]["workerType"])
		else:
			return None

	def set_organization_id(self, organization_id):
		self.json_obj["params"]["organizationId"] = organization_id

	def get_organization_id(self):
		if "organizationId" in self.json_obj["params"]:
			return self.json_obj["params"]["organizationId"]
		else:
			return None

	def set_application_type_id(self, application_type_id):
		self.json_obj["params"]["applicationTypeId"] = application_type_id
	
	def get_application_type_id(self):
		if "applicationTypeId" in self.json_obj["params"]:
			return self.json_obj["params"]["applicationTypeId"]
		else:
			return None

class WorkerRetrieveJson(JsonRpcRequest):
	def __init__(self, id, worker_id):
		super().__init__(id, "WorkerRetrieve")
		self.set_worker_id(worker_id)

	def get_worker_id(self):
		return self.json_obj["params"]["workerId"]

	def set_worker_id(self, worker_id):
		self.json_obj["params"]["workerId"] = worker_id

class WorkOrderJson(JsonRpcRequest):
	def __init__(self, id, method, work_order_id):
		super().__init__(id, method)
		self.set_work_order_id(work_order_id)

	def set_work_order_id(self, work_order_id):
		self.json_obj["params"]["workOrderId"] = work_order_id

	def get_work_order_id(self):
		return self.json_obj["params"]["workOrderId"]

class WorkOrderSubmitJson(WorkOrderJson):
	def __init__(self, id, response_timeout_msecs, payload_format,
		work_order_id, worker_id, workload_id,
		requester_id, encrypted_session_key, session_key_iv,
		requester_nonce, result_uri=None, notify_uri=None, worker_encryption_key=None,
		data_encryption_algorithm=None):
		super().__init__(id, "WorkOrderSubmit", 
			work_order_id)
		self.set_response_timeout_msecs(response_timeout_msecs)
		self.set_payload_format(payload_format)
		if result_uri:
			self.set_result_uri(result_uri)
		else:
			self.set_result_uri("")
		if notify_uri:
			self.set_notify_uri(notify_uri)
		else:
			self.set_notify_uri("")
		self.set_worker_id(worker_id)
		self.set_workload_id(workload_id)
		self.set_requester_id(requester_id)
		if worker_encryption_key:
			self.set_worker_encryption_key(worker_encryption_key)
		else:
			self.set_worker_encryption_key("")
		if data_encryption_algorithm:
			self.set_data_encryption_algorithm(data_encryption_algorithm)
		else:
			self.set_data_encryption_algorithm("")

		self.set_encrypted_session_key(encrypted_session_key)
		self.set_session_key_iv(session_key_iv)
		self.set_requester_nonce(requester_nonce)
		self.update_encrypted_request_hash()
		self.update_requester_signature()
		self.json_obj["params"]["inData"] = []
		self.json_obj["params"]["outData"] = []


	def set_response_timeout_msecs(self, response_timeout_msecs):
		self.json_obj["params"]["responseTimeoutMSecs"] = \
			response_timeout_msecs

	def set_payload_format(self, payload_format):
		self.json_obj["params"]["payloadFormat"] = payload_format

	def set_result_uri(self, result_uri):
		self.json_obj["params"]["resultUri"] = result_uri

	def set_notify_uri(self, notify_uri):
		self.json_obj["params"]["notifyUri"] = notify_uri

	def set_worker_id(self, worker_id):
		self.json_obj["params"]["workerId"] = worker_id

	def set_workload_id(self, workload_id):
		self.json_obj["params"]["workloadId"] = workload_id

	def set_requester_id(self, requester_id):
		self.json_obj["params"]["requesterId"] = requester_id

	def set_worker_encryption_key(self, worker_encryption_key):
		self.json_obj["params"]["workerEncryptionKey"] = worker_encryption_key

	def set_data_encryption_algorithm(self, data_encryption_algorithm):
		self.json_obj["params"]["dataEncryptionAlgorithm"] = \
			data_encryption_algorithm

	def set_encrypted_session_key(self, encrypted_session_key):
		self.json_obj["params"]["encryptedSessionKey"] = encrypted_session_key

	def set_session_key_iv(self, session_key_iv):
		self.json_obj["params"]["sessionKeyIv"] = session_key_iv

	def set_requester_nonce(self, requester_nonce):
		self.json_obj["params"]["requesterNonce"] = requester_nonce

	def update_encrypted_request_hash(self):
		self.json_obj["params"]["encryptedRequestHash"] = ""

	def update_requester_signature(self):
		self.json_obj["params"]["requesterSignature"] = ""

	def set_verifying_key(self, verifying_key):
		self.json_obj["params"]["verifyingKey"] = verifying_key

	def add_in_data(self, data, data_hash=None, encrypted_data_encryption_key=None):
		in_data_copy = self.json_obj["params"]["inData"]
		index = len(in_data_copy)
		in_data_copy.append({})
		in_data_copy[index]["index"] = index
		in_data_copy[index]["data"] = data
		if data_hash:
			in_data_copy[index]["dataHash"] = data_hash
		if encrypted_data_encryption_key:
			in_data_copy[index]["encryptedDataEncryptionKey"] = \
					encrypted_data_encryption_key
			in_data_copy[index]["iv"] = iv
		else:
			in_data_copy[index]["encryptedDataEncryptionKey"] = ""
			in_data_copy[index]["iv"] = ""
		self.json_obj["params"]["inData"] = in_data_copy

	def add_out_data(self, data_hash=None, encrypted_data_encryption_key=None):
		out_data_copy = self.json_obj["params"]["outData"]
		index = len(out_data_copy)
		out_data_copy.append({})
		out_data_copy[index]["index"] = index
		out_data_copy[index]["data"] = ""
		if data_hash:
			out_data_copy[index]["dataHash"] = data_hash
		if encrypted_data_encryption_key:
			out_data_copy[index]["encryptedDataEncryptionKey"] = \
				encrypted_data_encryption_key
		else:
			out_data_copy[index]["encryptedDataEncryptionKey"] = ""
		out_data_copy[index]["iv"] = ""
		self.json_obj["params"]["outData"] = out_data_copy

	# Use these if you want to pass json to WorkOrderJRPCImpl
	def get_params(self):
		params_copy = self.json_obj["params"].copy()
		params_copy.pop("inData")
		params_copy.pop("outData")
		return params_copy

	def get_in_data(self):
		return self.json_obj["params"]["inData"]

	def get_out_data(self):
		return self.json_obj["params"]["outData"]

class WorkOrderGetResultJson(WorkOrderJson):
	def __init__(self, id, work_order_id):
		super().__init__(id, "WorkOrderGetResult", work_order_id)

class WorkOrderReceiptRetrieveJson(WorkOrderJson):
	def __init__(self, id, work_order_id):
		super().__init__(id, "WorkOrderReceiptRetrieve", work_order_id)
