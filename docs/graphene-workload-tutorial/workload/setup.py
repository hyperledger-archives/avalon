#!/usr/bin/env python

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

import sys

# This should only be run with python3
if sys.version_info[0] < 3:
    print('ERROR: must run with python3')
    sys.exit(1)

from setuptools import setup, find_packages

setup(name='avalon_python_workload',
      version=0.6,
      description='Avalon python workload for Graphene',
      author='Hyperledger Avalon',
      url='https://github.com/hyperledger/avalon',
      packages=find_packages(),
      data_files=[],
      entry_points={}
      )
