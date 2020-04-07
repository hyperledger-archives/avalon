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

// Constant values for registry
const (
    PENDING   = 0
    COMPLETED = 1
    PROCESSED = 2
    FAILED    = 3
    REJECTED  = 4

    RECEIPT_CREATE   = "ReceiptCreate"
    RECEIPT_UPDATE      = "ReceiptUpdate"
    PAGESIZE     = 10
    UINT64FORMAT = "%020d"
    BYTE32FORMAT = "%-32v"
)

// Receipt data structure
type Receipt struct {
    ReceiptCreate    ReceiptCreate `json:"receiptCreate"`
    ReceiptUpdates    []ReceiptUpdate `json:"receiptUpdates"`
}

// ReceiptCreate data structure
type ReceiptCreate struct {
    WorkOrderId          string `json:"workOrderId"`
    WorkerId             string `json:"workerId"`
    WorkerServiceId      string `json:"workerServiceId"`
    RequesterId          string `json:"requesterId"`
    ReceiptCreateStatus  uint64 `json:"receiptCreateStatus"`
    WorkOrderRequestHash string `json:"workOrderRequestHash"`
}

// ReceiptUpdate data structure
type ReceiptUpdate struct {
    WorkOrderId          string `json:"workOrderId"`
    UpdaterId            string `json:"UpdaterId"`
    UpdateType           uint64 `json:"UpdateType"`
    UpdateData           string `json:"UpdateData"`
    UpdateSignature      string `json:"UpdateSignature"`
    SignatureRules       string `json:"SignatureRules"`
}
// ReceiptLookUpRes registry lookup response data structure
type ReceiptLookUpRes struct {
    TotalCount uint64   `json:"totalCount"`
    LookupTag  string   `json:"lookupTag"`
    IDs        []string `json:"ids,omitempty"`
}

// ReceiptRetrieveRes receipt retrieve response data structure
type ReceiptRetrieveRes struct {
    WorkerServiceId      string `json:"workerServiceId"`
    WorkerId             string `json:"workerId"`
    RequesterId          string `json:"requesterId"`
    ReceiptCreateStatus  uint64 `json:"receiptCreateStatus"`
    WorkOrderRequestHash string `json:"workOrderRequestHash"`
    CurrentReceiptStatus uint64 `json:"currentReceiptStatus"`
}

// ReceiptUpdateRetrieveRes receipt update retrieve response data structure
type ReceiptUpdateRetrieveRes struct {
    UpdaterId            string `json:"updaterId"`
    UpdateType           uint64 `json:"updateType"`
    UpdateData           string `json:"updateData"`
    UpdateSignature      string `json:"updateSignature"`
    SignatureRules       string `json:"signatureRules"`
    UpdateCount          uint64 `json:"updateCount"`
}
type ReceiptCreatedEvent struct {
    WorkOrderId          string `json:"workOrderId"`
    WorkerServiceId      string `json:"workerServiceId"`
    WorkerId             string `json:"workerId"`
    RequesterId          string `json:"requesterId"`
    ReceiptStatus        uint64 `json:"receiptStatus"`
    WorkOrderRequestHash string `json:"workOrderRequestHash"`
    ErrorCode            uint64 `json:"errorCode"`
}

type ReceiptUpdatedEvent struct {
    WorkOrderId          string `json:"workOrderId"`
    UpdaterId            string `json:"updaterId"`
    UpdateType           uint64 `json:"updateType"`
    UpdateData           string `json:"updateData"`
    UpdateSignature      string `json:"UpdateSignature"`
    SignatureRules       string `json:"SignatureRules"`
    ErrorCode            uint64 `json:"errorCode"`
}