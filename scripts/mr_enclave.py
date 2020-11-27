#!/usr/bin/env python3

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

import toml
import binascii

def extract_mr_enclave(toml_file):
    with open(toml_file, 'r') as f:
        parsed_toml = toml.load(f)
    mr_enclave = parsed_toml["python"]["mr_enclave"]
    return mr_enclave

toml_file = "gsc-info.toml"
mr_enclave_hex_str = extract_mr_enclave(toml_file)

# Persist mr_enclave hex bytes into a file
mr_enclave_hex_byte_arr = binascii.unhexlify(mr_enclave_hex_str)
file_data = " ".join([hex(i) for i in mr_enclave_hex_byte_arr]).rstrip(" ")

with open("wpe_mr_enclave.txt", 'w') as f:
    f.write(file_data)


