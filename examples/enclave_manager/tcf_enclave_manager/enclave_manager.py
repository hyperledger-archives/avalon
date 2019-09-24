#!/usr/bin/env python3

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
import json

import tcf_enclave_helper as enclave_helper
from error_code.error_status import WorkOrderStatus
from database import connector
import sgx_work_order_request as work_order_request
from utility.tcf_types import WorkerStatus, WorkerType
import utility.utility as utils

import logging

logger = logging.getLogger(__name__)

# representation of the enclave data
enclave_data = None

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


class EnclaveManager:
    """
    Wrapper for managing Worker data
    """

    def __init__(self, config, signup_data, measurements):
        self.config = config

        self.enclave_data = signup_data
        self.sealed_data = signup_data.sealed_data
        self.verifying_key = signup_data.verifying_key
        self.encryption_key = signup_data.encryption_key

        # TODO: EncryptionKeyNonce and EncryptionKeySignature are hardcoded to dummy values.
        # Need to come up with a scheme to generate both for every unique encryption key.
        self.encryption_key_nonce = ""
        self.encryption_key_signature = ""
        self.enclave_id = signup_data.enclave_id
        self.extended_measurements = measurements

        # ProofDataType is one of TEE prefixed type
        # TODO: Read ProofDataType from config file
        self.proof_data_type = config.get("WorkerConfig")["ProofDataType"]
        self.proof_data = signup_data.proof_data

    def manager_on_boot(self, kv_helper):
        """
        Executes Boot flow of enclave manager
        """
        logger.info("Executing boot time procedure")

        # Cleanup "workers" table
        workers_list = kv_helper.lookup("workers")

        if len(workers_list) == 0:
            logger.info("No worker entries available in workers table, skipping Cleanup")
        else:
            logger.info("Clearing entries in workers table")
            for worker in workers_list:
                kv_helper.remove("workers", worker)

        worker_info = create_json_worker(self, self.config)
        logger.info("Adding enclave workers to workers table")
        worker_id = utils.strip_begin_end_key(self.enclave_id).encode("UTF-8").hex()
        kv_helper.set("workers", worker_id, worker_info)

        # Cleanup wo-processing" table
        processing_list = kv_helper.lookup("wo-processing")
        if len(processing_list) == 0:
            logger.info("No workorder entries found in wo-processing table, skipping Cleanup")
            return
        for wo in processing_list:
            logger.info("Validating workorders in wo-processing table")
            wo_json_resp = kv_helper.get("wo-responses", wo)
            wo_processed = kv_helper.get("wo-processed", wo)

            if wo_json_resp is not None:
                try:
                    wo_resp = json.loads(wo_json_resp)
                except ValueError as e:
                    logger.error(
                        "Invalid JSON format found for the response for workorder %s - %s", wo, e)
                    if wo_processed is None:
                        kv_helper.set("wo-processed", wo, WorkOrderStatus.FAILED.name)
                    kv_helper.remove("wo-processing", wo)
                    continue

                if "Response" in wo_resp and wo_resp["Response"]["Status"] == WorkOrderStatus.FAILED:
                    if wo_processed is None:
                        kv_helper.set("wo-processed", wo, WorkOrderStatus.FAILED.name)
                    logger.error("Work order processing failed, removing it from wo-processing table")
                    kv_helper.remove("wo-processing", wo)
                    continue

                wo_receipt = kv_helper.get("wo-receipts", wo)
                if wo_receipt is None:
                    # create receipt
                    logger.info("Creating receipt in boot flow")
                    wo_receipt = create_receipt(wo, wo_json_resp)
                    logger.info("Receipt created for workorder %s during boot", wo_receipt)
                    kv_helper.set("wo-receipts", wo, wo_receipt)

                if wo_processed is None:
                    kv_helper.set("wo-processed", wo, WorkOrderStatus.SUCCESS.name)
            else:
                logger.info("No response found for the workorder %s,"
                            "hence placing the workorder request back in wo-scheduled", wo)
                kv_helper.set("wo-scheduled", wo,  WorkOrderStatus.SCHEDULED.name)

            logger.info("Finally deleting workorder %s from wo-processing table", wo)
            kv_helper.remove("wo-processing", wo)

        # End of for-loop

    # -----------------------------------------------------------------
    def process_work_orders(self, kv_helper):
        """
        Executes Run time flow of enclave manager
        """
        logger.info("Processing work orders")
        try:
            # Get all workorders requests from KV storage lookup and process
            list_of_workorders = kv_helper.lookup("wo-scheduled")

            if not list_of_workorders:
                logger.info("Received empty list of work orders from wo-scheduled table")
                return

        except Exception as e:
            logger.error("Problem while getting keys from wo-scheduled table")
            return

        for wo_id in list_of_workorders:
            try:
                kv_helper.set("wo-processing", wo_id, WorkOrderStatus.PROCESSING.name)

                # Get JSON workorder request corresponding to wo_id
                wo_json_req = kv_helper.get("wo-requests", wo_id)
                if wo_json_req is None:
                    logger.error("Received empty work order corresponding to id %s"
                                 "from wo-requests table", wo_id)
                    kv_helper.remove("wo-processing", wo_id)
                    return

            except Exception as e:
                logger.error("Problem while reading the work order %s"
                             "from wo-requests table", wo_id)
                kv_helper.remove("wo-processing", wo_id)
                return

            logger.info("Create workorder entry %s in wo-processing table", wo_id)
            kv_helper.set("wo-processing", wo_id,  WorkOrderStatus.PROCESSING.name)

            logger.info("Delete workorder entry %s from wo-scheduled table", wo_id)
            kv_helper.remove("wo-scheduled", wo_id)

            logger.info("Validating JSON workorder request %s", wo_id)
            validation_status = validate_request(wo_json_req)

            if not validation_status:
                logger.error(
                    "JSON validation for Workorder %s failed. Handling Failure scenarios", wo_id)
                wo_response["Response"]["Status"] = WorkOrderStatus.FAILED
                wo_response["Response"]["Message"] = "Workorder JSON request is invalid"
                kv_helper.set("wo-responses", wo_id, json.dumps(wo_response))
                kv_helper.set("wo-processed", wo_id,  WorkOrderStatus.FAILED.name)
                kv_helper.remove("wo-processing", wo_id)
                return

            # Execute work order request
            logger.info("Execute workorder with id %s", wo_id)
            wo_json_resp = execute_work_order(self.enclave_data, wo_json_req)
            wo_resp = json.loads(wo_json_resp)
            if "Response" in wo_resp and wo_resp["Response"]["Status"] == WorkOrderStatus.FAILED:
                logger.error("error in Response")
                kv_helper.set("wo-processed", wo_id, WorkOrderStatus.FAILED.name)
                kv_helper.set("wo-responses", wo_id, wo_json_resp)
                kv_helper.remove("wo-processing", wo_id)
                return

            logger.info("Mark workorder status for workorder id %s to Completed in wo-processed", wo_id)
            kv_helper.set("wo-processed", wo_id,  WorkOrderStatus.SUCCESS.name)

            logger.info("Create entry in wo-responses table for workorder %s", wo_id)
            kv_helper.set("wo-responses", wo_id, wo_json_resp)

            logger.info("Create workorder receipt for workorder %s", wo_id)
            receipt = create_receipt(wo_id, wo_json_resp)
            logger.info("receipt for the workorder id %s is %s", wo_id, receipt)

            logger.info("Create entry in wo-receipts table for workorder %s", wo_id)
            kv_helper.set("wo-receipts", wo_id, receipt)

            logger.info("Delete workorder entry %s from wo-processing table", wo_id)
            kv_helper.remove("wo-processing", wo_id)

        # end of for loop


# -----------------------------------------------------------------
def create_enclave_signup_data():
    """
    Create enclave signup data
    """
    try:
        enclave_signup_data = enclave_helper.EnclaveHelper.create_enclave_signup_data()
    except Exception as e:
        logger.error("failed to create enclave signup data; %s", str(e))
        sys.exit(-1)

    return enclave_signup_data

# -----------------------------------------------------------------


def execute_work_order(enclave_data, input_json_str, indent=4):
    """
    Submits workorder request to Worker enclave and retrieves the response
    """
    try:
        wo_request = work_order_request.SgxWorkOrderRequest(
            enclave_data,
            input_json_str)
        wo_response = wo_request.execute()

        try:
            json_response = json.dumps(wo_response, indent=indent)
        except:
            logger.error("ERROR: Failed to serialize JSON")
            wo_response["Response"]["Status"] = WorkOrderStatus.FAILED
            wo_response["Response"]["Message"] = "Failed to serialize JSON"
            json_response = json.dumps(wo_response)

    except Exception as e:
        logger.error("failed to execute work order; %s", str(e))
        wo_response["Response"]["Status"] = WorkOrderStatus.FAILED
        wo_response["Response"]["Message"] = str(e)
        json_response = json.dumps(wo_response)

    return json_response


# -----------------------------------------------------------------
def create_receipt(wo_id, wo_response):
    """
    Create work order receipt corresponding to workorder id
    """
    # Storing wo-response as receipt as of now. Receipt structure may get modified in future.
    return wo_response


# -----------------------------------------------------------------
def validate_request(wo_request):
    """
    Validate JSON workorder request
    """
    try:
        j_req = json.loads(wo_request)
    except ValueError as e:
        logger.error("Invalid JSON format found for workorder - %s", e)
        return False
    return True


# -----------------------------------------------------------------
def create_json_worker(enclave_data, config):
    """
    Create JSON worker object which gets saved in KvStorage
    """
    worker_type_data = dict()
    worker_type_data["verificationKey"] = enclave_data.verifying_key
    worker_type_data["extendedMeasurements"] = enclave_data.extended_measurements
    worker_type_data["proofDataType"] = enclave_data.proof_data_type
    worker_type_data["proofData"] = enclave_data.proof_data
    worker_type_data["encryptionKey"] = enclave_data.encryption_key
    worker_type_data["encryptionKeySignature"] = enclave_data.encryption_key_signature

    worker_info = dict()
    worker_info["workerType"] = WorkerType.TEE_SGX.value
    worker_info["organizationId"] = config.get("WorkerConfig")["OrganizationId"]
    worker_info["applicationTypeId"] = config.get("WorkerConfig")["ApplicationTypeId"]

    details_info = dict()
    details_info["workOrderSyncUri"] = config.get("WorkerConfig")["WorkOrderSyncUri"]
    details_info["workOrderAsyncUri"] = config.get("WorkerConfig")["WorkOrderAsyncUri"]
    details_info["workOrderPullUri"] = config.get("WorkerConfig")["WorkOrderPullUri"]
    details_info["workOrderNotifyUri"] = config.get("WorkerConfig")["WorkOrderNotifyUri"]
    details_info["receiptInvocationUri"] = config.get("WorkerConfig")["ReceiptInvocationUri"]
    details_info["workOrderInvocationAddress"] = config.get(
        "WorkerConfig")["WorkOrderInvocationAddress"]
    details_info["receiptInvocationAddress"] = config.get(
        "WorkerConfig")["ReceiptInvocationAddress"]
    details_info["fromAddress"] = config.get("WorkerConfig")["FromAddress"]
    details_info["hashingAlgorithm"] = config.get("WorkerConfig")["HashingAlgorithm"]
    details_info["signingAlgorithm"] = config.get("WorkerConfig")["SigningAlgorithm"]
    details_info["keyEncryptionAlgorithm"] = config.get("WorkerConfig")["KeyEncryptionAlgorithm"]
    details_info["dataEncryptionAlgorithm"] = config.get("WorkerConfig")["DataEncryptionAlgorithm"]
    details_info["workOrderPayloadFormats"] = config.get("WorkerConfig")["workOrderPayloadFormats"]
    details_info["workerTypeData"] = worker_type_data

    worker_info["details"] = details_info
    worker_info["status"] = WorkerStatus.ACTIVE.value

    # JSON serialize worker_info
    json_worker_info = json.dumps(worker_info)
    logger.info("JSON serialized worker info is %s", json_worker_info)
    return json_worker_info


# -----------------------------------------------------------------
def start_enclave_manager(config):
    """
    Instantiate KvStorage, Execute boot flow and run time flow
    """
    global enclave_data
    if config.get("KvStorage") is None:
        logger.error("Kv Storage path is missing")
        sys.exit(-1)
    try:
        logger.debug("initialize the enclave")
        # Extended measurements is a list of enclave basename and enclave measurement
        extended_measurements = enclave_helper.initialize_enclave(config.get("EnclaveModule"))
    except Exception as e:
        logger.exception("failed to initialize enclave; %s", str(e))
        sys.exit(-1)

    logger.info("creating a new enclave")
    enclave_signup_data = create_enclave_signup_data()

    logger.info("initialize enclave_manager")
    enclave_manager = EnclaveManager(config, enclave_signup_data, extended_measurements)
    logger.info("Enclave manager started")

    try:
        (kv_helper, _) = connector.open(config)
    except Exception as err:
        logger.error(f"Failed to open KV storage interface, Exiting SGX Enclave manager: {err}")
        sys.exit(-1)

    try:
        logger.info("----------------------- Starting Boot time flow -----------------------")
        enclave_manager.manager_on_boot(kv_helper)
        logger.info("----------------------- Boot time flow Complete -----------------------")
    except:
        logger.error("Failed to execute boot time flow, Exiting SGX Enclave manager...")
        exit(1)

    try:
        sleep_interval = int(config["EnclaveManager"]["sleep_interval"])
    except:
        logger.error("Failed to get sleep interval from config file. setting sleep interval to 10 secs")
        sleep_interval = 10

    try:
        while True:
            # Poll KV storage for new work-order requests and process
            enclave_manager.process_work_orders(kv_helper)
            logger.info("Enclave manager sleeping for %d secs", sleep_interval)
            time.sleep(sleep_interval)
    except:
        logger.error("Error while processing work-order. Shutting down enclave manager")
        exit(1)


TCFHOME = os.environ.get("TCF_HOME", "../../../../")

# -----------------------------------------------------------------
# -----------------------------------------------------------------


def parse_command_line(config, args):
    """
    Parse command line arguments
    """
    # global consensus_file_name

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--logfile", help="Name of the log file, __screen__ for standard output", type=str)
    parser.add_argument("--loglevel", help="Logging leve", type=str)

    options = parser.parse_args(args)

    if config.get("Logging") is None:
        config["Logging"] = {
            "LogFile": "__screen__",
            "LogLevel": "INFO"
        }
    if options.logfile:
        config["Logging"]["LogFile"] = options.logfile
    if options.loglevel:
        config["Logging"]["LogLevel"] = options.loglevel.upper()


# -----------------------------------------------------------------
def main(args=None):
    import config.config as pconfig
    import utility.logger as plogger

    # parse out the configuration file first
    conffiles = ["tcs_config.toml"]
    confpaths = [".", TCFHOME + "/" + "config"]

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="configuration file", nargs="+")
    parser.add_argument("--config-dir", help="configuration folder", nargs="+")
    (options, remainder) = parser.parse_known_args(args)

    if options.config:
        conffiles = options.config

    if options.config_dir:
        confpaths = options.config_dir

    try:
        config = pconfig.parse_configuration_files(conffiles, confpaths)
        json.dumps(config, indent=4)
    except pconfig.ConfigurationException as e:
        logger.error(str(e))
        sys.exit(-1)

    plogger.setup_loggers(config.get("Logging", {}))
    sys.stdout = plogger.stream_to_logger(logging.getLogger("STDOUT"), logging.DEBUG)
    sys.stderr = plogger.stream_to_logger(logging.getLogger("STDERR"), logging.WARN)

    parse_command_line(config, remainder)
    logger.info("Starting Enclave manager")
    start_enclave_manager(config)


main()
