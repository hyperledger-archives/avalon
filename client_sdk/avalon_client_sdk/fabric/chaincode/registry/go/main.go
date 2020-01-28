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

var logger = shim.NewLogger("Registry")

// getWorkerByID - This function retrieve the worker register with its ID
// params:
//   byte32 workerID
func (t *Registry) getRegistryByID(stub shim.ChaincodeStubInterface, registryID string) (*Registry, error) {
	var param Registry
	Avalbytes, err := stub.GetState(registryID)
	if err != nil {
		return nil, err
	}

	if Avalbytes == nil {
		return nil, errors.New("Worker with ID '" + registryID + "' does not exist")
	}

	err = json.Unmarshal(Avalbytes, &param)
	if err != nil {
		logger.Errorf("Error trying to decode the worker: %s", err)
		return nil, err
	}

	return &param, nil
}

// Init the init function of the chaincode
func (t *Registry) Init(stub shim.ChaincodeStubInterface) pb.Response {
	logger.Info("Registry Init")
	return shim.Success(nil)
}

// registryAdd - This function add a new organization
// params:
//   byte32 orgID
//   stromg uri
//   bytes32 scAddr
//   bytes32[] appTypeIds
// returns:
func (t *Registry) registryAdd(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("registryAdd")
	if len(args) != 4 {
		logger.Errorf("Mismatch number of arguments, expect 4, received %d", len(args))
		return shim.Error("registryAdd must include 4 arguments, orgID, uri, scAddr and appTypeIds")
	}

	var r Registry
	r.OrgID = args[0]
	r.URI = args[1]
	r.SCAddr = args[2]
	r.AppTypeIds = strings.Split(args[3], ",")
	r.Status = ACTIVE

	//Serialize the value
	value, err := json.Marshal(r)
	if err != nil {
		return shim.Error(err.Error())
	}

	logger.Infof("The registry ID: %s", r.OrgID)
	err = stub.PutState(r.OrgID, value)
	if err != nil {
		return shim.Error(err.Error())
	}

	compValue := []byte(r.OrgID)
	for _, appTypeID := range r.AppTypeIds {
		attrs, _ := processAttributes([]string{appTypeID, r.OrgID}, []string{BYTE32FORMAT, BYTE32FORMAT})
		compKey, err := stub.CreateCompositeKey(OBJECTTYPE, attrs)
		if err != nil {
			return shim.Error(err.Error())
		}
		err = stub.PutState(compKey, compValue)
		if err != nil {
			return shim.Error(err.Error())
		}
	}

	logger.Info("Finished registerAdd")
	return shim.Success(nil)
}

// registryUpdate - This function updates a Registry
// params:
//   byte32 orgID
//   stromg uri
//   bytes32 scAddr
//   bytes32[] appTypeIds
// returns:
func (t *Registry) registryUpdate(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("registryUpdate")

	if len(args) != 4 {
		logger.Errorf("Mismatch number of arguments, expect 4, received %d", len(args))
		return shim.Error("registryUpdate must include 4 arguments, orgID, uri, scAddr and appTypeIds")
	}

	r, err := t.getRegistryByID(stub, args[0])
	if err != nil {
		logger.Errorf("Can not find the registry with ID: %s", args[0])
		return shim.Error(err.Error())
	}

	var oldAppTypeIds []string
	oldAppTypeIds = append(r.AppTypeIds)
	r.URI = args[1]
	r.SCAddr = args[2]
	r.AppTypeIds = strings.Split(args[3], ",")

	//Serialize the value
	value, err := json.Marshal(r)
	if err != nil {
		return shim.Error(err.Error())
	}

	logger.Infof("The registry ID: %s", r.OrgID)
	err = stub.PutState(r.OrgID, value)
	if err != nil {
		return shim.Error(err.Error())
	}

	// Remove all the app IDs
	for _, appTypeID := range oldAppTypeIds {
		attrs, _ := processAttributes([]string{appTypeID, r.OrgID}, []string{BYTE32FORMAT, BYTE32FORMAT})
		compKey, err := stub.CreateCompositeKey(OBJECTTYPE, attrs)
		if err != nil {
			return shim.Error(err.Error())
		}
		err = stub.DelState(compKey)
		if err != nil {
			return shim.Error(err.Error())
		}
	}

	compValue := []byte(r.OrgID)
	for _, appTypeID := range r.AppTypeIds {
		attrs, _ := processAttributes([]string{appTypeID, r.OrgID}, []string{BYTE32FORMAT, BYTE32FORMAT})
		compKey, err := stub.CreateCompositeKey(OBJECTTYPE, attrs)
		if err != nil {
			return shim.Error(err.Error())
		}
		err = stub.PutState(compKey, compValue)
		if err != nil {
			return shim.Error(err.Error())
		}
	}

	logger.Info("Finished registerUpdate")
	return shim.Success(nil)
}

// registrySetStatus - This function set the status of a registry
// params:
//   byte32 orgID
//   uint256 status
// returns:
func (t *Registry) registrySetStatus(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("registrySetStatus")

	if len(args) != 2 {
		logger.Errorf("Expected parameters are 2, received %d", len(args))
		return shim.Error("registrySetStatus must include 2 arguments, orgID and status")
	}

	arg1, err := strconv.ParseUint(args[1], 10, 64)
	if err != nil {
		logger.Errorf("Registry status must be integer, received %v", args[1])
		return shim.Error(err.Error())
	}

	r, err := t.getRegistryByID(stub, args[0])
	if err != nil {
		logger.Errorf("Can not find the registry with ID: %s", args[0])
		return shim.Error(err.Error())
	}

	r.Status = arg1
	//Serialize the value
	value, err := json.Marshal(r)
	if err != nil {
		return shim.Error(err.Error())
	}

	err = stub.PutState(r.OrgID, value)
	if err != nil {
		return shim.Error(err.Error())
	}

	return shim.Success(value)
}

// registryLookUp - This function retrieves a list of registry ids that match input
// parameter. The registry must match to all input parameters (AND mode) to be
// included in the list.
// params:
//   bytes32 appTypeId
// returns:
//   int totalCount
//   string LookupTag
//   bytes32[] ids
func (t *Registry) registryLookUp(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("registryLookUp")

	if len(args) != 1 {
		logger.Errorf("Expected 1 argument, received %d", len(args))
		return shim.Error("registryLookUp must include 1 argument, appTypeId")
	}

	args = append(args, "")
	return t.registryLookUpNext(stub, args)
}

// registryLookUpNext - This function is called to retrieve additional results of the
// registry lookup initiated by registryLookUp call.
// params:
//   bytes32 appTypeId
//   string lookUpTag
// returns:
//   int totalCount
//   string newLookupTag
//   bytes32[] ids
func (t *Registry) registryLookUpNext(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("registryLookUpNext")

	if len(args) != 2 {
		logger.Errorf("Expected arguments are 2, received %d", len(args))
		return shim.Error("registryLookUpNext must include 2 argements, appTypeId and lookUpTag")
	}

	attrs, _ := processAttributes(args[0:1], []string{BYTE32FORMAT})

	logger.Infof("The lookup key: %v", attrs)

	iter, metadata, err := stub.GetStateByPartialCompositeKeyWithPagination(OBJECTTYPE, attrs,
		int32(PAGESIZE+1), args[1])
	if err != nil {
		logger.Errorf("Error trying to query with partial composite key: %s", err)
		return shim.Error(err.Error())
	}

	var resparam RegistryLookUpRes
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

// registryRetrieve - This function retrieves information for the Worker and it can be
// called from any authorized publickey (Ethereum address) or DID
// params:
//   byte32 orgId
// returns:
//   string uri
//   bytes32 scAddr
//   bytes32[] appTypeIds
//   uint6=256 status
func (t *Registry) registryRetrieve(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("registryRetrieve")
	if len(args) != 1 {
		logger.Errorf("Expected parameter is 1, received %d", len(args))
		return shim.Error("registryRetrieve must include 1 argument, orgId")
	}

	logger.Infof("registry retrieve orgId: %s", args[0])

	r, err := t.getRegistryByID(stub, args[0])
	if err != nil {
		return shim.Error(err.Error())
	}

	var resparam RegistryRetrieveRes
	resparam.Status = r.Status
	resparam.URI = r.URI
	resparam.SCAddr = r.SCAddr
	resparam.AppTypeIds = r.AppTypeIds

	//Serialize the response
	value, err := json.Marshal(resparam)
	if err != nil {
		return shim.Error(err.Error())
	}

	return shim.Success(value)
}

// query - This function retrieves information by org id
// params:
//   byte32 orgId
// returns:
func (t *Registry) query(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	logger.Info("query")

	// Get the state from the ledger
	logger.Infof("query by orgID: %s", args[0])
	Avalbytes, err := stub.GetState(args[0])
	if err != nil {
		return shim.Error(err.Error())
	}

	if Avalbytes == nil {
		return shim.Error("orgID '" + args[0] + "' does not exist")
	}

	return shim.Success(Avalbytes)
}

// Invoke - this function simply satisfy the main requirement of chaincode
func (t *Registry) Invoke(stub shim.ChaincodeStubInterface) pb.Response {
	logger.Info("Invoke")
	function, args := stub.GetFunctionAndParameters()
	if function == "registryAdd" {
		return t.registryAdd(stub, args)
	} else if function == "registryUpdate" {
		return t.registryUpdate(stub, args)
	} else if function == "registrySetStatus" {
		return t.registrySetStatus(stub, args)
	} else if function == "registryLookUp" {
		return t.registryLookUp(stub, args)
	} else if function == "registryLookUpNext" {
		return t.registryLookUpNext(stub, args)
	} else if function == "registryRetrieve" {
		return t.registryRetrieve(stub, args)
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
	err := shim.Start(new(Registry))
	if err != nil {
		logger.Errorf("Error starting Registry chaincode: %s", err)
	}
}
