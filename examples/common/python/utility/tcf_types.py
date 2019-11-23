# Copyright 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum, unique


@unique
class RegistryStatus(Enum):
    ACTIVE = 1
    OFF_LINE = 2
    DECOMMISSIONED = 3


@unique
class WorkerType(Enum):
    TEE_SGX = 1
    MPC = 2
    ZK = 3


@unique
class WorkerStatus(Enum):
    ACTIVE = 1
    OFF_LINE = 2
    DECOMMISSIONED = 3
    COMPROMISED = 4


@unique
class JsonRpcErrorCode(Enum):
    SUCCESS = 0
    UNKNOWN_ERROR = 1
    INVALID_PARAMETER = 2
    ACCESS_DENIED = 3
    INVALID_SIGNATURE = 4
    NO_LOOKUP_RESULTS = 5
    UNSUPPORTED_MODE = 6
    KEY_EXISTS = 9


@unique
class ReceiptCreateStatus(Enum):
    PENDING = 0
    COMPLETED = 1
    PROCESSED = 2
    FAILED = 3
    REJECTED = 4
