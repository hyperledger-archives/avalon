/* Copyright 2020 iExec Blockchain Tech
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

pragma solidity ^0.5.0;

import './LibSet.bytes32.sol';

contract WorkOrderReceiptRegistry
{
	using LibSet_bytes32 for LibSet_bytes32.set;

	// Structures
	struct WorkOrderReceipt
	{
		bool    active;
		bytes32 workerServiceId;
		bytes32 workerId;
		bytes32 requesterId;
		uint256 receiptCreateStatus;
		bytes   workOrderRequestHash;
		uint256 currentReceiptStatus;
		mapping(bytes32 => uint256[]) updates;
	}

	struct WorkOrderReceiptUpdate
	{
		bytes32 updaterId;
		uint256 updateType;
		bytes   updateData;
		bytes   updateSignature;
		string  signatureRules;
	}

	// Constants
	uint256 constant internal LASTUPDATE = 0xFFFFFFFF;

	// Members
	mapping(bytes32 => WorkOrderReceipt)                                                               internal m_workorders;
	WorkOrderReceiptUpdate[]                                                                           internal m_workorderupdates;
	// workerServiceId => workerId => requesterId => receiptCreateStatus => Set<workOrderId>
	mapping(bytes32 => mapping(bytes32 => mapping(bytes32 => mapping(uint256 => LibSet_bytes32.set)))) internal m_lookuptable;

	// Events
	event workOrderReceiptCreated(
		bytes32 indexed workOrderId,
		bytes32 indexed workerServiceId,
		bytes32 indexed requesterId,   // CHANGE (order): cannot have indexed after non indexed
		bytes32         workerId,      // CHANGE (order): cannot have indexed after non indexed
		uint256         receiptStatus, // CHANGE (consistency): status/update types are uint256, not bytes32
		bytes           workOrderRequestHash,
		uint256         errorCode);

	event workOrderReceiptUpdated(
		bytes32 indexed workOrderId,
		bytes32 indexed updaterId,
		uint256 indexed updateType, // CHANGE (consistency): status/update types are uint256, not bytes32
		bytes           updateData,
		bytes           updateSignature,
		string          signatureRules,
		uint256         errorCode);

	// Methods
	function workOrderReceiptCreate(
		bytes32       workOrderId,
		bytes32       workerId,
		bytes32       workerServiceId,
		bytes32       requesterId,
		uint256       receiptCreateStatus,
		bytes  memory workOrderRequestHash)
	public returns (uint256 errorCode)
	{
		WorkOrderReceipt storage receipt = m_workorders[workOrderId];

		if (!receipt.active)
		{
			receipt.active               = true;
			receipt.workerServiceId      = workerServiceId;
			receipt.workerId             = workerId;
			receipt.requesterId          = requesterId;
			receipt.receiptCreateStatus  = receiptCreateStatus;
			receipt.workOrderRequestHash = workOrderRequestHash;
			receipt.currentReceiptStatus = receiptCreateStatus;

			m_lookuptable[workerServiceId][workerId][requesterId][receiptCreateStatus].add(workOrderId);
			m_lookuptable[workerServiceId][workerId][requesterId][255].add(workOrderId); // ANY ?

			errorCode = 0;
		}
		else
		{
			errorCode = 1;
		}

		emit workOrderReceiptCreated(
			workOrderId,
			workerServiceId,
			requesterId, // CHANGE (order): cannot have indexed after non indexed
			workerId,    // CHANGE (order): cannot have indexed after non indexed
			receiptCreateStatus,
			workOrderRequestHash,
			errorCode);
	}


	function workOrderReceiptUpdate(
		bytes32       workOrderId,
		bytes32       updaterId,
		uint256       updateType,
		bytes  memory updateData,
		bytes  memory updateSignature,
		string memory signatureRules)
	public returns (uint256 errorCode)
	{
		WorkOrderReceipt storage receipt = m_workorders[workOrderId];

		// Updating receipt
		if (receipt.currentReceiptStatus < 255)
		{
			m_lookuptable[receipt.workerServiceId][receipt.workerId][receipt.requesterId][receipt.currentReceiptStatus].remove(workOrderId);
			receipt.currentReceiptStatus = updateType;
			m_lookuptable[receipt.workerServiceId][receipt.workerId][receipt.requesterId][receipt.currentReceiptStatus].add(workOrderId);
		}

		// Storing update
		m_workorderupdates.push(WorkOrderReceiptUpdate({
			updaterId:       updaterId,
			updateType:      updateType,
			updateData:      updateData,
			updateSignature: updateSignature,
			signatureRules:  signatureRules
		}));
		receipt.updates[updaterId].push(m_workorderupdates.length-1);

		errorCode = 0;

		emit workOrderReceiptUpdated(
			workOrderId,
			updaterId,
			updateType,
			updateData,
			updateSignature,
			signatureRules,
			errorCode);
	}

	function workOrderReceiptUpdateRetrieve(
		bytes32 workOrderId,
		bytes32 _updaterId, // CHANGE (solidity): input and output CANNOT have the same name
		uint256 updateIndex)
	public view returns(
		bytes32       updaterId,
		uint256       updateType,
		bytes  memory updateData,
		bytes  memory updateSignature,
		string memory signatureRules,
		uint256       updateCount)
	{
		WorkOrderReceipt       storage receipt   = m_workorders[workOrderId];
		uint256[]              storage updateIds = receipt.updates[_updaterId];
		uint256                        updateId  = updateIds[updateIndex == LASTUPDATE ? updateIds.length-1 : updateIndex];
		WorkOrderReceiptUpdate storage update    = m_workorderupdates[updateId];

		updaterId       = update.updaterId;
		updateType      = update.updateType;
		updateData      = update.updateData;
		updateSignature = update.updateSignature;
		signatureRules  = update.signatureRules;
		updateCount     = updateIds.length;
	}

	function workOrderReceiptRetrieve(bytes32 workOrderId)
	public view returns (
		bytes32       workerServiceId,
		bytes32       workerId,
		bytes32       requesterId,
		uint256       receiptCreateStatus,
		bytes  memory workOrderRequestHash,
		uint256       currentReceiptStatus)
	{
		WorkOrderReceipt storage receipt = m_workorders[workOrderId];
		workerServiceId      = receipt.workerServiceId;
		workerId             = receipt.workerId;
		requesterId          = receipt.requesterId;
		receiptCreateStatus  = receipt.receiptCreateStatus;
		workOrderRequestHash = receipt.workOrderRequestHash;
		currentReceiptStatus = receipt.currentReceiptStatus;
	}


	function workOrderReceiptLookUp(
		bytes32 workerServiceId,
		bytes32 workerId,
		bytes32 requesterId,
		uint256 receiptStatus)
	public view returns (uint256 totalCount, uint256 lookUpTag, bytes32[] memory ids)
	{
		ids        = m_lookuptable[workerServiceId][workerId][requesterId][receiptStatus].content();
		totalCount = ids.length;
		lookUpTag  = 0;
	}

	function workOrderReceiptLookUpNext(
		bytes32 workerServiceId,
		bytes32 workerId,
		bytes32 requesterId,
		uint256 receiptStatus,
		uint256 lastLookUpTag)
	public view returns(uint256 totalCount, uint256 lookUpTag, bytes32[] memory ids)
	{
		ids        = m_lookuptable[workerServiceId][workerId][requesterId][receiptStatus].content();
		totalCount = ids.length;
		lookUpTag  = 0;

		// silent unused warnings
		lastLookUpTag;
	}
}
