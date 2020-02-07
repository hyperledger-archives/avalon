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

	OBJECTTYPE   = "Receipt"
	PAGESIZE     = 10
	UINT64FORMAT = "%020d"
	BYTE32FORMAT = "%-32v"
)

// Receipt data structure
type Receipt struct {
	WorkOrderId          string `json:"workOrgerId"`
	WorkerId             string `json:"workerId"`
	WorkerServiceId      string `json:"workerServiceId"`
	RequesterId          string `json:"requesterId"`
	ReceiptCreateStatus  uint64 `json:"receiptCreateStatus"`
	WorkOrderRequestHash string `json:"workOrderRequestHash"`
}

// ReceiptLookUpRes registry lookup response data structure
type ReceiptLookUpRes struct {
	TotalCount uint64   `json:"totalCount"`
	LookupTag  string   `json:"lookupTag"`
	IDs        []string `json:"ids,omitempty"`
}

// ReceiptRetrieveRes registry retrieve response data structure
type ReceiptRetrieveRes struct {
	WorkerServiceId      string `json:"workerServiceId"`
	WorkerId             string `json:"workerId"`
	RequesterId          string `json:"requesterId"`
	ReceiptCreateStatus  uint64 `json:"receiptCreateStatus"`
	WorkOrderRequestHash string `json:"workOrderRequestHash"`
	CurrentReceiptStatus uint64 `json:"currentReceiptStatus"`
}

type ReceiptCreatedEvent struct {
	WorkOrderId          string `json:"workOrgerId"`
	WorkerServiceId      string `json:"workerServiceId"`
	WorkerId             string `json:"workerId"`
	RequesterId          string `json:"requesterId"`
	ReceiptStatus        uint64 `json:"receiptStatus"`
	WorkOrderRequestHash string `json:"workOrderRequestHash"`
	ErrorCode            uint64 `json:"errorCode"`
}
