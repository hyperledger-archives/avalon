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
status code defined for test case
"""
from enum import IntEnum, unique

@unique
class TestStep(IntEnum):
    SUCCESS = 0
    FAILURE = 1

@unique
class WorkOrderStatus(IntEnum):
    SUCCESS = 0
    FAILED = 1
    INVALID_PARAMETER_FORMAT_OR_VALUE = 2
    ACCESS_DENIED = 3
    INVALID_SIGNATURE = 4
    PENDING = 5
    SCHEDULED = 6
    PROCESSING = 7
    BUSY = 8
    UNKNOWN_ERROR = 9

@unique
class GetResultWaitTime(IntEnum):
    LOOP_WAIT_TIME = 3
