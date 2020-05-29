#!/usr/bin/env python3

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

import sys
import json
import random
import secrets
import logging
import argparse

import config.config as pconfig
import utility.logger as plogger
import avalon_crypto_utils.signature as signature
from error_code.error_status import SignatureStatus
from listener.base_jrpc_listener import BaseJRPCListener
from avalon_sdk.work_order.work_order_params import WorkOrderParams

logger = logging.getLogger(__name__)


class KMEListener(BaseJRPCListener):
    """
    Listener to handle requests from WorkerProcessingEnclave(WPE)
    """

    # The isLeaf instance variable describes whether a resource will have
    # children and only leaf resources get rendered. KMEListener is a leaf
    # node in the derivation tree and hence isLeaf is required.
    isLeaf = True

    def __init__(self, rpc_methods):
        """
        Constructor for KMEListener. Pass through the rpc methods to the
        constructor of the BaseJRPCListener.
        Parameters :
            rpc_methods - An array of RPC methods to which requests will
                          be dispatched.
        """
        super().__init__(rpc_methods)


def construct_wo_req(in_data, workload_id, encryption_key,
                     session_key, session_iv):
    """
    Construct the parameters for a standard work order request

    Parameters :
        @param in_data - In data to be passed to workload processor
        @param workload_id - Id of the target workload
        @encryption_key - Worker encryption key
        @session_key - Session key to be embedded in request
        @session_iv - Session key iv for encryption algorithm
    Returns :
        @returns A json request prepared using parameters passed
    """
    # Create work order
    # Convert workloadId to hex
    workload_id_hex = workload_id.encode("UTF-8").hex()
    work_order_id = secrets.token_hex(32)
    requester_id = secrets.token_hex(32)
    requester_nonce = secrets.token_hex(16)
    # worker id is not known here. Hence passing a random string
    worker_id = secrets.token_hex(32)
    # Create work order params
    wo_params = WorkOrderParams(
        work_order_id, worker_id, workload_id_hex, requester_id,
        session_key, session_iv, requester_nonce,
        result_uri=" ", notify_uri=" ",
        worker_encryption_key=encryption_key,
        data_encryption_algorithm="AES-GCM-256"
    )
    wo_params.add_in_data(in_data)

    # Encrypt work order request hash
    wo_params.add_encrypted_request_hash()

    return {
        "jsonrpc": "2.0",
        "method": workload_id,
        "id": random.randint(0, 100000),
        "params": json.loads(wo_params.to_string())
    }


def verify_res_signature(work_order_res, worker_verification_key):
    """
    Verify work order result signature

    Parameters :
        @param work_order_res - Result from work order response
        @param worker_verification_key - Worker verification key
    Returns :
        @returns True - If verification succeeds
                 False - If verification fails
    """
    sig_obj = signature.ClientSignature()
    status = sig_obj.verify_signature(work_order_res, worker_verification_key)
    if status == SignatureStatus.PASSED:
        logger.info("Signature verification successful")
    else:
        logger.error("Signature verification failed")
        return False
    return True
