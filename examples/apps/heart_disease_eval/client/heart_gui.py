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

"""
Heart Evaluation GUI Client for use in submitting data to worker.
"""

import os
import sys
import random
import json
import argparse
import logging
import secrets

# Tkinter imports
import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.font as font
from PIL import ImageTk, Image

# Avalon imports
import crypto_utils.crypto_utility as utility
import avalon_sdk.worker.worker_details as worker
from avalon_sdk.worker.worker_details import WorkerType
from avalon_sdk.work_order.work_order_params import WorkOrderParams
from avalon_sdk.avalon_direct_client \
    import AvalonDirectClient
import config.config as pconfig
import utility.logger as plogger
import crypto_utils.crypto.crypto as crypto
from error_code.error_status import WorkOrderStatus, ReceiptCreateStatus
import crypto_utils.signature as signature
from error_code.error_status import SignatureStatus
from avalon_sdk.work_order_receipt.work_order_receipt \
     import WorkOrderReceiptRequest

# Remove duplicate loggers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logger = logging.getLogger(__name__)
# Default TCFHOME assumes PWD is examples/apps/heart_disease_eval/client :
TCFHOME = os.environ.get("TCF_HOME", "../../../../")

# GUI color scheme
BACKGROUND = "light sky blue"
ENTRY_COLOR = "light grey"
BUTTON_COLOR = "deep sky blue"
RESULT_BACKGROUND = "pale goldenrod"


# -----------------------------------------------------------------
def _generate_random_or_normal_number(normal, percent_normal, low, high):
    """Generate number "normal" for "percent_normal" % of the time.
       Otherwise, generate a random number in the interval ["low", "high"].
    """
    if percent_normal >= random.randint(0, 100):
        return normal
    return random.randint(low, high)


def _generate_random_data():
    """Generate a random data string for input as evaluation data.
       For example:    "35 0 1 67 102 125 1 95 0 10 1 1 3 1"
    """

    age = _generate_random_or_normal_number(35, 67, 18, 100)
    sex = _generate_random_or_normal_number(0, 50, 1, 1)
    cp = _generate_random_or_normal_number(4, 67, 1, 3)
    trestbps = _generate_random_or_normal_number(67, 67, 108, 218)
    chol = _generate_random_or_normal_number(102, 67, 126, 309)
    fbs = _generate_random_or_normal_number(125, 67, 98, 248)
    restecg = _generate_random_or_normal_number(0, 67, 1, 2)
    thalach = _generate_random_or_normal_number(95, 67, 61, 198)
    exang = _generate_random_or_normal_number(0, 67, 1, 1)
    oldpeak = _generate_random_or_normal_number(10, 67, 0, 100)
    slop = _generate_random_or_normal_number(0, 67, 1, 2)
    ca = _generate_random_or_normal_number(0, 67, 1, 3)
    thaldur = _generate_random_or_normal_number(3, 67, 6, 7)
    num = _generate_random_or_normal_number(0, 67, 1, 1)

    return "{} {} {} {} {} {} {} {} {} {} {} {} {} {}".format(
        age, sex, cp, trestbps, chol, fbs, restecg, thalach,
        exang, oldpeak, slop, ca, thaldur, num)


def _int_validate(text):
    """Validates that input is a non-negative integer."""

    if str.isdigit(text) or text == "":
        return True
    else:
        return False


def _float_validate(text):
    """Validates that input is a non-negative, non-special float."""

    if text == "":
        return True
    try:
        float(text)
        if float(text) < 0.0 or float(text) == float("NaN") \
                or float(text) == float("INF") \
                or float(text) == float("-INF"):
            return False
        return True
    except ValueError:
        return False


class intEntry:
    """User entry for non-negative integer."""

    def __init__(self, master, name):
        global cur_row
        label = tk.Label(master, text=name, background=BACKGROUND)
        label.grid(row=cur_row, column=0, sticky="e", pady=(5, 0))
        validate = (master.register(_int_validate))
        self.entry = tk.Entry(
            master, validate="all",
            validatecommand=(validate, "%P"), width=5,
            background=ENTRY_COLOR)
        self.entry.grid(
            row=cur_row, column=1, padx=(10, 0), pady=(5, 0), sticky="w")
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


class floatEntry:
    """User entry for non-negative, non-special floating point number."""

    def __init__(self, master, name):
        global cur_row
        label = tk.Label(master, text=name, background=BACKGROUND)
        label.grid(row=cur_row, column=0, sticky="e", pady=(5,))
        validate = (master.register(_float_validate))
        self.entry = tk.Entry(
            master, validate="all",
            validatecommand=(validate, "%P"), width=10,
            background=ENTRY_COLOR)
        self.entry.grid(row=cur_row, column=1, padx=(10, 0), pady=(5,),
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


class radio:
    """User entry for a radio button."""

    # Options is a list of text-value pairs
    def __init__(self, master, name, options):
        global cur_row
        if not all(len(tup) == 2 for tup in options):
            print("ERROR: Mismatched text-value pairs")
            exit(1)

        self.var = tk.IntVar()
        self.var.set(None)
        label = tk.Label(master, text=name, background=BACKGROUND)
        label.grid(row=cur_row, column=0, pady=(5, 0), sticky="e")

        self.button_list = []
        for i in range(len(options)):
            button = tk.Radiobutton(
                master, text=options[i][0],
                variable=self.var, value=options[i][1],
                background=BACKGROUND)
            self.button_list.append(button)
            if i == 0:
                button.grid(row=cur_row, column=1, pady=(5, 0),
                            sticky="w")
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
    """Create result window that appears after clicking "Evaluate"."""

    def __init__(self, parent, message):
        tk.Toplevel.__init__(self, parent)
        self.config(background=RESULT_BACKGROUND)
        self.parent = parent
        # Lock main window
        self.transient(parent)
        self.grab_set()
        self.initial_focus = self
        self.initial_focus.focus_set()
        self.title("Evaluation Result")
        self.protocol("WM_DELETE_WINDOW", self.close)

        # Main content
        self.main_frame = tk.Frame(self, background=RESULT_BACKGROUND)
        self.main_frame.pack()

        self.frame1 = tk.Frame(self.main_frame)
        self.frame1.pack(side=tk.LEFT)
        self.result_text = tk.StringVar()
        self.label = tk.Label(
            self.frame1, textvariable=self.result_text, width=45,
            background=RESULT_BACKGROUND)
        default_font = font.Font(font="TkDefaultFont")
        new_font = default_font
        new_font.config(weight=font.BOLD)
        self.label.config(font=new_font)
        self.label.pack()

        # JSON window display sidebar buttons
        self.frame2 = tk.Frame(self.main_frame, background=RESULT_BACKGROUND)
        self.frame2.pack(side=tk.LEFT)

        self.frame2 = tk.Frame(
            self.frame2, background=RESULT_BACKGROUND)
        self.frame2.pack(side=tk.LEFT)

        self.request_button = tk.Button(
            self.frame2, text="View Request", command=self.request,
            background=BUTTON_COLOR)
        self.request_button.pack(fill=tk.X, padx=(0, 10), pady=(10, 0))

        self.result_button = tk.Button(
            self.frame2, text="View Result", command=self.result,
            background=BUTTON_COLOR)
        self.result_button.pack(fill=tk.X, padx=(0, 10), pady=(10, 0))

        self.receipt_button = tk.Button(
            self.frame2, text="View Receipt",
            command=self.receipt, background=BUTTON_COLOR)
        self.receipt_button.pack(fill=tk.X, padx=(0, 10), pady=(10, 0))

        # Close button
        self.close_button = tk.Button(
            self, text="Close",
            command=self.close, background=BUTTON_COLOR)
        self.close_button.pack(pady=(0, 5))

        self.evaluate(message)

    def evaluate(self, message):
        """Create and submit workorder and wait for result."""

        self.result_text.set("Waiting for evaluation result...")
        self.update()

        # Create, sign, and submit workorder.
        # Convert workloadId to hex.
        workload_id = "heart-disease-eval"
        workload_id = workload_id.encode("UTF-8").hex()
        session_iv = utility.generate_iv()
        session_key = utility.generate_key()
        requester_nonce = secrets.token_hex(16)
        work_order_id = secrets.token_hex(32)
        requester_id = secrets.token_hex(32)
        wo_params = WorkOrderParams(
            work_order_id, worker_id, workload_id, requester_id,
            session_key, session_iv, requester_nonce,
            result_uri=" ", notify_uri=" ",
            worker_encryption_key=worker_obj.encryption_key,
            data_encryption_algorithm="AES-GCM-256"
        )
        wo_params.add_in_data(message)

        wo_params.add_encrypted_request_hash()

        private_key = utility.generate_signing_keys()
        if requester_signature:
            # Add requester signature and requester verifying_key
            if wo_params.add_requester_signature(private_key) is False:
                logger.info("Work order request signing failed")
                exit(1)

        # Set text for JSON sidebar
        req_id = 51
        self.request_json = wo_params.to_jrpc_string(req_id)

        work_order_instance = direct_jrpc.get_work_order_instance(
            config
        )
        response = work_order_instance.work_order_submit(
            wo_params.get_work_order_id(),
            wo_params.get_worker_id(),
            wo_params.get_requester_id(),
            wo_params.to_string(),
            id=req_id
        )
        logger.info("Work order submit response : {}\n ".format(
            json.dumps(response, indent=4)
        ))
        if "error" in response and response["error"]["code"] != \
                WorkOrderStatus.PENDING:
            sys.exit(1)
        # Create work order receipt
        req_id += 1
        wo_receipt_instance = direct_jrpc.get_work_order_receipt_instance(
            config
        )
        wo_request = json.loads(self.request_json)
        wo_receipt_obj = WorkOrderReceiptRequest()
        wo_create_receipt = wo_receipt_obj.create_receipt(
            wo_request,
            ReceiptCreateStatus.PENDING.value,
            private_key
        )
        logger.info("Work order create receipt request : {} \n \n ".format(
            json.dumps(wo_create_receipt, indent=4)
        ))
        # Submit work order create receipt jrpc request
        wo_receipt_resp = wo_receipt_instance.work_order_receipt_create(
            wo_create_receipt["workOrderId"],
            wo_create_receipt["workerServiceId"],
            wo_create_receipt["workerId"],
            wo_create_receipt["requesterId"],
            wo_create_receipt["receiptCreateStatus"],
            wo_create_receipt["workOrderRequestHash"],
            wo_create_receipt["requesterGeneratedNonce"],
            wo_create_receipt["requesterSignature"],
            wo_create_receipt["signatureRules"],
            wo_create_receipt["receiptVerificationKey"],
            req_id
        )

        logger.info("Work order create receipt response : {} \n \n ".format(
            wo_receipt_resp
        ))

        # Retrieve result and set GUI result text
        res = work_order_instance.work_order_get_result(
            work_order_id,
            req_id
        )
        self.result_json = json.dumps(res, indent=4)
        if "result" in res:
            sig_obj = signature.ClientSignature()
            status = sig_obj.verify_signature(
                res, worker_obj.verification_key)
            try:
                if status == SignatureStatus.PASSED:
                    logger.info("Signature verification Successful")
                    decrypted_res = utility. \
                        decrypted_response(res, session_key, session_iv)
                    logger.info("\n" +
                                "Decrypted response:\n {}".
                                format(decrypted_res))
                else:
                    logger.info("Signature verification Failed")
                    sys.exit(1)
            except Exception as err:
                logger.info("ERROR: Failed to decrypt response: %s", str(err))
                sys.exit(1)
        else:
            logger.info("\n Work order get result failed {}\n".format(res))
            sys.exit(1)

        # Set text for JSON sidebar
        self.result_text.set(
            decrypted_res[0]["data"])

        # Retrieve receipt
        # Set text for JSON sidebar
        req_id += 1
        self.receipt_json = json.dumps(
            wo_receipt_instance.work_order_receipt_retrieve(
                work_order_id,
                req_id
            ),
            indent=4
        )

    def request(self):
        jsonWindow(self, self.request_json, "Request JSON")

    def result(self):
        jsonWindow(self, self.result_json, "Result JSON")

    def receipt(self):
        jsonWindow(self, self.receipt_json, "Receipt JSON")

    def close(self):
        self.parent.focus_set()
        self.destroy()


class jsonWindow(tk.Toplevel):
    """Template for JSON display
       (from clicking View Request/Result/Receipt buttons).
    """

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


def gui_main():
    """Create main Tkinter window and "Evaluate" event handler."""

    root = tk.Tk()
    root.title("Heart Disease Evaluation")
    root.config(background=BACKGROUND)

    # Display image
    imageFile = TCFHOME + \
        "/examples/apps/heart_disease_eval/images/ecg.jpg"
    img = ImageTk.PhotoImage(Image.open(imageFile))
    canvas = tk.Canvas(root, width=290, height=220, background=BACKGROUND)
    canvas.pack()
    canvas.create_image(20, 20, anchor=tk.NW, image=img)

    # Setup left and right frames for data entry
    var_root = tk.Frame(root, background=BACKGROUND)
    var_root.pack(pady=(10, 0))
    v_frame1 = tk.Frame(var_root, background=BACKGROUND)
    v_frame1.pack(fill=tk.Y, side=tk.LEFT, padx=(10, 0))
    v_frame2 = tk.Frame(var_root, background=BACKGROUND)
    v_frame2.pack(fill=tk.Y, side=tk.LEFT, padx=(0, 10))
    # Organizes parameter grid
    global cur_row
    cur_row = 0

    # Parameter grid
    age = intEntry(v_frame1, "Age")
    sex = radio(v_frame1, "Sex", [("Male", 1), ("Female", 0)])
    cp = radio(v_frame1, "Chest pain type", [("Typical angina", 1),
               ("Atypical angina", 2), ("Non-anginal pain", 3),
               ("Asymptomatic", 4)])
    trestbps = intEntry(v_frame1, "Resting blood pressure\n (mm Hg)")
    chol = intEntry(v_frame1, "Serum cholesterol (mg/dl)")
    fbs = intEntry(v_frame1, "Fasting blood sugar (mg/dl)")
    restecg = radio(v_frame1, "Electrocardiographic\n resting results",
                    [("Normal", 0), ("ST-T wave abnormality", 1),
                     ("Showing hypertrophy", 2)])
    thalach = intEntry(v_frame1, "Maximum heart rate")
    exang = radio(v_frame2, "Exercise induced angina",
                  [("Yes", 1), ("No", 0)])
    oldpeak = floatEntry(
        v_frame2, "ST depression induced by\n exercise relative to rest")
    slope = radio(v_frame2, "Slope of the peak\n exercise ST segment",
                  [("Upsloping", 0), ("Flat", 1), ("Downsloping", 2)])
    ca = radio(v_frame2, "Major vessels colored\n by flouroscopy",
               [("0", 0), ("1", 1), ("2", 2), ("3", 3)])
    thal = radio(
        v_frame2,
        "Thallium stress test",
        [("Normal", 3), ("Fixed defect", 6), ("Reversible defect", 7)])
    num = radio(v_frame2, "Heart disease diagnosis",
                [("<50% diameter narrowing", 0),
                 (">50% diameter narrowing", 1)])
    var_list = [age, sex, cp, trestbps, chol, fbs, restecg, thalach,
                exang, oldpeak, slope, ca, thal, num]

    def string_toggle():
        """Disable/enable other variable entries/buttons based on
           whether string input option is selected.
        """

        if string_use.get() == 1 or random_use.get() == 1:
            for var in var_list:
                var.disable()
            string_entry.config(state=tk.NORMAL)
        else:
            for var in var_list:
                var.enable()
            string_entry.config(state=tk.DISABLED)

    # Input vars as string option with a check button to enable
    random_frame = tk.Frame(root, background=ENTRY_COLOR)
    random_frame.pack()

    # Option to generate random data entry
    random_use = tk.IntVar()
    random_check = tk.Checkbutton(
        random_frame, command=string_toggle, variable=random_use,
        background=BACKGROUND)
    random_check.pack(side=tk.LEFT)
    random_label = tk.Label(
        random_frame,
        text="Generate random data ",
        background=BACKGROUND)
    random_label.pack(side=tk.LEFT)

    # Option to enter data as space-separated string entries
    string_frame = tk.Frame(root, background=ENTRY_COLOR)
    string_frame.pack()
    string_use = tk.IntVar()
    string_check = tk.Checkbutton(
        string_frame, command=string_toggle, variable=string_use,
        background=BACKGROUND)
    string_check.pack(side=tk.LEFT)
    string_label = tk.Label(
        string_frame,
        text="Input variables as a string",
        background=BACKGROUND)
    string_label.pack(side=tk.LEFT)
    string_entry = tk.Entry(
        string_frame, state=tk.DISABLED, width=50,
        background=ENTRY_COLOR)
    string_entry.pack(side=tk.LEFT)

    def evaluate():
        """Open window that will submit work order and retrieve
           an evaluation result.
        """

        message = "Heart disease evaluation data: "
        if string_use.get() == 1:  # input is space-separated numbers
            input_data = string_entry.get()
            if input_data is None or len(input_data) == 0:
                messagebox.showwarning(
                    "Error", "Must input space-separated variables")
                return
            message = message + input_data

        elif random_use.get() == 1:
            input_data = _generate_random_data()
            if input_data is None or len(input_data) == 0:
                messagebox.showwarning(
                    "Error", "Random variable generation error")
                return
            message = message + input_data
        else:
            for var in var_list:
                if var.get() is None:
                    messagebox.showwarning("Error", "Must input all variables")
                    return
                message = message + str(var.get()) + " "
        root.wait_window(resultWindow(root, message))

    def aggregate():
        """Open window that will submit work order to retrieve
           an aggregate result.
        """

        message = "Heart disease aggregate data: "
        root.wait_window(resultWindow(root, message))

    # "Evaluate" button
    eval_text = tk.StringVar()
    eval_label = tk.Label(root, textvariable=eval_text,
                          background=BACKGROUND)
    eval_label.pack()
    eval_button = tk.Button(root, text="Evaluate", command=evaluate,
                            background=BUTTON_COLOR)
    eval_button.pack()

    # "Aggregate" button
    aggr_text = tk.StringVar()
    aggr_label = tk.Label(root, textvariable=aggr_text, background=BACKGROUND)
    aggr_label.pack()
    aggr_button = tk.Button(root, text="Aggregate all data",
                            command=aggregate, background=BUTTON_COLOR)
    aggr_button.pack(pady=(0, 10))

    root.mainloop()


def parse_command_line(args):
    """Setup and parse command line arguments and help information."""

    global worker_obj
    global worker_id
    global verbose
    global config
    global off_chain
    global requester_signature

    parser = argparse.ArgumentParser()
    use_service = parser.add_mutually_exclusive_group()
    parser.add_argument(
        "-c", "--config",
        help="the config file containing the" +
        " Ethereum contract information", type=str)
    use_service.add_argument(
        "-r", "--registry-list",
        help="the Ethereum address of the registry list",
        type=str)
    use_service.add_argument(
        "-s", "--service-uri",
        help="skip URI lookup and send to specified URI",
        type=str)
    use_service.add_argument(
        "-o", "--off-chain",
        help="skip URI lookup and use the registry in the config file",
        action="store_true")
    parser.add_argument(
        "-w", "--worker-id",
        help="skip worker lookup and retrieve specified worker",
        type=str)
    parser.add_argument(
        "-v", "--verbose",
        help="increase output verbosity",
        action="store_true")
    parser.add_argument(
        "-rs", "--requester_signature",
        help="Enable requester signature for work order requests",
        action="store_true")

    options = parser.parse_args(args)

    if options.config:
        conf_files = [options.config]
    else:
        conf_files = [TCFHOME +
                      "/sdk/avalon_sdk/tcf_connector.toml"]
    conf_paths = ["."]

    try:
        config = pconfig.parse_configuration_files(conf_files, conf_paths)
        json.dumps(config, indent=4)
    except pconfig.ConfigurationException as e:
        logger.error(str(e))
        sys.exit(-1)

    global direct_jrpc
    direct_jrpc = AvalonDirectClient(conf_files[0])

    # Whether or not to connect to the registry list on the blockchain
    off_chain = False

    if options.registry_list:
        config["ethereum"]["direct_registry_contract_address"] = \
            options.registry_list

    if options.service_uri:
        service_uri = options.service_uri
        off_chain = True

    if options.off_chain:
        service_uri = config["tcf"].get("json_rpc_uri")
        off_chain = True

    requester_signature = options.requester_signature

    verbose = options.verbose
    worker_id = options.worker_id

    # Initializing Worker Object
    worker_obj = worker.SGXWorkerDetails()


def initialize_logging(config):
    """Initialize logging."""

    if verbose:
        config["Logging"] = {
            "LogFile": "__screen__",
            "LogLevel": "INFO"
        }
    else:
        config["Logging"] = {
            "LogFile": "__screen__",
            "LogLevel": "WARN"
        }
    plogger.setup_loggers(config.get("Logging", {}))
    sys.stdout = plogger.stream_to_logger(
        logging.getLogger("STDOUT"), logging.DEBUG)
    sys.stderr = plogger.stream_to_logger(
        logging.getLogger("STDERR"), logging.WARN)


def initialize_tcf(config):
    """Initialize Avalon: get Avalon worker instance."""

    logger.info("***************** Avalon *****************")

    # Retrieve Worker Registry
    if not off_chain:
        registry_list_instance = direct_jrpc. \
            get_worker_registry_list_instance(config)
        registry_count, lookup_tag, registry_list = \
            registry_list_instance.registry_lookup()
        logger.info("\n Registry lookup response : registry count {}\
            lookup tag {} registry list {}\n".format(
            registry_count, lookup_tag, registry_list
        ))
        if (registry_count == 0):
            logger.warn("No registries found")
            sys.exit(1)
        registry_retrieve_result = \
            registry_list_instance.registry_retrieve(
                registry_list[0])
        logger.info("\n Registry retrieve response : {}\n".format(
            registry_retrieve_result
        ))
        config["tcf"]["json_rpc_uri"] = registry_retrieve_result[0]

    # Prepare worker

    global worker_id
    if not worker_id:
        worker_registry_instance = direct_jrpc.get_worker_registry_instance(
            config
        )
        req_id = 31
        worker_lookup_result = worker_registry_instance.worker_lookup(
            worker_type=WorkerType.TEE_SGX,
            id=req_id
        )
        logger.info("\n Worker lookup response : {} \n".format(
            json.dumps(worker_lookup_result, indent=4)
        ))
        if "result" in worker_lookup_result and \
                "ids" in worker_lookup_result["result"].keys():
            if worker_lookup_result["result"]["totalCount"] != 0:
                worker_id = \
                    worker_lookup_result["result"]["ids"][0]
            else:
                logger.error("ERROR: No workers found")
                sys.exit(1)
        else:
            logger.error("ERROR: Failed to lookup worker")
            sys.exit(1)
    req_id += 1
    worker = worker_registry_instance.worker_retrieve(
        worker_id,
        req_id
    )
    logger.info("\n Worker retrieve response : {}\n".format(
        json.dumps(worker, indent=4)
    ))
    worker_obj.load_worker(
        worker
    )
    logger.info("**********Worker details Updated with Worker ID" +
                "*********\n%s\n", worker_id)


def main(args=None):
    """Entry point function."""

    parse_command_line(args)

    initialize_logging(config)

    initialize_tcf(config)

    # Open GUI
    gui_main()


# -----------------------------------------------------------------------------
main()
