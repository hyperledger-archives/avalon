/*
Copyright IBM Corp. 2020 All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

		 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package main

//Off Chain Trusted Compute Service Work Registry Chaincode
import (
	"encoding/json"
	"errors"

	"github.com/hyperledger/fabric/core/chaincode/lib/cid"
	"github.com/hyperledger/fabric/core/chaincode/shim"
	pb "github.com/hyperledger/fabric/protos/peer"
)

var logger = shim.NewLogger("WorkerOrder")

// getWorkOrderID - This function retrieves the work order with its ID
// params:
//   byte32 workOrderID
func (t *WorkOrder) getOrderByID(stub shim.ChaincodeStubInterface, workOrderID string) (*WorkOrder, error) {
	var param WorkOrder
	Avalbytes, err := stub.GetState(workOrderID)
	if err != nil {
		return nil, err
	}

	if Avalbytes == nil {
		return nil, errors.New("WorkOrder with ID '" + workOrderID + "' does not exist")
	}

	err = json.Unmarshal(Avalbytes, &param)
	if err != nil {
		logger.Errorf("Error trying to decode the work order: %s", err)
		return nil, err
	}

	return &param, nil
}

// getMSPID - This function retrieve the MSPID of the calling agent
func (t *WorkOrder) getMSPID(stub shim.ChaincodeStubInterface) string {
	var mspid string
	id, err := cid.New(stub)
	if err != nil {
		logger.Errorf("Can not get peer id")
		return ""
	}

	mspid, err = id.GetMSPID()
	if err != nil {
		logger.Errorf("Can not get msp id")
		return ""
	}

	logger.Info("The mspid retrieved is: " + mspid)

	cert, err := cid.GetX509Certificate(stub)
	if err != nil {
		logger.Errorf("Can not get certificate")
		return ""
	}

	logger.Infof("The common name is %s", cert.Subject.CommonName)

	return mspid
}

// getCallerID - This function returns the caller identity
func (t *WorkOrder) getCallerID(stub shim.ChaincodeStubInterface) string {
	cert, err := cid.GetX509Certificate(stub)
	if err != nil {
		logger.Errorf("Can not get certificate")
		return ""
	}

	logger.Infof("The common name is %s", cert.Subject.CommonName)

	return cert.Subject.CommonName
}

// Init the init function of the chaincode
func (t *WorkOrder) Init(stub shim.ChaincodeStubInterface) pb.Response {
	logger.Info("WorkOrder Init")
	return shim.Success(nil)
}

// workOrderSubmit - This function submits a work order
// params:
//   bytes32 workOrderId
//   bytes32 workerId
//   bytes32 requestId
//   string workOrderRequest
// returns:
func (t *WorkOrder) workOrderSubmit(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workOrderSubmit")
	if len(args) != 4 {
		logger.Errorf("Too many parameters, expect 4, received %d", len(args))
		return shim.Error("workOrderSubmit must include 4 arguments, workOrderID, workerId, requestId and workOrderRequest")
	}

	var param WorkOrder
	param.WorkOrderId = args[0]
	param.WorkerId = args[1]
	param.RequesterId = args[2]
	param.WorkOrderRequest = args[3]
	param.WorkOrderStatus = ORDERSUBMITTED
	param.WorkOrderResponse = ""

	//Serialize the value
	value, err := json.Marshal(param)
	if err != nil {
		return shim.Error(err.Error())
	}

	logger.Infof("The work order ID: %s", param.WorkOrderId)
	err = stub.PutState(param.WorkOrderId, value)
	if err != nil {
		return shim.Error(err.Error())
	}

	// Handling payload for the event
	var eventData WorkOrderSubmittedEvent
	eventData.WorkOrderId = param.WorkOrderId
	eventData.WorkerId = param.WorkerId
	eventData.RequesterId = param.RequesterId
	eventData.WorkOrderRequest = param.WorkOrderRequest
	eventData.ErrorCode = 0
	eventData.SenderAddress = t.getCallerID(stub)
	eventData.Version = APIVERSION

	eventPayload, err := json.Marshal(eventData)
	if err != nil {
		return shim.Error(err.Error())
	}

	err = stub.SetEvent("workOrderSubmitted", eventPayload)
	if err != nil {
		return shim.Error(err.Error())
	}

	logger.Info("Finished workOrderSubmit")
	return shim.Success(nil)
}

// workOrderComplete - This function submit a work order
// params:
//   bytes32 workOrderId
//   string workOrderResponse
// returns:
func (t *WorkOrder) workOrderComplete(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workOrderComplete")
	if len(args) != 2 {
		logger.Errorf("Too many parameters, expect 2, received %d", len(args))
		return shim.Error("workOrderSubmit must include 2 arguments, workOrderID and workOrderResponse")
	}

	wo, err := t.getOrderByID(stub, args[0])
	if err != nil {
		logger.Errorf("Could not find the work order by the id %s", args[0])
		return shim.Error(err.Error())
	}
	logger.Infof("The work order ID: %s", wo.WorkOrderId)

	wo.WorkOrderStatus = ORDERCOMPLETED
	wo.WorkOrderResponse = args[1]

	//Serialize the value
	value, err := json.Marshal(wo)
	if err != nil {
		return shim.Error(err.Error())
	}

	err = stub.PutState(wo.WorkOrderId, value)
	if err != nil {
		return shim.Error(err.Error())
	}

	// Handling payload for the event
	var eventData WorkOrderCompletedEvent
	eventData.RequesterId = wo.RequesterId
	eventData.WorkOrderId = wo.WorkOrderId
	eventData.WorkOrderStatus = wo.WorkOrderStatus
	eventData.WorkOrderResponse = wo.WorkOrderResponse
	eventData.ErrorCode = 0
	eventData.Version = APIVERSION

	eventPayload, err := json.Marshal(eventData)
	if err != nil {
		return shim.Error(err.Error())
	}

	err = stub.SetEvent("workOrderCompleted", eventPayload)
	if err != nil {
		return shim.Error(err.Error())
	}

	logger.Info("Finished workOrderComplete")
	return shim.Success(nil)
}

// workOrderGet - This function retrieve a work order
// params:
//   bytes32 workOrderId
// returns:
//   uint256 workOrderStatus,
//   bytes32 workerId,
//   string workOrderRequest,
//   string workOrderResponse,
//   uint256 errorCode
func (t *WorkOrder) workOrderGet(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workOrderComplete")
	if len(args) != 1 {
		logger.Errorf("Too many parameters, expect 1, received %d", len(args))
		return shim.Error("workOrderSubmit must include 1 argument, workOrderID")
	}

	wo, err := t.getOrderByID(stub, args[0])
	if err != nil {
		logger.Errorf("Could not find the work order by the id %s", args[0])
		return shim.Error(err.Error())
	}
	logger.Infof("The work order ID: %s", wo.WorkOrderId)

	// Handling payload for the event
	var payloadData WorkOrderGetRes
	payloadData.WorkOrderStatus = wo.WorkOrderStatus
	payloadData.WorkerId = wo.WorkerId
	payloadData.WorkOrderRequest = wo.WorkOrderRequest
	payloadData.WorkOrderResponse = wo.WorkOrderResponse
	payloadData.ErrorCode = 0

	value, err := json.Marshal(payloadData)
	if err != nil {
		return shim.Error(err.Error())
	}

	logger.Info("Finished workOrderGet")
	return shim.Success(value)
}

// Invoke - this function simply satisfy the main requirement of chaincode
func (t *WorkOrder) Invoke(stub shim.ChaincodeStubInterface) pb.Response {
	logger.Info("Invoke")
	function, args := stub.GetFunctionAndParameters()
	if function == "workOrderSubmit" {
		return t.workOrderSubmit(stub, args)
	} else if function == "workOrderComplete" {
		return t.workOrderComplete(stub, args)
	} else if function == "workOrderGet" {
		return t.workOrderGet(stub, args)
	}

	return shim.Error("Invalid invoke function name")
}

func main() {
	err := shim.Start(new(WorkOrder))
	if err != nil {
		logger.Errorf("Error starting WorkOrder chaincode: %s", err)
	}
}
