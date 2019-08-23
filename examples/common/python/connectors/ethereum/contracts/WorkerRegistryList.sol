/* Copyright 2019 Intel Corporation
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

pragma solidity >= 0.4.0;

contract DirectRegistry{
    enum RegistryStatus {
        Unknown,
        Active,
        OffLine,
        Decommissioned
    }
    struct RegistryInfo {
        bytes32 orgId;
        string uri;
        bytes32 scAddr;
        bytes32[] appTypeIds;
        RegistryStatus status;
    }

    event RegistryAddEvent(
        bytes32 orgId,
        string uri,
        bytes32 scAddr,
        bytes32[] appTypeIds,
        RegistryStatus status
    );

    event RegistryUpdateEvent(
        bytes32 orgId,
        string uri,
        bytes32 scAddr,
        bytes32[] appTypeIds
    );

    event RegistrySetStatusEvent(
        bytes32 orgId,
        RegistryStatus status
    );
    // To know the contractor owner
    address private contractOwner;
    // Map of registryInfo identified by key registryId
    mapping (bytes32 => RegistryInfo)  private registryMap;
    // Map of index to wokerId
    mapping (uint => bytes32) private registryList;
    // Total number of registries
    uint private registryCount;

    constructor() public {
        contractOwner = msg.sender;
        registryCount = 0;
    }
    // Restrict to call registryRegister by authorised contract owner or
    // is registry is of known organization.
    modifier onlyOwner() {
        require(
            msg.sender == contractOwner,
            "Sender not authorized"
        );
        _;
    }

    function registryAdd (
        bytes32 orgId,
        string memory uri,
        bytes32 scAddr,
        bytes32[] memory appTypeIds) public onlyOwner()  {
        // Add a new registry entry to registry list
        // with registry list organization id, uri, smart contract
        // address of worker registry contract and application type ids
        require(orgId.length != 0,  "Empty org id");
        require(bytes(uri).length != 0, "Empty uri");
        require(scAddr.length != 0, "Empty address");

        // Check if registry exists, if yes then error
        RegistryInfo memory registry = registryMap[orgId];
        require(registry.orgId != orgId && registry.scAddr != scAddr,
            "Registry exists with these details");
        registryMap[orgId] = RegistryInfo(
            orgId,
            uri,
            scAddr,
            appTypeIds,
            RegistryStatus.Active);
        // Insert to registryList with current registryCount as key and registryId as value.
        registryList[registryCount] = orgId;
        // Increment registry count
        registryCount++;
        emit RegistryAddEvent(orgId, uri, scAddr, appTypeIds, RegistryStatus.Active);
    }

    function registryUpdate(bytes32 orgId, string memory uri, bytes32 scAddr,
        bytes32[] memory appTypeIds) public {
        // Update registry with identified by organization id
        require(orgId.length != 0,  "Empty org id");
        require(bytes(uri).length != 0, "Empty uri");
        require(scAddr.length != 0, "Empty address");
        // Check if registry already exists, if yes then update the registryMap
        RegistryInfo memory registry = registryMap[orgId];
        require(registry.orgId == orgId, "Registry doesn't exist with these details");
        registryMap[orgId].uri = uri;
        registryMap[orgId].scAddr = scAddr;
        for (uint i = 0; i < appTypeIds.length; i++) {
            bool exists = false;
            for (uint j = 0; j < registry.appTypeIds.length; j++) {
                if (registry.appTypeIds[j] == appTypeIds[i]) {
                    exists = true;
                    break;
                }
            }
            if (!exists) {
                registryMap[orgId].appTypeIds.push(appTypeIds[i]);
            }
        }
        emit RegistryUpdateEvent(orgId, uri, scAddr, appTypeIds);
    }

    function registrySetStatus(bytes32 orgId, RegistryStatus status) public {
        // Set the registry status identified by organization id
        require(orgId.length != 0,  "Empty org id");
        require(registryMap[orgId].orgId == orgId, "orgId doesn't exist");
        registryMap[orgId].status = status;
        emit RegistrySetStatusEvent(orgId, status);
    }

    function registryLookUp(bytes32 appTypeId) public view returns(
            uint totalCount,
            string memory lookUpTag,
            bytes32[] memory orgIds) {
        uint wCount = 0;
        // lookUpTag is empty now, need to implement with specific content
        // to be used to get the next available registries.
        string memory lookUpString = "";
        // Since solidity doesn't support returning dynamic array of memory storage,
        // allocate the array with registry count.
        bytes32[] memory wList = new bytes32[](registryCount);
        for (uint i = 0; i < registryCount; i++) {
            // Do lookup in registryList with an index and get the registry id
            // and use it to lookup in registryMap
            RegistryInfo memory registry = registryMap[registryList[i]];
	    if (appTypeId != 0) {
            	for(uint j = 0; j < registry.appTypeIds.length; j++) {
                   if (registry.appTypeIds[j] == appTypeId) {
                      //If match, update registry list and registry count
                      wList[wCount] = registry.orgId;
                      wCount ++;
                   }
                }
	    }
	    else {
		    wList[wCount] = registry.orgId;
		    wCount ++;
	    }
        }
        // If array size is smaller than registry count then return only required size array.
        if (wCount < registryCount) {
            bytes32[] memory result = new bytes32[](wCount);
            for (uint k = 0; k < wCount; k++) {
                result[k] = wList[k];
            }
            return (wCount, lookUpString, result);
        }
        return (wCount, lookUpString, wList);
    }

    function registryRetrieve(bytes32 orgId) public view
        returns (
            string memory _uri,
            bytes32 _scAddr,
            bytes32[] memory _appTypeIds,
            RegistryStatus status) {
        // Retrieve registry details identified by orgId
        require(orgId.length != 0,  "Empty org id");
        require(registryMap[orgId].orgId == orgId, "orgId doesn't exist");
        // Do lookup with the given registryId from registryMap
        RegistryInfo memory registry = registryMap[orgId];
        return (registry.uri, registry.scAddr, registry.appTypeIds, registry.status);
    }

    //stub for registryLookUpNext
    function registryLookUpNext(
        bytes32 appTypeId,
        string memory lookUpTag) public pure
        returns(
        int totalCount,
        string memory newLookupTag,
        bytes32[] memory registryIds) {
        require(appTypeId.length != 0,  "Empty Application id");
        require(bytes(lookUpTag).length != 0,  "lookUpTag is empty");
        bytes32[] memory wIds;
        string memory newTag = "";
        int count = 0;
        return (count, newTag, wIds);
    }
}

