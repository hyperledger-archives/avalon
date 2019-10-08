/* Copyright 2019 iExec Blockchain Tech
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

contract WorkOrderRegistry
{
	bytes4 constant VERSION = 0x01010000; // 1.1.0.0

	enum WorkOrderStatus
	{
		NULL,
		ACTIVE,
		COMPLETED,
		FAILED
	}

	struct WorkOrder
	{
		uint256 status;
		uint256 timestamp;
		bytes32 workerID;
		bytes32 requesterID;
		string  request;
		string  response;
	}

	// workOrderID → workOrder
	mapping(bytes32 => WorkOrder) m_workorders;

	event workOrderSubmitted(
		bytes32 indexed workOrderId,
		bytes32 indexed workerId,
		bytes32 indexed requesterId,
		string          workOrderRequest,
		uint256         errorCode,
		address         senderAddress,
		bytes4          version);

	event workOrderCompleted(
		bytes32 requesterId,
		bytes32 workOrderId,
		uint256 workOrderStatus,
		string workOrderResponse,
		uint256 errorCode,
		bytes4 version);

	constructor()
	public
	{}

	function workOrderSubmit(
		bytes32       _workOrderID,
		bytes32       _workerID,
		bytes32       _requesterID,
		string memory _workOrderRequest)
	public returns (
		uint256      errorCode
	) {
		WorkOrder storage wo = m_workorders[_workOrderID];

		errorCode = (wo.status == uint256(WorkOrderStatus.NULL)) ? 0 : 1;

		if (errorCode == 0)
		{
			wo.status      = uint256(WorkOrderStatus.ACTIVE);
			wo.timestamp   = now;
			wo.workerID    = _workerID;
			wo.requesterID = _requesterID;
			wo.request     = _workOrderRequest;
		}

		emit workOrderSubmitted(
			_workOrderID,
			_workerID,
			_requesterID,
			_workOrderRequest,
			errorCode,
			msg.sender,
			VERSION);

		return errorCode;
	}

	function workOrderComplete(
		bytes32       _workOrderID,
		string memory _workOrderResponse
	) public returns (
		uint256       errorCode
	) {
		WorkOrder storage wo = m_workorders[_workOrderID];

		errorCode = (wo.status == uint256(WorkOrderStatus.ACTIVE)) ? 0 : 1;

		if (errorCode == 0)
		{
			wo.status   = uint256(WorkOrderStatus.COMPLETED);
			wo.response = _workOrderResponse;
		}

		emit workOrderCompleted(
			wo.requesterID,
			_workOrderID,
			wo.status,
			wo.response,
			errorCode,
			VERSION);

		return errorCode;
	}

	function workOrderGet(
		bytes32      _workOrderID
	) public view returns (
		uint256       status,
		bytes32       workerID,
		string memory request,
		string memory response,
		uint256       errorCode
	) {
		WorkOrder storage wo = m_workorders[_workOrderID];
		return (
			wo.status,
			wo.workerID,
			wo.request,
			wo.response,
			0);
	}

}
