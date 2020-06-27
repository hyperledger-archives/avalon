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

from enum import Enum, unique


@unique
class RegistryStatus(Enum):
    """
    Worker registry status values:
    1 - registry is ACTIVE
    2 - registry is temporarily OFF_LINE
    3 - registry is DECOMMISSIONED

    From EEA spec 5.2.
    """
    ACTIVE = 1
    OFF_LINE = 2
    DECOMMISSIONED = 3
