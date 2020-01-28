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

import (
	"encoding/json"
	"errors"
	"fmt"
	"strconv"

	"github.com/hyperledger/fabric/core/chaincode/shim"
	pb "github.com/hyperledger/fabric/protos/peer"
)

var logger = shim.NewLogger("Receipt")

// getReceiptByID - This function retrieve the receipt with its ID
// params:
//   byte32 receiptId
func (t *Receipt) getReceiptByID(stub shim.ChaincodeStubInterface, receiptId string) (*Receipt, error) {
	var param Receipt
	Avalbytes, err := stub.GetState(receiptId)
	if err != nil {
		return nil, err
	}

	if Avalbytes == nil {
		return nil, errors.New("Receipt with ID '" + receiptId + "' does not exist")
	}

	err = json.Unmarshal(Avalbytes, &param)
	if err != nil {
		logger.Errorf("Error trying to decode the worker: %s", err)
		return nil, err
	}

	return &param, nil
}

// Init the init function of the chaincode
func (t *Receipt) Init(stub shim.ChaincodeStubInterface) pb.Response {
	logger.Info("Receipt Init")
	return shim.Success(nil)
}

// registryAdd - This function add a new organization
// params:
//   byte32 orgID
//   stromg uri
//   bytes32 scAddr
//   bytes32[] appTypeIds
// returns:
func (t *Receipt) workOrderReceiptCreate(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workOrderReceiptCreate")
	if len(args) != 6 {
		logger.Errorf("Mismatch number of arguments, expect 6, received %d", len(args))
		return shim.Error("workOrderReceiptCreate must include 6 arguments, workOrderId, workerId, workerServiceId, requesterId, receiptCreateStatus and workOrderRequestHash")
	}

	arg4, err := strconv.ParseUint(args[4], 10, 64)
	if err != nil {
		logger.Errorf("Receipt create status must be an integer")
		return shim.Error("Receipt create status must be an integer")
	}

	var r Receipt
	r.WorkOrderId = args[0]
	r.WorkerId = args[1]
	r.WorkerServiceId = args[2]
	r.RequesterId = args[3]
	r.ReceiptCreateStatus = arg4
	r.WorkOrderRequestHash = args[5]

	//Serialize the value
	value, err := json.Marshal(r)
	if err != nil {
		return shim.Error(err.Error())
	}

	err = stub.PutState(r.WorkOrderId, value)
	if err != nil {
		return shim.Error(err.Error())
	}

	compValue := []byte(r.WorkOrderId)

	attrs, _ := processAttributes([]string{r.WorkerServiceId, r.WorkerId, r.RequesterId, args[4]},
		[]string{BYTE32FORMAT, BYTE32FORMAT, BYTE32FORMAT, UINT64FORMAT})
	compKey, err := stub.CreateCompositeKey(OBJECTTYPE, attrs)
	if err != nil {
		return shim.Error(err.Error())
	}
	err = stub.PutState(compKey, compValue)
	if err != nil {
		return shim.Error(err.Error())
	}

	// Handling payload for the event
	var eventData ReceiptCreatedEvent
	eventData.WorkOrderId = r.WorkOrderId
	eventData.WorkerServiceId = r.WorkerServiceId
	eventData.WorkerId = r.WorkerId
	eventData.RequesterId = r.RequesterId
	eventData.ReceiptStatus = r.ReceiptCreateStatus
	eventData.WorkOrderRequestHash = r.WorkOrderRequestHash
	eventData.ErrorCode = 0

	eventPayload, err := json.Marshal(eventData)
	if err != nil {
		return shim.Error(err.Error())
	}

	err = stub.SetEvent("workOrderReceiptCreated", eventPayload)
	if err != nil {
		return shim.Error(err.Error())
	}

	logger.Info("Finished workOrderReceiptCreate")
	return shim.Success(nil)
}

// workOrderReceiptUpdate - This function updates a Receipt
// params:
//   bytes32 workOrderId,
//   bytes32 updaterId. should this be workerId?
//   uint256 updateType,
//   bytes updateData,
//   bytes updateSignature,
//   string signatureRules
func (t *Receipt) workOrderReceiptUpdate(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workOrderReceiptUpdate")

	return shim.Error("Not Implemented")
}

// workOrderReceiptLookUp - This function retrieves a list of registry ids that match input
// parameter. The registry must match to all input parameters (AND mode) to be
// included in the list.
// params:
//    bytes32 workerServiceId,
//    bytes32 workerId,
//    bytes32 requesterId,
//    uint256 receiptStatus
// returns:
//   int totalCount
//   string LookupTag
//   bytes32[] ids
func (t *Receipt) workOrderReceiptLookUp(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workOrderReceiptLookUp")

	if len(args) != 4 {
		logger.Errorf("Expected 4 arguments, received %d", len(args))
		return shim.Error("workOrderReceiptLookUp must include 4 arguments, workerServiceId, workerId, requesterId, receiptStatus")
	}

	args = append(args, "")
	return t.workOrderReceiptLookUpNext(stub, args)
}

// workOrderReceiptLookUpNext - This function is called to retrieve additional results of the
// registry lookup initiated by registryLookUp call.
// params:
//   bytes32 appTypeId
//   string lookUpTag
// returns:
//   int totalCount
//   string newLookupTag
//   bytes32[] ids
func (t *Receipt) workOrderReceiptLookUpNext(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workOrderReceiptLookUpNext")

	if len(args) != 5 {
		logger.Errorf("Expected 5 arguments, received %d", len(args))
		return shim.Error("workOrderReceiptLookUpNext must include 5 arguments, workerServiceId, workerId, requesterId, receiptStatus, lookUpTag")
	}

	attrs, err := processAttributes(args[0:4], []string{BYTE32FORMAT, BYTE32FORMAT, BYTE32FORMAT, UINT64FORMAT})
	if err != nil {
		logger.Errorf("Cannot format the query parameters")
		return shim.Error(err.Error())
	}

	logger.Infof("The lookup key: %v", attrs)

	iter, metadata, err := stub.GetStateByPartialCompositeKeyWithPagination(OBJECTTYPE, attrs,
		int32(PAGESIZE+1), args[4])
	if err != nil {
		logger.Errorf("Error trying to query with partial composite key: %s", err)
		return shim.Error(err.Error())
	}

	var resparam ReceiptLookUpRes
	for iter.HasNext() {
		item, _ := iter.Next()
		logger.Infof("The value: %v", item)
		resparam.IDs = append(resparam.IDs, string(item.Value))
		if len(resparam.IDs) == PAGESIZE {
			break
		}
	}
	logger.Info("Result metadata: %v", metadata)
	resparam.LookupTag = metadata.GetBookmark()
	resparam.TotalCount = uint64(metadata.GetFetchedRecordsCount())

	//Serialize the response
	value, err := json.Marshal(resparam)
	if err != nil {
		return shim.Error(err.Error())
	}

	return shim.Success(value)
}

// workOrderReceiptRetrieve - This function retrieves information for the Worker and it can be
// called from any authorized publickey (Ethereum address) or DID
// params:
//   byte32 orgId
// returns:
//   string uri
//   bytes32 scAddr
//   bytes32[] appTypeIds
//   uint6=256 status
func (t *Receipt) workOrderReceiptRetrieve(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workOrderReceiptRetrieve")
	if len(args) != 1 {
		logger.Errorf("Expected parameter is 1, received %d", len(args))
		return shim.Error("registryRetrieve must include 1 argument, orgId")
	}

	logger.Infof("registry retrieve orgId: %s", args[0])

	r, err := t.getReceiptByID(stub, args[0])
	if err != nil {
		return shim.Error(err.Error())
	}

	var resparam ReceiptRetrieveRes
	resparam.WorkerServiceId = r.WorkerServiceId
	resparam.WorkerId = r.WorkerId
	resparam.RequesterId = r.RequesterId
	resparam.ReceiptCreateStatus = r.ReceiptCreateStatus
	resparam.WorkOrderRequestHash = r.WorkOrderRequestHash
	resparam.CurrentReceiptStatus = r.ReceiptCreateStatus

	//Serialize the response
	value, err := json.Marshal(resparam)
	if err != nil {
		return shim.Error(err.Error())
	}

	return shim.Success(value)
}

// query - This function retrieves information by org id
// params:
//   byte32 receiptId
// returns:
func (t *Receipt) query(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("work order receipt query")

	// Get the state from the ledger
	logger.Infof("query by receipt id: %s", args[0])
	Avalbytes, err := stub.GetState(args[0])
	if err != nil {
		return shim.Error(err.Error())
	}

	if Avalbytes == nil {
		return shim.Error("work order receipt with ID '" + args[0] + "' does not exist")
	}

	return shim.Success(Avalbytes)
}

// Invoke - this function simply satisfy the main requirement of chaincode
func (t *Receipt) Invoke(stub shim.ChaincodeStubInterface) pb.Response {
	logger.Info("Invoke")
	function, args := stub.GetFunctionAndParameters()
	if function == "workOrderReceiptCreate" {
		return t.workOrderReceiptCreate(stub, args)
	} else if function == "workOrderReceiptUpdate" {
		return t.workOrderReceiptUpdate(stub, args)
	} else if function == "workOrderReceiptRetrieve" {
		return t.workOrderReceiptRetrieve(stub, args)
	} else if function == "workOrderReceiptLookUp" {
		return t.workOrderReceiptLookUp(stub, args)
	} else if function == "workOrderReceiptLookUpNext" {
		return t.workOrderReceiptLookUpNext(stub, args)
	} else if function == "query" {
		return t.query(stub, args)
	}

	return shim.Error("Invalid invoke function name")
}

// processAttributes - This function formalize the input attributes. It
// will transform the variable length of a parameter value into a fixed
// length string value
// params:
//   []string arg1, the value of attributes
//   []string arg2, the type of the values to be formatted to. For example, if
//            this value is UINT64FORMAT, then the value will be left padded 0.
//            if this value is BYTE32FORMAT, then the value will be right padded
//            spaces
// returns:
//   []string the fixed length
func processAttributes(arg1 []string, arg2 []string) ([]string, error) {
	var attrs []string
	for i, argType := range arg2 {
		switch argType {
		case UINT64FORMAT:
			arg, err := strconv.ParseUint(arg1[i], 10, 64)
			if err != nil {
				return nil, err
			}
			attrs = append(attrs, fmt.Sprintf(UINT64FORMAT, arg))
		case BYTE32FORMAT:
			attrs = append(attrs, fmt.Sprintf(BYTE32FORMAT, arg1[i]))
		}
	}
	return attrs, nil
}

func main() {
	err := shim.Start(new(Receipt))
	if err != nil {
		logger.Errorf("Error starting Receipt chaincode: %s", err)
	}
}
