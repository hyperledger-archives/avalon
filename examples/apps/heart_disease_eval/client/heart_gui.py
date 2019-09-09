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
import random
import json
import argparse
import logging
import base64

import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.font as font

from service_client.generic import GenericServiceClient
import utility.utility as utility
import worker.worker_details as worker
import json_rpc_request.json_rpc_request as jrpc_request
from connectors.direct.direct_adaptor_factory_wrapper \
	import DirectAdaptorFactoryWrapper
import config.config as pconfig
import utility.logger as plogger

# Remove duplicate loggers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logger = logging.getLogger(__name__)
TCFHOME = os.environ.get("TCF_HOME", "../../")

# -----------------------------------------------------------------
# Validates that input is a non-negative int
def _int_validate(text):
	if str.isdigit(text) or text == "":
		return True
	else:
		return False

# Validates that input is a non-negative, non-special float
def _float_validate(text):
	if text == "":
		return True
	try:
		float(text)
		if float(text) < 0.0 or float(text) == float("NaN") \
			or float(text) == float("INF") or float(text) == float("-INF"):
			return False
		return True
	except ValueError:
		return False

# User entry for ints
class intEntry:
	def __init__(self, master, name):
		global cur_row
		label = tk.Label(master, text=name)
		label.grid(row=cur_row, column=0, sticky="e", pady=(5,0))
		validate = (master.register(_int_validate))
		self.entry = tk.Entry(master, validate="all", 
			validatecommand=(validate, "%P"))
		self.entry.grid(row=cur_row, column=1, padx=(10,0), pady=(5,0),
			sticky="w")
		cur_row += 1

	def get(self):
		# Fails if empty field
		try:
			return int(self.entry.get())
		except ValueError:
			return None

	def enable(self):
		self.entry.config(state=tk.NORMAL)

	def disable(self):
		self.entry.config(state=tk.DISABLED)

# User entry for floats
class floatEntry:
	def __init__(self, master, name):
		global cur_row
		label = tk.Label(master, text=name)
		label.grid(row=cur_row, column=0, sticky="e", pady=(5,))
		validate = (master.register(_float_validate))
		self.entry = tk.Entry(master, validate="all", 
			validatecommand=(validate, "%P"))
		self.entry.grid(row=cur_row, column=1, padx=(10,0), pady=(5,), 
			sticky="w")
		cur_row += 1

	def get(self):
		try:
			return float(self.entry.get())
		except ValueError:
			return None

	def enable(self):
		self.entry.config(state=tk.NORMAL)

	def disable(self):
		self.entry.config(state=tk.DISABLED)

#Radio button
class radio:
	# Options is a list of text-value pairs
	def __init__(self, master, name, options):
		global cur_row
		if not all(len(tup)==2 for tup in options):
			print("ERROR: Mismatched text-value pairs")
			exit(1)

		self.var = tk.IntVar()
		self.var.set(None)
		label = tk.Label(master, text=name)
		label.grid(row=cur_row, column=0, pady=(5,0), sticky="e")

		self.button_list = []
		for i in range(len(options)):
			button = tk.Radiobutton(master, text=options[i][0], 
				variable=self.var, value=options[i][1])
			self.button_list.append(button)
			if i==0:
				button.grid(row=cur_row, column=1, pady=(5,0), sticky="w")
			else:
				button.grid(row=cur_row, column=1, sticky="w")
			cur_row += 1

	def get(self):
		try:
			return self.var.get()
		except tk.TclError:
			return None

	def enable(self):
		for button in self.button_list:
			button.config(state=tk.NORMAL)

	def disable(self):
		for button in self.button_list:
			button.config(state=tk.DISABLED)

class resultWindow(tk.Toplevel):
	def __init__(self, parent, message):
		tk.Toplevel.__init__(self, parent)
		self.config(background="pale goldenrod")
		self.parent = parent
		# Lock main window
		self.transient(parent)
		self.grab_set()
		self.initial_focus = self
		self.initial_focus.focus_set()
		self.title("Evaluation Result")
		self.protocol("WM_DELETE_WINDOW", self.close)

		# Main content
		self.main_frame = tk.Frame(self, background="pale goldenrod")
		self.main_frame.pack()

		self.frame1 = tk.Frame(self.main_frame)
		self.frame1.pack(side=tk.LEFT)
		self.result_text = tk.StringVar()
		self.label = tk.Label(self.frame1, textvariable=self.result_text,
			width=45, background="pale goldenrod")
		default_font = font.Font(font="TkDefaultFont")
		new_font = default_font
		new_font.config(weight=font.BOLD)
		self.label.config(font=new_font)
		self.label.pack()
		self.frame2 = tk.Frame(self.main_frame, background="pale goldenrod")
		self.frame2.pack(side=tk.LEFT)

		# JSON sidebar
		self.request_button = tk.Button(
			self.frame2, text="View Request", command=self.request)
		self.request_button.pack(fill=tk.X, padx=(0,10), pady=(10,0))

		self.result_button = tk.Button(
			self.frame2, text="View Result", command=self.result)
		self.result_button.pack(fill=tk.X, padx=(0,10),pady=(10,0))

		self.receipt_button = tk.Button(
			self.frame2, text="View Receipt", command=self.receipt)
		self.receipt_button.pack(fill=tk.X, padx=(0,10),pady=(10,0))

		# Close button
		self.close_button = tk.Button(self, text="Close", command=self.close)
		self.close_button.pack(pady=(0,5))

		self.evaluate(message)

	# Submit work order and retrieve result
	def evaluate(self, message):
		self.result_text.set("Waiting for evaluation result...")
		self.update()

		# Create, sign, and submit workorder 
		# Convert workloadId to hex
		workload_id = "heart-disease-eval"
		workload_id = workload_id.encode("UTF-8").hex()
		wo_submit_json = jrpc_request.WorkOrderSubmitJson(3, 6000, "pformat",
			worker_id, workload_id, "0x1234", 
			worker_encryption_key=base64.b64decode(
				worker_obj.worker_encryption_key).hex(),
			data_encryption_algorithm="AES-GCM-256")
		wo_id = wo_submit_json.get_work_order_id()
		wo_submit_json.add_in_data(message)

		private_key = utility.generate_signing_keys()
		session_iv = utility.generate_sessioniv()
		encrypted_session_key = utility.generate_encrypted_session_key(
			session_iv, worker_obj.worker_encryption_key)
		direct_wrapper.init_work_order(config)
		# Set text for JSON sidebar
		self.request_json = json.dumps(json.loads(
			direct_wrapper.work_order_submit(
				wo_submit_json, encrypted_session_key,
				worker_obj, private_key, session_iv)), indent=4)

		# Retrieve result and set GUI result text
		wo_get_result_json = jrpc_request.WorkOrderGetResultJson(4, wo_id)
		self.result_json = json.dumps(
			direct_wrapper.work_order_get_result(
				wo_get_result_json, encrypted_session_key), indent=4)
		# Set text for JSON sidebar
		self.result_text.set(
			json.loads(self.result_json)["outData"][0]["data"])

		# Retrieve receipt
		direct_wrapper.init_work_order_receipt(config)
		wo_receipt_retrieve_json = \
			jrpc_request.WorkOrderReceiptRetrieveJson(5, wo_id)
		# Set text for JSON sidebar
		self.receipt_json = \
			json.dumps(direct_wrapper.work_order_receipt_retrieve(
				wo_receipt_retrieve_json), indent=4)

	def request(self):
		jsonWindow(self, self.request_json, "Request JSON")

	def result(self):
		jsonWindow(self, self.result_json, "Result JSON")

	def receipt(self):
		jsonWindow(self, self.receipt_json, "Receipt JSON")

	def close(self):
		self.parent.focus_set()
		self.destroy()

# Template for JSON display
class jsonWindow(tk.Toplevel):
	def __init__(self, parent, json, title):
		tk.Toplevel.__init__(self, parent)
		self.title(title)
		self.scrollbar = tk.Scrollbar(self)
		self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		self.text = tk.Text(self, yscrollcommand=self.scrollbar.set)
		self.text.insert(tk.END, json)
		self.text.config(state=tk.DISABLED)
		self.text.pack(expand=True, fill="both")

		self.scrollbar.config(command=self.text.yview)

# Create main Tkinter window
def GuiMain():
	root = tk.Tk()
	root.title("Heart Disease Evaluation")
	var_root = tk.Frame(root)
	var_root.pack(pady=(10,0))
	v_frame1 = tk.Frame(var_root)
	v_frame1.pack(fill=tk.Y, side=tk.LEFT, padx=(10,0))
	v_frame2 = tk.Frame(var_root)
	v_frame2.pack(fill=tk.Y, side=tk.LEFT, padx=(0,10))
	# Organizes parameter grid
	global cur_row
	cur_row = 0

	# Parameter grid
	age = intEntry(v_frame1, "Age")
	sex = radio(v_frame1, "Sex", [("Male", 1), ("Female", 0)])
	cp = radio(v_frame1, "Chest pain type", [("Typical angina", 1), 
		("Atypical angina", 2), ("Non-anginal pain", 3), ("Asymptomatic", 4)])
	trestbps = intEntry(v_frame1, "Resting blood pressure (mm Hg)")
	chol = intEntry(v_frame1, "Serum cholesterol (mg/dl)")
	fbs = intEntry(v_frame1, "Fasting blood sugar (mg/dl)")
	restecg = radio(v_frame1, "Resting electrocardiographic results", 
		[("Normal", 0), ("Having ST-T wave abnormality", 1), 
		("Showing hypertrophy", 2)])
	thalach = intEntry(v_frame1, "Maximum heart rate achieved")
	exang = radio(v_frame2, "Exercise induced angina", 
		[("Yes", 1), ("No", 0)])
	oldpeak = floatEntry(v_frame2, 
		"ST depression induced by exercise relative to rest")
	slope = radio(v_frame2, "Slope of the peak exercise ST segment", 
		[("Upsloping", 1), ("Flat", 2), ("Downsloping", 3)])
	ca = radio(v_frame2, "Number of major vessels colored by flouroscopy", 
		[("0", 0), ("1", 1), ("2", 2), ("3", 3)])
	thal = radio(v_frame2, "Thallium stress test", 
		[("Normal", 3), ("Fixed defect", 6), ("Reversible defect", 7)])
	num = radio (v_frame2, "Diagnosis of heart disease", 
		[("<50% diameter narrowing", 0), (">50% diameter narrowing", 1)])
	var_list = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, 
		exang, oldpeak, slope, ca, thal, num]

	# Disable/enable other variable entries/buttons based on 
	# whether string input option is selected
	def string_toggle():
		if string_use.get()==1:
			for var in var_list:
				var.disable()
			string_entry.config(state=tk.NORMAL)
		else:
			for var in var_list:
				var.enable()
			string_entry.config(state=tk.DISABLED)

	# Input vars as string option
	string_frame = tk.Frame(root)
	string_frame.pack()
	string_label = tk.Label(string_frame, text="Input variables as string")
	string_label.pack(side=tk.LEFT)
	string_use = tk.IntVar()
	string_check = tk.Checkbutton(
		string_frame, command=string_toggle, variable=string_use)
	string_check.pack(side=tk.LEFT)
	string_entry = tk.Entry(string_frame, state=tk.DISABLED)
	string_entry.pack(side=tk.LEFT)

	# Open window that will submit work order and retrieve evaluation result
	def evaluate():
		message = "Heart disease evaluation data: "
		if string_use.get()==1:
			message = message + string_entry.get()
		else:
			for var in var_list:
				if var.get()==None:
					messagebox.showwarning("Error", "Must input all variables")
					return
				message = message + str(var.get()) + " "
		root.wait_window(resultWindow(root, message))

	# "Evaluate" button
	eval_text = tk.StringVar()
	eval_label = tk.Label(root, textvariable=eval_text)
	eval_label.pack()
	eval_button = tk.Button(root, text="Evaluate", command=evaluate)
	eval_button.pack(pady=(0,10))

	root.mainloop() 

def ParseCommandLine(args) :

	global worker_obj
	global worker_id
	global verbose
	global config
	global off_chain

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
	parser.add_argument("-v", "--verbose", 
		help="increase output verbosity", 
		action="store_true")

	options = parser.parse_args(args)

	if options.config:
		conffiles = [options.config]
	else:
		conffiles = [ TCFHOME + \
			"/examples/common/python/connectors/tcf_connector.toml" ]
	confpaths = [ "." ]

	try :
		config = pconfig.parse_configuration_files(conffiles, confpaths)
		config_json_str = json.dumps(config, indent=4)
	except pconfig.ConfigurationException as e :
		logger.error(str(e))
		sys.exit(-1)

	global direct_wrapper
	direct_wrapper = DirectAdaptorFactoryWrapper(conffiles[0])

	# Whether or not to connect to the registry list on the blockchain
	off_chain = False

	if options.registry_list:
		config["ethereum"]["direct_registry_contract_address"] = \
			options.registry_list

	if options.service_uri:
		service_uri = options.service_uri
		off_chain = True
		uri_client = GenericServiceClient(service_uri) 

	if options.off_chain:
		service_uri = config["tcf"].get("json_rpc_uri")
		off_chain = True
		uri_client = GenericServiceClient(service_uri) 

	service_uri = options.service_uri
	verbose = options.verbose
	worker_id = options.worker_id

	# Initializing Worker Object
	worker_obj = worker.WorkerDetails()

def Main(args=None):
	ParseCommandLine(args)

	if verbose:
		config["Logging"] = {
			"LogFile" : "__screen__",
			"LogLevel" : "INFO"
		}
	else:
		config["Logging"] = {
			"LogFile" : "__screen__",
			"LogLevel" : "WARN"
		}
	plogger.setup_loggers(config.get("Logging", {}))
	sys.stdout = plogger.stream_to_logger(
		logging.getLogger("STDOUT"), logging.DEBUG)
	sys.stderr = plogger.stream_to_logger(
		logging.getLogger("STDERR"), logging.WARN)

	logger.info("***************** TRUSTED COMPUTE FRAMEWORK (TCF)" + \
		" *****************") 

	# Retrieve Worker Registry
	if not off_chain:
		direct_wrapper.init_worker_registry_list(config)
		registry_lookup_result = direct_wrapper.registry_lookup()
		if (registry_lookup_result[0] == 0):
			logger.warn("No registries found")
			sys.exit(1)
		registry_retrieve_result = direct_wrapper.registry_retrieve(
			registry_lookup_result[2][0])
		config["tcf"]["json_rpc_uri"] = registry_retrieve_result[0]

	# Prepare worker
	direct_wrapper.init_worker_registry(config)

	global worker_id
	if not worker_id:
		worker_lookup_json = jrpc_request.WorkerLookupJson(1, worker_type=1)
		worker_lookup_result = direct_wrapper.worker_lookup(worker_lookup_json)
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

	worker_retrieve_json = jrpc_request.WorkerRetrieveJson(2, worker_id)
	worker_obj.load_worker(direct_wrapper.worker_retrieve(worker_retrieve_json))
	logger.info("**********Worker details Updated with Worker ID" + \
		"*********\n%s\n", worker_id)

	# Open GUI
	GuiMain()

#------------------------------------------------------------------------------
Main()
