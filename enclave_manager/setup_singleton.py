#!/usr/bin/env python

# Copyright 2018-2020 Intel Corporation
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

# This should only be run with python3
import sys
if sys.version_info[0] < 3:
    print('ERROR: must run with python3')
    sys.exit(1)

from setuptools import setup, find_packages, Extension

tcf_root_dir = os.environ.get('TCF_HOME', '../')

enclave_bridge_wrapper_path = os.path.join(tcf_root_dir,
         'tc/sgx/trusted_worker_manager/enclave_untrusted/enclave_bridge_wrapper')

enclave_bridge_path = os.path.join(tcf_root_dir,
        'tc/sgx/trusted_worker_manager/enclave_untrusted/enclave_bridge')

# Defaults to path '/opt/intel/sgxsdk' if SGX_SDK env variable is not passed
sgx_sdk = os.environ.get('SGX_SDK', '/opt/intel/sgxsdk')

## -----------------------------------------------------------------
## Set up the enclave
## -----------------------------------------------------------------
debug_flag = os.environ.get('TCF_DEBUG_BUILD',0)

compile_args = [
    '-std=c++11',
    '-Wno-switch',
    '-Wno-unused-function',
    '-Wno-unused-variable',
]

# By default the extension class adds '-O2' to the compile
# flags, this lets us override since these are appended to
# the compilation switches.
if debug_flag :
    compile_args += ['-g']

include_dirs = [
    enclave_bridge_wrapper_path,
    os.path.join(enclave_bridge_wrapper_path, 'singleton'),
    enclave_bridge_path,
    os.path.join(enclave_bridge_path, 'singleton'),
    os.path.join(tcf_root_dir, 'common/cpp'),
    os.path.join(tcf_root_dir, 'tc/sgx/trusted_worker_manager/common'),
    os.path.join(tcf_root_dir, 'common/cpp/crypto'),
    os.path.join(tcf_root_dir, 'common/cpp/packages/base64'),
    os.path.join(sgx_sdk, 'include')
]

library_dirs = [
    os.path.join(enclave_bridge_path, 'build/lib'),
    os.path.join(tcf_root_dir, "common/cpp/build"),
]

libraries = [
    'uavalon-parson',
    'uavalon-verify-ias-report',
    'avalon-singleton-enclave-bridge'
]

enclave_module_files = [
    "avalon_enclave_manager/singleton/singleton_enclave.i",
    os.path.join(enclave_bridge_wrapper_path, 'swig_utils.cpp'),
    os.path.join(enclave_bridge_wrapper_path, 'work_order_wrap.cpp'),
    os.path.join(enclave_bridge_wrapper_path, 'enclave_info.cpp'),
    os.path.join(enclave_bridge_wrapper_path, 'signup_info.cpp'),
    os.path.join(enclave_bridge_wrapper_path, 'singleton/signup_info_singleton.cpp'),
]

enclave_module = Extension(
    'avalon_enclave_manager.singleton._singleton_enclave',
    enclave_module_files,
    swig_opts = ['-c++', '-threads'] + ['-I%s' % i for i in include_dirs],
    extra_compile_args = compile_args,
    libraries = libraries,
    include_dirs = include_dirs,
    library_dirs = library_dirs,
    runtime_library_dirs = [os.path.join(enclave_bridge_path, 'build/lib')],
    define_macros = [
                        ('_UNTRUSTED_', 1),
                        ('TCF_DEBUG_BUILD', debug_flag),
                    ],
    undef_macros = ['NDEBUG', 'EDEBUG']
    )

## -----------------------------------------------------------------
version = subprocess.check_output(
    os.path.join(tcf_root_dir, 'bin/get_version')).decode('ascii').strip()

setup(name='singleton_enclave_manager',
      version = version,
      description = 'Avalon Intel SGX Singleton Enclave Manager',
      author = 'Hyperledger Avalon',
      url = 'https://github.com/hyperledger/avalon',
      packages = find_packages(),
      install_requires = [
          'requests'
          ],
      ext_modules = [
          enclave_module
      ],
      data_files = [],
      entry_points = {
        'console_scripts':
        ['enclave_manager = avalon_enclave_manager.singleton.singleton_enclave_manager:main']
          }
)
