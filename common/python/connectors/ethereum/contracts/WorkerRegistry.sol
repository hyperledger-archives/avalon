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

contract WorkerRegistry{

    enum WorkerType {
        UNKNOWN,
        TEE_SGX,
        MPC,
        ZK
    }
    enum WorkerStatus {
        Unknown,
        Active,
        OffLine,
        Decommissioned,
        Compromised
    }
    struct WorkerInfo {
        bytes32 workerId;
        WorkerType workerType;
        bytes32 organizationId;
        bytes32[] applicationTypeIds;
        string details;
        WorkerStatus status;
    }

    // To store the contractor owner
    address private contractOwner;
    // Map of workerInfo identified by key workerId
    mapping (bytes32=>WorkerInfo)  private workersMap;
    // Map of index to workerId
    mapping (uint=>bytes32) private workersList;
    // Total number of workers count
    uint private workersCount;
    // Worker registry event
    event WorkerRegisterEvent(
        bytes32 workerId,
        WorkerType workerType,
        bytes32 organizationId,
        bytes32[] applicationTypeIds,
        string details,
        WorkerStatus status
    );
    // Worker Update event
    event WorkerUpdateEvent(
        bytes32 workerId,
        string details
    );
    // Worker set status event
    event WorkerSetStatusEvent(
        bytes32 workerId,
        WorkerStatus status
    );

    constructor() public {
        contractOwner = msg.sender;
        workersCount = 0;
    }
    // Restrict to call workerRegister by authorised contract owner or
    // if worker is of a known organization.
    modifier onlyOwner() {
        require(
            msg.sender == contractOwner,
            "Sender not authorized or worker doesn't belong to organization"
        );
        _;
    }

    function isValidWorkerType(WorkerType workerType) internal pure returns (bool)  {
        if (uint(workerType) >= uint(WorkerType.TEE_SGX) && uint(workerType) <= uint(WorkerType.ZK)) {
            return true;
        }
        else {
            return false;
        }
    }

    function workerRegister (
        bytes32 workerId,
        WorkerType workerType,
        bytes32 organizationId,
        bytes32[] memory applicationTypeIds,
        string memory details) public onlyOwner  {
        // Registry a new worker with associated with details of worker
        // If workerId, workerType and application id matches then it
        // Updates the organization id, details and applicationTypeIds
        require(workerId.length != 0,  "Empty worker id");
        require(isValidWorkerType(workerType) == true, "Invalid workerType");
        // Check if worker already exists, if yes then update the workersMap
        WorkerInfo storage worker = workersMap[workerId];
        if (worker.workerId == workerId &&
         worker.workerType == workerType &&
         worker.organizationId == organizationId) {
            worker.details = details;
            // Iterate through the list of provided app ids and insert if it doesn't exist
            for (uint i = 0; i < applicationTypeIds.length; i++) {
                bool exists = false;
                for (uint j = 0; j < worker.applicationTypeIds.length; j++) {
                    if (worker.applicationTypeIds[j] == applicationTypeIds[i]) {
                        exists = true;
                        break;
                    }
                }
                if (!exists) {
                    worker.applicationTypeIds.push(applicationTypeIds[i]);
                }
            }
        }
        else {
            // Insert to workersMap with worker id as key and workerInfo as value
            workersMap[workerId] = WorkerInfo(
                workerId,
                workerType,
                organizationId,
                applicationTypeIds,
                details,
                WorkerStatus.Active
                );
            // Insert to workersList with current workersCount as key and workerId as value.
            workersList[workersCount] = workerId;
            // Increment worker count
            workersCount++;
        }
        emit WorkerRegisterEvent(workerId, workerType, organizationId,
            applicationTypeIds, details, WorkerStatus.Active);
    }

    function workerUpdate(bytes32 workerId, string memory details) public onlyOwner {
        // Updates details field of worker identified by workerId
        require(workerId.length != 0,  "Empty worker id");
        require(workersMap[workerId].workerId == workerId, "workerId doesn't exist");
        workersMap[workerId].details = details;
        emit WorkerUpdateEvent(workerId, details);
    }

    function workerSetStatus(bytes32 workerId, WorkerStatus status) public onlyOwner {
        // Update the status of worker identified by workerId
        require(workerId.length != 0,  "Empty worker id");
        require(workersMap[workerId].workerId == workerId, "workerId doesn't exist");
        workersMap[workerId].status = status;
        emit WorkerSetStatusEvent(workerId, status);
    }

    function workerLookUp(
        WorkerType workerType,
        bytes32 organizationId,
        bytes32 applicationTypeId) public view returns(
            uint totalCount,
            string memory LookupTag,
            bytes32[] memory workerIds) {
        // Lookup worker identified workerType, organizationId, applicationTypeId
        // All input parameters are optional and if they passed
        // all of them should match
        uint wCount = 0;
        bytes32[] memory wList = new bytes32[](workersCount);
        uint8 argCount = 0;
        if (workerType != WorkerType.UNKNOWN) {
            argCount++;
        }
        if (organizationId.length != 0) {
            argCount++;
        }
        if (applicationTypeId.length != 0) {
            argCount++;
        }
        for (uint i = 0; i < workersCount; i++) {
            uint matched = 0;
            // Do lookup in workersList with an index and get the worker id and
            // use it to lookup in workersMap
            WorkerInfo memory worker = workersMap[workersList[i]];
            if (argCount == 0) {
                wList[wCount] = worker.workerId;
                wCount += 1;
            }
            else {
                if (workerType != WorkerType.UNKNOWN && worker.workerType == workerType) {
                    matched++;
                }
                if (organizationId.length != 0 && worker.organizationId == organizationId) {
                    matched++;
                }
                if (applicationTypeId.length != 0) {
                    for(uint j = 0; j < worker.applicationTypeIds.length; j++) {
                        if (worker.applicationTypeIds[j] == applicationTypeId) {
                            matched++;
                            break;
                        }
                    }
                }
                if (matched == argCount) {
                    wList[wCount] = worker.workerId;
                    wCount += 1;
                }
            }
        }
        // If array size is smaller than registry count then return only required size array.
        if (wCount < workersCount) {
            bytes32[] memory result = new bytes32[](wCount);
            for (uint k = 0; k < wCount; k++) {
                result[k] = wList[k];
            }
            // lookupTag is empty now need to implement with
            // specific content to be used to get the next available workers.
            return (wCount, "", result);
        }
        return (wCount, "", wList);
    }

    function workerRetrieve(bytes32 workerId) public view
        returns (
            WorkerType workerType,
            bytes32 organizationId,
            bytes32[] memory applicationTypeIds,
            string memory details,
            WorkerStatus status) {
        // Retrieve worker details identified by worker id
        // Returns all details associated with that worker
        require(workerId.length != 0,  "Empty worker id");
        require(workersMap[workerId].workerId == workerId, "workerId doesn't exist");
        // Do lookup with the given workerId from workerMap
        WorkerInfo memory worker = workersMap[workerId];
        // if worker id exists in map it returns workerInfo otherwise it
        // returns empty worker object, that's why first argument in return
        // statement is bool value indicates existence of worker id */
        return (worker.workerType,
            worker.organizationId, worker.applicationTypeIds,
            worker.details, worker.status
            );
    }

    // Stub for workerLookUpNext
    function workerLookUpNext(
        WorkerType workerType,
        bytes32 organizationId,
        bytes32 applicationTypeId,
        string memory lookUpTag) public pure
        returns(
        int totalCount,
        string memory newLookupTag,
        bytes32[] memory workerIds) {
        // If worker count is high then workerlookup will do pagination
        // with separator newLookUpTag. First workerLookup should be called
        // If returns non empty lookup tag then this function will be
        // called to get additional worker list
        // TODO: Functionality need to be implemented
        require(isValidWorkerType(workerType) == true, "Invalid workerType!!");
        require(applicationTypeId.length != 0,  "Empty Application id");
        require(organizationId.length != 0,  "Empty organization id");
        bytes32[] memory wIds;
        string memory newTag = "";
        int count = 0;
        return (count, newTag, wIds);
    }
}
