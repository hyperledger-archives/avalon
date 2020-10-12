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

import os
import sys
from jinja2 import Template

if len(sys.argv) != 2:
    print("Name of workload required as argument.")
    sys.exit(1)

name = sys.argv[1]

# Normalize name to lowercase
workload = name.lower()
OUT_DIR = workload

# Print name of workload to console
print("Name of new workload: {}".format(workload))

# Convert to get the name of the class 
workload_classname = workload.title()

# Template files to be processed 
FILES = {
    "Dockerfile.template",
    "avalon-workload-graphene.yaml.template",
    "avalon-workload-gsgx.yaml.template",
    os.path.join("compose","graphene-sgx.yaml.template"),
    "docker-compose.yaml.template",
    os.path.join("graphene_sgx","build_gsc_workload.sh.template"),
    os.path.join("src","my_workload.py.template"),
    os.path.join("tests","test_work_orders.json.template"),
    "workload.json.template",
    "Makefile.template"
}

IN_DIR = "workload"

# Create intermediate directories meant to be part of resultant workload
os.makedirs(os.path.join(OUT_DIR,"src"))
os.mkdir(os.path.join(OUT_DIR,"tests"))
os.mkdir(os.path.join(OUT_DIR,"compose"))
os.mkdir(os.path.join(OUT_DIR,"graphene_sgx"))

for filename in FILES:

    with open(os.path.join(IN_DIR,filename), "r") as fh:
        content = fh.read()
        # Create instance of Template
        temp = Template(content)
        # Carry out substitution
        new_content = temp.render(my_workload=workload, My_workload=workload_classname)

    # Prepending output directory to filename
    new_filename = os.path.join(OUT_DIR, filename[:filename.rindex('.')])
    if filename == os.path.join("src","my_workload.py.template"):
        new_filename = new_filename.replace("my_workload", workload)

    with open(new_filename, "w") as fh:
        # Write content to new file
        fh.write(new_content)

