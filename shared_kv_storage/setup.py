#!/usr/bin/env python

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

import os
import sys
import subprocess

from setuptools import setup, find_packages, Extension

tcf_root_dir = os.environ.get('TCF_HOME', '../')
module_src_path = os.path.join(tcf_root_dir, 'shared_kv_storage/db_store')


if os.sys.version_info[0] < 3:
    print('ERROR: must run with python3')
    sys.exit(1)

conf_dir = "/etc/avalon"

data_files = [
    (conf_dir, ['packaging/lmdb_config.toml.example'])
]

if os.path.exists("/lib/systemd/system"):
    data_files.append(('/lib/systemd/system',
                       ['packaging/systemd/shared_kv_storage.service']))


debug_flag = os.environ.get('TCF_DEBUG_BUILD', 0)

compile_args = [
    '-std=c++11',
    '-Wno-switch',
    '-Wno-unused-function',
    '-Wno-unused-variable',
]

# By default the extension class adds '-O2' to the compile
# flags, this lets us override since these are appended to
# the compilation switches.
if debug_flag:
    compile_args += ['-g']

include_dirs = [
    module_src_path,
    os.path.join(tcf_root_dir, 'common/cpp')
]

library_dirs = [
    os.path.join(tcf_root_dir, 'shared_kv_storage/db_store/packages/build'),
]

libraries = [
    'lmdb-store',
    'lmdb'
]

module_files = [
    os.path.join(
        tcf_root_dir, 'shared_kv_storage/kv_storage/remote_lmdb/db_store.i'),
    os.path.join(module_src_path, 'db_store.cpp'),
]

dbstore_module = Extension(
    'kv_storage.remote_lmdb._db_store',
    module_files,
    swig_opts=['-c++', '-threads'] + ['-I%s' % i for i in include_dirs],
    extra_compile_args=compile_args,
    libraries=libraries,
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    define_macros=[],
    undef_macros=[]
)

setup(name='kv_storage',
      version=subprocess.check_output(
          ['../bin/get_version']).decode('utf-8').strip(),
      description='Shared KV Storage',
      author='Hyperledger Avalon',
      url='https://github.com/hyperledger/avalon',
      packages=find_packages(),
      install_requires=[
          'requests',
      ],
      ext_modules=[
          dbstore_module
      ],
      data_files=data_files,
      entry_points={
          'console_scripts':
          ['kv_storage = kv_storage.remote_lmdb.lmdb_listener:main']
      })
