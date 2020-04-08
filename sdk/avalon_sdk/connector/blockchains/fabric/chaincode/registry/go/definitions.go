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
	ACTIVE         = 1
	OFFLINE        = 2
	DECOMMISSIONED = 3

	OBJECTTYPE   = "Registry"
	PAGESIZE     = 10
	UINT64FORMAT = "%020d"
	BYTE32FORMAT = "%-32v"
)

// Registry data structure
type Registry struct {
	OrgID      string   `json:"orgID"`
	URI        string   `json:"uri"`
	SCAddr     string   `json:"scAddr"`
	AppTypeIds []string `json:"appTypeIds,omitempty"`
	Status     uint64   `json:"status"`
}

// RegistryLookUpRes registry lookup response data structure
type RegistryLookUpRes struct {
	TotalCount uint64   `json:"totalCount"`
	LookupTag  string   `json:"lookupTag"`
	IDs        []string `json:"ids,omitempty"`
}

// RegistryRetrieveRes registry retrieve response data structure
type RegistryRetrieveRes struct {
	URI        string   `json:"uri"`
	SCAddr     string   `json:"scAddr"`
	AppTypeIds []string `json:"appTypeIds,omitempty"`
	Status     uint64   `json:"status"`
}
