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

import binascii

# Return list of binary hex ids as list of UTF strings
def pretty_ids(ids):
    pretty_list = []
    for id in ids:
        pretty_list.append(hex_to_utf(id))
    return pretty_list

# Return binary hex as UTF string
def hex_to_utf(binary):
    return binascii.hexlify(binary).decode("UTF-8")
