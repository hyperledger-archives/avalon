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

from enum import IntEnum, unique


@unique
class EnclaveError(IntEnum):
    ENCLAVE_SUCCESS = 0,
    ENCLAVE_ERR_UNKNOWN = -1,
    ENCLAVE_ERR_MEMORY = -2,
    ENCLAVE_ERR_IO = -3,
    ENCLAVE_ERR_RUNTIME = -4,
    ENCLAVE_ERR_INDEX = -5,
    ENCLAVE_ERR_DIVIDE_BY_ZERO = -6,
    ENCLAVE_ERR_OVERFLOW = -7,
    ENCLAVE_ERR_VALUE = -8,
    ENCLAVE_ERR_SYSTEM = -9,
    # The system is busy and the operation may be retried. If retries fail,
    # this should be converted to ENCLAVE_ERR_SYSTEM for reporting.
    ENCLAVE_ERR_SYSTEM_BUSY = -10,
    ENCLAVE_ERR_CRYPTO = -11,
    ENCLAVE_ERR_INVALID_WORKLOAD = -12  # Invalid workload ID
