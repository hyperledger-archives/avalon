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

// Constants for work order
const (
	ORDERSUBMITTED = 0
	ORDERCOMPLETED = 1
	ORDERFAILED    = 2

	APIVERSION = "0x0101"
)

// WorkOrder Chaincode struct
type WorkOrder struct {
	WorkOrderId       string `json:"workOrderId"`
	WorkerId          string `json:"workerId"`
	RequesterId       string `json:"requesterId"`
	WorkOrderStatus   uint64 `json:"workOrderStatus`
	WorkOrderRequest  string `json:"workOrderRequest,omitempty"`
	WorkOrderResponse string `json:"workOrderResponse,omitempty"`
}

type WorkOrderSubmittedEvent struct {
	WorkOrderId      string `json:"workOrderId"`
	WorkerId         string `json:"workerId"`
	RequesterId      string `json:"requesterId"`
	WorkOrderRequest string `json:"workOrderRequest"`
	ErrorCode        uint64 `json:"errorCode"`
	SenderAddress    string `json:"senderAddress"`
	Version          string `json:"version"`
}

type WorkOrderCompletedEvent struct {
	RequesterId       string `json:"requesterId"`
	WorkOrderId       string `json:"workOrderId"`
	WorkOrderStatus   uint64 `json:"workOrderStatus"`
	WorkOrderResponse string `json:"workOrderResponse"`
	ErrorCode         uint64 `json:"errorCode"`
	Version           string `json:"version"`
}

type WorkOrderGetRes struct {
	WorkOrderStatus   uint64 `json:"workOrderStatus"`
	WorkerId          string `json:"workerId"`
	WorkOrderRequest  string `json:"workOrderRequest"`
	WorkOrderResponse string `json:"workOrderResponse"`
	ErrorCode         uint64 `json:"errorCode"`
}
