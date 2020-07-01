#!/usr/bin/python
# Copyright IBM Corp. 2020 All Rights Reserved.
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

import asyncio
import logging
import json
import random
from hfc.fabric.transaction.tx_context import create_tx_context
from hfc.fabric.transaction.tx_proposal_request \
    import create_tx_prop_req, CC_INVOKE, CC_TYPE_GOLANG, TXProposalRequest
from hfc.util.utils import build_tx_req, send_transaction
from hfc.util.crypto.crypto import ecies
from hfc.fabric.client import Client

from avalon_sdk.connector.blockchains.fabric import base

logger = logging.getLogger(__name__)


class TxCommitter(base.ClientBase):
    """
    Utility class to invoke Fabric chain code and query
    chain code.
    """
    def __init__(self, profile, channel_name,
                 org_name, peer_name, user_name):
        super().__init__(profile, channel_name,
                         org_name, peer_name, user_name)

    def _get_endorsers(self, queryonly=False):
        """
        Get the endorsing peers.

        Parameters:
        queryonly  If the invocation does not result in ledger change,
                   queryonly should be set to True.
                   If the invocation does result in ledger change, it should
                   be set to False.
        """
        endorsers = dict()
        uniqueOrgs = dict()
        for org in self.client.organizations.values():
            if len(org._peers) > 0 and org._mspid not in uniqueOrgs.keys():
                key = random.choice(org._peers)
                endorsers[key] = self.client.peers[key]
                uniqueOrgs[org._mspid] = {}
                if queryonly:
                    break
        return endorsers

    def cc_invoke(self, args, cc_name, fcn, cc_version, queryonly=False):
        """
        Invoke a chaincode method.

        Parameters:
        args       JSON RPC serialized data used as the
                   sole parameter to invoke the chaincode
        cc_name    chaincode name
        fcn        chaincode function name to be invoked
        cc_version chaincode version to be used
        queryonly  If the invocation does not result in ledger change,
                   queryonly should be set to True.
                   If the invocation does result in ledger change, it should
                   be set to False.
        """
        if queryonly:
            return self.cc_query(args, cc_name, fcn)

        loop = asyncio.get_event_loop()
        crypto = ecies()

        endorses = self._get_endorsers(queryonly)

        tran_prop_req = create_tx_prop_req(
            prop_type=CC_INVOKE,
            cc_type=CC_TYPE_GOLANG, cc_name=cc_name, fcn=fcn,
            cc_version=cc_version, args=args)

        tx_context = create_tx_context(self.user, crypto, tran_prop_req)

        responses, proposal, header = self.channel.send_tx_proposal(
            tx_context, endorses.values())

        res = loop.run_until_complete(asyncio.gather(*responses))

        tran_req = build_tx_req((res, proposal, header))

        tx_context_tx = create_tx_context(self.user,
                                          crypto,
                                          TXProposalRequest())

        responses = loop.run_until_complete(base.get_stream_result(
            send_transaction(self.client.orderers, tran_req, tx_context_tx)))

        logger.debug('Tx response: {}'.format(responses))
        return responses

    def cc_query(self, args, cc_name, fcn):
        """
        Invoke a chaincode query method. If there is no query method from the
        chaincode, then this will fail.

        Parameters:
        args     Array of the strings used as the parameters to query method
        cc_name  Chaincode name
        fcn      Chaincode function name
        """
        loop = asyncio.get_event_loop()
        try:
            responses = loop.run_until_complete(self.client.chaincode_query(
                requestor=self.user, channel_name=self.channel_name,
                peers=[self.peer_name], args=args, cc_name=cc_name, fcn=fcn))
            logger.debug('Tx response: {0}'.format(responses))
            return json.loads(responses)
        except Exception as ex:
            # In case of invalid input catch exception
            # return empty dict.
            logger.debug('Query response: {0}'.format(ex))
            return {}
