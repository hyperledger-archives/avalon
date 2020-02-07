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
	"fmt"
	"strconv"
	"strings"

	"github.com/hyperledger/fabric/core/chaincode/shim"
	pb "github.com/hyperledger/fabric/protos/peer"
)

var logger = shim.NewLogger("WorkerRegistry")

// getWorkerByID - This function retrieve the worker register with its ID
// params:
//   byte32 workerID
func (t *WorkerRegistry) getWorkerByID(stub shim.ChaincodeStubInterface, workerID string) (*WorkerRegistry, error) {
	var param WorkerRegistry
	Avalbytes, err := stub.GetState(workerID)
	if err != nil {
		return nil, err
	}

	if Avalbytes == nil {
		return nil, errors.New("Worker with ID '" + workerID + "' does not exist")
	}

	err = json.Unmarshal(Avalbytes, &param)
	if err != nil {
		logger.Errorf("Error trying to decode the worker: %s", err)
		return nil, err
	}

	return &param, nil
}

// Init the init function of the chaincode
func (t *WorkerRegistry) Init(stub shim.ChaincodeStubInterface) pb.Response {
	logger.Info("WorkerRegistry Init")
	return shim.Success(nil)
}

// workerRegister - This function registers a Worker
// params:
//   byte32 workerID
//   uint256 workerType
//   bytes32 organizationID
//   bytes32[] applicationTypeId
//   string details
// returns:
func (t *WorkerRegistry) workerRegister(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workerRegister")
	if len(args) != 5 {
		logger.Errorf("Too many parameters, expect 5, received %d", len(args))
		return shim.Error("workerRegister must include 5 arguments, workerID, workerType, organizationID, applicationTypeId, and details")
	}

	var param WorkerRegistry
	param.WorkerID = args[0]
	arg1, err := strconv.ParseUint(args[1], 10, 64)
	if err != nil {
		logger.Errorf("Worker Type must be an integer")
		return shim.Error("Worker Type must be an integer")
	}
	param.WorkerType = arg1
	param.OrganizationID = args[2]
	param.ApplicationTypeId = strings.Split(args[3], ",")
	param.Details = args[4]
	param.Status = WORKERACTIVE

	//Serialize the value
	value, err := json.Marshal(param)
	if err != nil {
		return shim.Error(err.Error())
	}

	logger.Infof("The worker ID: %s", param.WorkerID)
	err = stub.PutState(param.WorkerID, value)
	if err != nil {
		return shim.Error(err.Error())
	}

	// Need to add compositeKey so that the search would work
	// The composite key is made of OBJECTTYPE, workerType, organizationID and appTypeID
	compValue := []byte(param.WorkerID)
	for _, appTypeID := range param.ApplicationTypeId {
		key1 := fmt.Sprintf(UINT64FORMAT, param.WorkerType)
		key2 := fmt.Sprintf(BYTE32FORMAT, param.OrganizationID)
		key3 := fmt.Sprintf(BYTE32FORMAT, appTypeID)
		key4 := fmt.Sprintf(BYTE32FORMAT, param.WorkerID)
		compKey, err := stub.CreateCompositeKey(OBJECTTYPE,
			[]string{key1, key2, key3, key4})
		if err != nil {
			return shim.Error(err.Error())
		}
		logger.Infof("The composite key: %s, length: %d", compKey, len(compKey))
		err = stub.PutState(compKey, compValue)
		if err != nil {
			return shim.Error(err.Error())
		}
	}

	// Handling payload for the event
	eventData := map[string]interface{}{"workerID": param.WorkerID}
	eventPayload, err := json.Marshal(eventData)
	if err != nil {
		return shim.Error(err.Error())
	}

	err = stub.SetEvent("workerRegistered", eventPayload)
	if err != nil {
		return shim.Error(err.Error())
	}

	logger.Info("Finished workerRegister")
	return shim.Success(nil)
}

// workerUpdate - This function set the detail of a Worker
// params:
//   byte32 workerID
//   string detail
// returns:
func (t *WorkerRegistry) workerUpdate(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workerSetStatus")
	logger.Infof("query workerID: %s", args[0])

	if len(args) != 2 {
		logger.Errorf("Expected parameters are 2, received %d", len(args))
		return shim.Error("workerUpdate must include 2 arguments, workerID and details")
	}

	wr, err := t.getWorkerByID(stub, args[0])
	if err != nil {
		return shim.Error(err.Error())
	}

	wr.Details = args[1]
	//Serialize the value
	value, err := json.Marshal(wr)
	if err != nil {
		return shim.Error(err.Error())
	}

	err = stub.PutState(wr.WorkerID, value)
	if err != nil {
		return shim.Error(err.Error())
	}

	return shim.Success(value)
}

// WorkerSetStatus - This function set the status of a Worker
// params:
//   byte32 workerID
//   uint256 status
// returns:
func (t *WorkerRegistry) workerSetStatus(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workerSetStatus")
	logger.Infof("query workerID: %s", args[0])

	if len(args) != 2 {
		logger.Errorf("Expected parameters are 2, received %d", len(args))
		return shim.Error("workerSetStatus must include 2 arguments, workID and status")
	}

	arg1, err := strconv.ParseUint(args[1], 10, 64)
	if err != nil {
		logger.Errorf("Worker status must be integer, received %v", args[1])
		return shim.Error(err.Error())
	}

	wr, err := t.getWorkerByID(stub, args[0])
	if err != nil {
		return shim.Error(err.Error())
	}

	wr.Status = arg1
	//Serialize the value
	value, err := json.Marshal(wr)
	if err != nil {
		return shim.Error(err.Error())
	}

	err = stub.PutState(wr.WorkerID, value)
	if err != nil {
		return shim.Error(err.Error())
	}

	return shim.Success(value)
}

// WorkerLookUp - This function retrieves a list of Worker ids that match input
// parameter. The Worker must match to all input parameters (AND mode) to be
// included in the list.
// params:
//   uint8 workerType
//   bytes32 organizationId
//   bytes32 applicationTypeId
// returns:
//   int totalCount
//   string LookupTag
//   bytes32[] ids
func (t *WorkerRegistry) workerLookUp(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workerLookUp")

	if len(args) != 3 {
		logger.Errorf("Expected parameters are 3, received %d", len(args))
		return shim.Error("workerLookUp must include 3 arguments, workType, organizationID and applicationTypeId")
	}

	args = append(args, "")
	return t.workerLookUpNext(stub, args)
}

// WorkerLookUpNext - This function is called to retrieve additional results of the
// Worker lookup initiated byworkerLookUp call.
// params:
//   uint8 workerType
//   bytes32 organizationId
//   bytes32 applicationTypeId
//   string lookUpTag
// returns:
//   int totalCount
//   string newLookupTag
//   bytes32[] ids
func (t *WorkerRegistry) workerLookUpNext(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workerLookUpNext")

	if len(args) != 4 {
		logger.Errorf("Expected parameters are 4, received %d", len(args))
		return shim.Error("workerLookUpNext must include 4 arguments, workerType, organizationID, applicationTypeId and lookupTag")
	}

	attrs, err := processAttributes(args[0:3], []string{UINT64FORMAT, BYTE32FORMAT, BYTE32FORMAT})
	if err != nil {
		return shim.Error(err.Error())
	}
	logger.Infof("The lookup key: %v", attrs)

	iter, metadata, err := stub.GetStateByPartialCompositeKeyWithPagination(OBJECTTYPE, attrs,
		int32(PAGESIZE+1), args[3])
	if err != nil {
		logger.Errorf("Error trying to query with partial composite key: %s", err)
		return shim.Error(err.Error())
	}

	var resparam WorkerLookUpResParam
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

// WorkerRetrieve - This function retrieves information for the Worker and it can be
// called from any authorized publickey (Ethereum address) or DID
// params:
//   byte32 workerId
// returns:
//   uint256 status
//   uint8 workerType
//   bytes32 organizationId
//   bytes32[] applicationTypeId
//   string details
func (t *WorkerRegistry) workerRetrieve(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("workerRetrieve")
	if len(args) != 1 {
		logger.Errorf("Expected parameter is 1, received %d", len(args))
		return shim.Error("workerRetrieve must include 1 argument, workerID")
	}

	logger.Infof("worker retrieve workerID: %s", args[0])

	wr, err := t.getWorkerByID(stub, args[0])
	if err != nil {
		return shim.Error(err.Error())
	}

	var resparam WorkerRetrieveResParam
	resparam.Status = wr.Status
	resparam.WorkerType = wr.WorkerType
	resparam.OrganizationID = wr.OrganizationID
	resparam.ApplicationTypeId = wr.ApplicationTypeId
	resparam.Details = wr.Details

	//Serialize the response
	value, err := json.Marshal(resparam)
	if err != nil {
		return shim.Error(err.Error())
	}

	return shim.Success(value)
}

// query - This function retrieves information by worker id
// params:
//   byte32 workerId
// returns:
//   uint8 workerType
//   string workerTypeDataUri
//   bytes32 organizationId
//   bytes32[] applicationTypeId
func (t *WorkerRegistry) query(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("query")

	// Get the state from the ledger
	logger.Infof("query workerID: %s", args[0])
	Avalbytes, err := stub.GetState(args[0])
	if err != nil {
		return shim.Error(err.Error())
	}

	if Avalbytes == nil {
		return shim.Error("WorkerID '" + args[0] + "' does not exist")
	}

	return shim.Success(Avalbytes)
}

// Invoke - this function simply satisfy the main requirement of chaincode
func (t *WorkerRegistry) Invoke(stub shim.ChaincodeStubInterface) pb.Response {
	logger.Info("Invoke")
	function, args := stub.GetFunctionAndParameters()
	if function == "workerRegister" {
		return t.workerRegister(stub, args)
	} else if function == "workerUpdate" {
		return t.workerUpdate(stub, args)
	} else if function == "workerSetStatus" {
		return t.workerSetStatus(stub, args)
	} else if function == "workerLookUp" {
		return t.workerLookUp(stub, args)
	} else if function == "workerLookUpNext" {
		return t.workerLookUpNext(stub, args)
	} else if function == "workerRetrieve" {
		return t.workerRetrieve(stub, args)
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
	err := shim.Start(new(WorkerRegistry))
	if err != nil {
		logger.Errorf("Error starting WorkerRegistry chaincode: %s", err)
	}
}
