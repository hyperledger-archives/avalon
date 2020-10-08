#!/usr/bin/python3

# Copyright 2020 Intel Corporation
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
