#!/usr/bin/env python3

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

"""
error_code_handler.py -- Error code defined for handlers 

"""

from enum import IntEnum, unique
@unique
class WorkorderError(IntEnum):
    SUCCESS = 0
    UNKNOWN_ERROR = 1
    INVALID_PARAMETER_FORMAT_OR_VALUE = 2
    ACCESS_DENIED = 3
    INVALID_SIGNATURE = 4
    PENDING = 5
    PROCESSING = 6
    BUSY = 7

from enum import IntEnum, unique
@unique
class WorkerStatus(IntEnum):
    ACTIVE = 0
    OFF_LINE = 1
    DECOMMISSIONED = 2
    COMPROMISED = 3
    
from enum import IntEnum, unique
@unique
class WorkerError(IntEnum):
    SUCCESS = 0
    UNKNOWN_ERROR = 1
    INVALID_PARAMETER_FORMAT_OR_VALUE = 2
    ACCESS_DENIED = 3
    INVALID_SIGNATURE = 4
    NO_MORE_LOOKUP_RESULTS = 5
    UNSUPPORTED_MODE = 6

from enum import IntEnum, unique
@unique
class ReceiptCreateStatus(IntEnum):
    PENDING = 0
    COMPLETED = 1
    PROCESSED = 2
    FAILED = 3
    REJECTED = 4

from enum import IntEnum, unique
@unique
class SignatureStatus(IntEnum):
    PASSED = 1
    FAILED = 2
    SUCCESSFULLY_SIGNED = 3
    INVALID_SIGNATURE_FORMAT = -1
    ERROR_RESPONSE = -2
    INVALID_VERIFICATION_KEY = -3

from enum import IntEnum, unique
@unique
class WorkOrderStatus(IntEnum):
    SUCCESS = 0
    FAILED = 1
    PROCESSING = 2
    SCHEDULED = 3

