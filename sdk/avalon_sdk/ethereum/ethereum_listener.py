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

import os
import web3
import json
import asyncio
import logging
import random
from eth_abi import decode_abi
from utility.hex_utils import is_valid_hex_str
from avalon_sdk.ethereum.ethereum_wrapper import get_keccak_for_text
from avalon_sdk.http_client.http_jrpc_client import HttpJrpcClient

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

LISTENER_SLEEP_DURATION = 5  # second


class BlockchainInterface:
    def __init__(self, config):
        # TODO: store list of contracts?
        self._config = config
        self._uri_client = HttpJrpcClient(config["ethereum"]["event_provider"])

    def newListener(self, contract, event, fromBlock='latest'):
        if self._is_jrpc_evt_required():
            # This will return the filter_id of newly created filter
            return self._new_JRPC_listener(event)
        else:
            return contract.events[event].createFilter(fromBlock=fromBlock)

    def _new_JRPC_listener(self, event, fromBlock='latest'):
        evt_hash = None
        if event == "workOrderCompleted":
            evt_hash = get_keccak_for_text(
                "workOrderCompleted(bytes32,bytes32,uint256,string,"
                + "uint256,bytes4)")
        elif event == "workOrderSubmitted":
            evt_hash = get_keccak_for_text(
                "workOrderSubmitted(bytes32,bytes32,bytes32,string,"
                + "uint256,address,bytes4)")
        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": "eth_newFilter",
            "id": random.randint(0, 100000)
        }
        contract_address = self\
            ._config["ethereum"]["work_order_contract_address"]
        json_rpc_request["params"] = get_new_filter_payload(evt_hash,
                                                            contract_address)

        logging.debug("New filter request : %s", json.dumps(json_rpc_request))
        response = self._uri_client._postmsg(json.dumps(json_rpc_request))
        return response['result']

    def _is_jrpc_evt_required(self):
        """
        This function checks if the Ethereum client configured
        uses different endpoints for events & transaction calls
        """
        provider = self._config["ethereum"]["provider"]
        evt_provider = self._config["ethereum"]["event_provider"]

        if provider == evt_provider:
            return False
        else:
            return True


def get_last_read_block():
    f = None
    try:
        f = open("bookmark", 'r')
        block_num = f.readline()
        return 0 if block_num == '' else int(block_num)
    except FileNotFoundError as e:
        logging.error(e)
        return 0
    finally:
        if f is not None:
            f.close()


def set_last_read_block(block_num):
    with open("bookmark", 'w') as f:
        f.seek(0)
        f.write(str(block_num))


def get_new_filter_payload(evt_hash, contract_address):
    params = {}
    params["fromBlock"] = "earliest"
    params["toBlock"] = "latest"
    params["address"] = contract_address
    params["topics"] = [[evt_hash]]

    return [params]


def parse_jrpc_evt(evt, wo_submitted_hash, wo_completed_hash):
    """
    This method parses an event log and converts it to an
    intelligible format
    """
    data = evt["data"]
    indexed_data = evt["topics"]
    evt_hash = indexed_data[0]
    if is_valid_hex_str(evt["blockNumber"]):
        block_number = int(evt["blockNumber"], 16)
    else:
        block_number = evt["blockNumber"]

    if evt_hash == wo_submitted_hash:
        workOrderRequest, errCode, senderAddress, ver = decode_abi(
            ["string", "uint256", "address", "bytes4"],
            bytes.fromhex(data[2:]))  # Truncate preceeding '0x'

        return {"args": {"workOrderRequest": workOrderRequest},
                "event": "workOrderSubmitted",
                "blockNumber": block_number}

    elif evt_hash == wo_completed_hash:
        requesterId, workOrderId,  workOrderStatus, workOrderResponse,\
            errorCode, version = decode_abi(
                ["bytes32", "bytes32", "uint256",
                 "string", "uint256", "bytes4"],
                bytes.fromhex(data[2:]))
        # TODO : Extract necessary fields into event to be returned
        return {"args": {"workOrderId": workOrderId, "version": version,
                         "workOrderResponse": workOrderResponse,
                         "requesterId": requesterId,
                         "workOrderStatus": workOrderStatus,
                         "errorCode": errorCode},
                "blockNumber": block_number, "event": "workOrderCompleted"}


def normalize_event(evt, wo_submitted_hash, wo_completed_hash):
    """
    This method reads "jsonrpc" field to detect the event source and format
    it to give all events a similar structure
    """
    try:
        jrpc = evt["jsonrpc"]
    except KeyError as e:
        return evt
    return parse_jrpc_evt(evt, wo_submitted_hash, wo_completed_hash)


class EventProcessor:
    def __init__(self, config):
        self._config = config
        self._uri_client = HttpJrpcClient(config["ethereum"]["event_provider"])
        self._wo_completed_hash = get_keccak_for_text(
            "workOrderCompleted(bytes32,bytes32,uint256,string,"
            + "uint256,bytes4)")
        self._wo_submitted_hash = get_keccak_for_text(
            "workOrderSubmitted(bytes32,bytes32,bytes32,string,"
            + "uint256,address,bytes4)")

    async def listener(self, event_filter):
        logging.info("Started listener for events from blockchain")
        while True:
            # Check for any new event logs since the last poll
            # on this filter. Though using events, this is not
            # fully asynchronous.
            for event in event_filter.get_new_entries():
                await self.queue.put(event)
                logging.debug("Event pushed into listener Queue")
            await asyncio.sleep(LISTENER_SLEEP_DURATION)

    async def jrpc_listener(self, event_filter):
        logging.info("Started jrpc listener for events from blockchain")
        while True:
            json_rpc_request = {
                "jsonrpc": "2.0",
                "method": "eth_getFilterLogs",
                "id": random.randint(0, 100000)
            }
            json_rpc_request["params"] = [event_filter]

            logging.debug("New events request %s",
                          json.dumps(json_rpc_request))
            response = self._uri_client._postmsg(json.dumps(json_rpc_request))

            events = response['result']
            last_processed_block = get_last_read_block()

            for event in events:
                block_num = event["blockNumber"]
                block_num = int(block_num, 16) if is_valid_hex_str(block_num)\
                    else block_num
                if block_num > last_processed_block:
                    # Placeholder flag to mark event format. Currently
                    # two types of event mechanism are being supported.
                    # The event formats for the two vary slightly which
                    # necessitates the use of a flag to distinguish.
                    event["jsonrpc"] = "2.0"
                    # These events being put by the listener are meant to be
                    # used by the handlers consuming from the same queue
                    await self.queue.put(event)
                    logging.debug("Event pushed into listener queue")

            await asyncio.sleep(LISTENER_SLEEP_DURATION)

    async def handler(self, callback, *kargs, **kwargs):
        logging.info("Started handler to handle events")
        while True:
            event = await self.queue.get()
            logging.debug("Event popped from listener queue")
            normalized_event = normalize_event(event, self._wo_submitted_hash,
                                               self._wo_completed_hash)

            set_last_read_block(normalized_event["blockNumber"])

            callback(normalized_event, *kargs, **kwargs)
            self.queue.task_done()

    async def sync_handler(self, *kargs, **kwargs):
        logging.info("Started synchronous handler to handle an event")
        event = await self.queue.get()
        logging.debug("Event popped from listener queue")
        normalized_event = normalize_event(event, self._wo_submitted_hash,
                                           self._wo_completed_hash)
        set_last_read_block(normalized_event["blockNumber"])
        self.queue.task_done()
        return normalized_event

    async def start(self, event_filter, callback, *kargs, **kwargs):
        self.queue = asyncio.Queue()
        loop = asyncio.get_event_loop()
        self.listeners = self.get_listeners(loop, event_filter)
        self.handlers = [loop.create_task(self.handler(
            callback, *kargs, **kwargs)) for _ in range(1)]

        await asyncio.gather(*self.listeners)  # infinite loop
        await self.queue.join()  # this code should never run
        await self.stop()  # this code should never run

    async def get_event_synchronously(self, event_filter, *kargs, **kwargs):
        """
        Get a single event synchronously using the event_filter
        provided.
        Returns an event received for the event_filter used.
        """
        self.queue = asyncio.Queue()
        loop = asyncio.get_event_loop()
        self.listeners = self.get_listeners(loop, event_filter)
        self.handlers = [loop.create_task(self.sync_handler(*kargs, **kwargs))]

        handler_result = await asyncio.gather(*self.handlers)

        return handler_result

    def get_listeners(self, loop, event_filter):
        # Check if the event_filter is an id returned from createNewFilter
        # JRPC call in which case it should be a hex string. Else it is a
        # filter created using web3 library
        if isinstance(event_filter, str) and is_valid_hex_str(event_filter):
            return [loop.create_task(
                self.jrpc_listener(event_filter)) for _ in range(1)]
        else:
            return [loop.create_task(
                self.listener(event_filter)) for _ in range(1)]

    async def stop(self):
        for process in self.listeners:
            process.cancel()
        for process in self.handlers:
            process.cancel()
        logging.debug("---exit---")
