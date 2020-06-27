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

func (t *Receipt) createReceiptUpdateRetrieveResponse(ru *ReceiptUpdate, r_size uint64) (*ReceiptUpdateRetrieveRes) {
    var resparam ReceiptUpdateRetrieveRes
    resparam.UpdaterId = ru.UpdaterId
    resparam.UpdateType = ru.UpdateType
    resparam.UpdateData = ru.UpdateData
    resparam.UpdateSignature = ru.UpdateSignature
    resparam.SignatureRules = ru.SignatureRules
    resparam.UpdateCount = r_size

    return &resparam
}
// Init the init function of the chaincode
func (t *Receipt) Init(stub shim.ChaincodeStubInterface) pb.Response {
    logger.Info("Receipt Init")
    return shim.Success(nil)
}

// registryAdd - This function create work order receipt for work order
// params:
//   bytes32 workOrderId,
//   bytes32 workerId,
//   bytes32 workerServiceId,
//   bytes32 requesterId,
//   uint256 receiptCreateStatus,
//   bytes workOrderRequestHash
// returns:
//   uint256
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

    var rc ReceiptCreate
    rc.WorkOrderId = args[0]
    rc.WorkerId = args[1]
    rc.WorkerServiceId = args[2]
    rc.RequesterId = args[3]
    rc.ReceiptCreateStatus = arg4
    rc.WorkOrderRequestHash = args[5]

    var r Receipt
    r.ReceiptCreate = rc
    r.ReceiptUpdates = []ReceiptUpdate{}
    //Serialize the value
    value, err := json.Marshal(r)
    if err != nil {
        return shim.Error(err.Error())
    }

    err = stub.PutState(rc.WorkOrderId, value)
    if err != nil {
        return shim.Error(err.Error())
    }

    compValue := []byte(rc.WorkOrderId)

    attrs, _ := processAttributes([]string{rc.WorkerServiceId, rc.WorkerId, rc.RequesterId, args[4]},
        []string{BYTE32FORMAT, BYTE32FORMAT, BYTE32FORMAT, UINT64FORMAT})
    compKey, err := stub.CreateCompositeKey(RECEIPT_CREATE, attrs)
    if err != nil {
        return shim.Error(err.Error())
    }
    err = stub.PutState(compKey, compValue)
    if err != nil {
        return shim.Error(err.Error())
    }

    // Handling payload for the event
    var eventData ReceiptCreatedEvent
    eventData.WorkOrderId = rc.WorkOrderId
    eventData.WorkerServiceId = rc.WorkerServiceId
    eventData.WorkerId = rc.WorkerId
    eventData.RequesterId = rc.RequesterId
    eventData.ReceiptStatus = rc.ReceiptCreateStatus
    eventData.WorkOrderRequestHash = rc.WorkOrderRequestHash
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

    if len(args) != 6 {
        logger.Errorf("Mismatch number of arguments, expect 6, received %d", len(args))
        return shim.Error("workOrderReceiptUpdate must include 6 arguments, workOrderId, updaterId, updateType, updateData, updateSignature and signatureRules")
    }

    arg2, err := strconv.ParseUint(args[2], 10, 64)
    if err != nil {
        logger.Errorf("Receipt update type must be an integer")
        return shim.Error("Receipt update type must be an integer")
    }

    r, err := t.getReceiptByID(stub, args[0])
    if err != nil {
        return shim.Error(err.Error())
    }

    var ru ReceiptUpdate
    ru.WorkOrderId = args[0]
    ru.UpdaterId = args[1]
    ru.UpdateType = arg2
    ru.UpdateData = args[3]
    ru.UpdateSignature = args[4]
    ru.SignatureRules = args[5]
    var err_code uint64
    // If updateType is from 0 to 255, the update sets the receipt status to updateType value
    // 0 - "pending". The work order is waiting to be processed by the worker
    // 1 - "completed". The worker processed the Work Order and no more worker updates are expected
    // 2 - "processed". The worker processed the Work Order, but additional worker updates are expected, e.g. oracle notifications
    // 3 - "failed". The Work Order processing failed, e.g. by the worker service because of an invalid workerId
    // 4 - "rejected". The Work Order is rejected by the smart contract, e.g. invalid workerServiceId
    // values from 5 to 254 are reserved
    // value 255 indicates any status
    // values above 255 are application specific values
    if arg2>=0 && arg2 < 256 {
        r.ReceiptUpdates = append(r.ReceiptUpdates, ru)
        err_code = 0
    } else {
        err_code = 1
    }
    //Serialize the value
    value, err := json.Marshal(r)
    if err != nil {
        return shim.Error(err.Error())
    }

    err = stub.PutState(ru.WorkOrderId, value)
    if err != nil {
        return shim.Error(err.Error())
    }

    // Store value in composite key
    compValue := value

    attrs, _ := processAttributes([]string{ru.WorkOrderId, ru.UpdaterId, strconv.Itoa(len(r.ReceiptUpdates))},
        []string{BYTE32FORMAT, BYTE32FORMAT, UINT64FORMAT})
    compKey, err := stub.CreateCompositeKey(RECEIPT_UPDATE, attrs)
    if err != nil {
        return shim.Error(err.Error())
    }
    err = stub.PutState(compKey, compValue)
    if err != nil {
        return shim.Error(err.Error())
    }

    // Handling payload for the event
    var eventData ReceiptUpdatedEvent
    eventData.WorkOrderId = ru.WorkOrderId
    eventData.UpdaterId = ru.UpdaterId
    eventData.UpdateType = ru.UpdateType
    eventData.UpdateData = ru.UpdateData
    eventData.UpdateSignature = ru.UpdateSignature
    eventData.SignatureRules = ru.SignatureRules
    eventData.ErrorCode = err_code

    eventPayload, err := json.Marshal(eventData)
    if err != nil {
        return shim.Error(err.Error())
    }

    err = stub.SetEvent("workOrderReceiptUpdated", eventPayload)
    if err != nil {
        return shim.Error(err.Error())
    }

    logger.Info("Finished workOrderReceiptUpdate")
    return shim.Success(nil)
}

// workOrderReceiptLookUp - This function retrieves a list of receipt Ids filtered by one or more 
// input parameters. If more than one input parameter is provided, a receipt must match all
// parameters to be included in the list (Boolean AND operation).
// params:
//    bytes32 workerServiceId,
//    bytes32 workerId,
//    bytes32 requesterId,
//    uint256 receiptStatus
// returns:
//   int totalCount
//   string lookupTag
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

// workOrderReceiptLookUpNext - This function retrieve additional results of the Work Order receipt
// lookup initiated by the workOrderReceiptLookUp call.
// params:
//   bytes32 workerServiceId,
//   bytes32 workerId,
//   bytes32 requesterId,
//   uint256 receiptStatus,
//   uint256 lastLookUpTag
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

    iter, metadata, err := stub.GetStateByPartialCompositeKeyWithPagination(RECEIPT_CREATE, attrs,
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

// workOrderReceiptUpdateRetrieve - This function retrieves update information for the Work order id
// params:
//  bytes32 workOrderId,
//  bytes32 updaterId,
//  uint256 updateIndex
// returns:
//   bytes32 updaterId,
//   uint256 updateType,
//   bytes updateData,
//   bytes updateSignature,
//   string signatureRules,
//   uint256 updateCount
func (t *Receipt) workOrderReceiptUpdateRetrieve(stub shim.ChaincodeStubInterface, args []string) pb.Response {
    if len(args) != 3 {
        logger.Errorf("Expected parameter number of arguments are 3, received %d", len(args))
        return shim.Error("workOrderReceiptUpdateRetrieve is requires 3 arguments, workOrderId, updaterId, updateIndex")
    }

    arg2, err := strconv.ParseUint(args[2], 10, 64)
    if err != nil {
        logger.Errorf("Receipt update type must be an integer")
        return shim.Error("Receipt update type must be an integer")
    }

    var ru ReceiptUpdate
    r, err := t.getReceiptByID(stub, args[0])
    if err != nil {
        return shim.Error(err.Error())
    }
    r_size := uint64(len(r.ReceiptUpdates))
    // If updateIndex value "0xFFFFFFFF" is reserved to retrieve the last received update.
    if arg2 == 256 {
        index := r_size - 1
        if index < 0 {
            return shim.Error("No Updates available for the receipt")
        }
        ru = r.ReceiptUpdates[index]
        if args[1] == "" || ru.UpdaterId == args[1] {
            resparam := t.createReceiptUpdateRetrieveResponse(&ru, r_size)
            value, err := json.Marshal(resparam)
            if err != nil {
                return shim.Error(err.Error())
            }
            return shim.Success(value)
        } else {
            return shim.Error("No matches found for the receipt")
        }
    }
    attrs, err := processAttributes(args[0:3], []string{BYTE32FORMAT, BYTE32FORMAT, UINT64FORMAT})
    if err != nil {
        logger.Errorf("Cannot format the query parameters")
        return shim.Error(err.Error())
    }

    logger.Infof("The lookup key: %v", attrs)
    iter, metadata, err := stub.GetStateByPartialCompositeKeyWithPagination(RECEIPT_UPDATE, attrs,
        int32(PAGESIZE+1), args[4])
    if err != nil {
        logger.Errorf("Error trying to query with partial composite key: %s", err)
        return shim.Error(err.Error())
    }

    for iter.HasNext() {
        item, _ := iter.Next()
        logger.Infof("The value: %v\n metadata: %v", item, metadata)
        err := json.Unmarshal(item.Value, &ru)
        if err != nil {
            return shim.Error(err.Error())
        }
    }
    resparam := t.createReceiptUpdateRetrieveResponse(&ru, r_size)
    //Serialize the response
    value, err := json.Marshal(resparam)
    if err != nil {
        return shim.Error(err.Error())
    }

    return shim.Success(value)
}
// workOrderReceiptRetrieve - This function retrieves receipt information for the Work Order
// params:
//   bytes32 workOrderId
// returns:
//   bytes32 workerServiceId,
//   bytes32 workerId,
//   bytes32 requesterId,
//   uint256 receiptCreateStatus,
//   bytes workOrderRequestHash,
//   uint256 currentReceiptStatus
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
    rc := r.ReceiptCreate
    resparam.WorkerServiceId = rc.WorkerServiceId
    resparam.WorkerId = rc.WorkerId
    resparam.RequesterId = rc.RequesterId
    resparam.ReceiptCreateStatus = rc.ReceiptCreateStatus
    resparam.WorkOrderRequestHash = rc.WorkOrderRequestHash
    resparam.CurrentReceiptStatus = rc.ReceiptCreateStatus

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
    } else if function == "workOrderReceiptUpdateRetrieve" {
        return t.workOrderReceiptUpdateRetrieve(stub, args)
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
            // If search argument workerType is 0 then ignore parameter
            arg, err := strconv.ParseUint(arg1[i], 10, 64)
            if err != nil {
                return nil, err
            }
            if arg != 0 {
                attrs = append(attrs, fmt.Sprintf(UINT64FORMAT, arg))
            }
            attrs = append(attrs, fmt.Sprintf(UINT64FORMAT, arg))
        case BYTE32FORMAT:
            // If search arguments orgId and appId are empty then ignore parameter
            arg := fmt.Sprintf("%v", arg1[i])
            if len(arg) > 0 {
                attrs = append(attrs, fmt.Sprintf(BYTE32FORMAT, arg1[i]))
            }
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
