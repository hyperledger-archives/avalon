from enum import Enum, unique
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

from enum import unique, IntEnum


@unique
class JsonRpcErrorCode(IntEnum):
    """
    JSON RPC error code values:
    0 - SUCCESS
    1 - UNKNOWN_ERROR
    2 - INVALID_PARAMETER format or value
    3 - ACCESS_DENIED
    4 - INVALID_SIGNATURE
    5 - NO_LOOKUP_RESULTS no more lookup results remaining
    6 - UNSUPPORTED_MODE (e.g. synchronous, asynchronous, poll,
        or notification)
    -32768 to -32000 - reserved for pre-defined errors in the JSON RPC spec.

    From EEA spec 4.1.1.
    """
    SUCCESS = 0
    UNKNOWN_ERROR = 1
    INVALID_PARAMETER = 2
    ACCESS_DENIED = 3
    INVALID_SIGNATURE = 4
    NO_LOOKUP_RESULTS = 5
    UNSUPPORTED_MODE = 6
