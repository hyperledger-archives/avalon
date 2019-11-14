#!/usr/bin/env python

# Copyright 2018 Intel Corporation
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

tcf_root_dir = os.environ.get('TCF_HOME', '../../../../')
enclave_dir = os.path.realpath(os.path.join(tcf_root_dir, 'tc/sgx/trusted_worker_manager/enclave'))

module_path = 'tc/sgx/trusted_worker_manager/enclave_wrapper'
module_src_path = os.path.join(tcf_root_dir, module_path)

sgx_sdk_env = os.environ.get('SGX_SDK', '/opt/intel/sgxsdk')
sgx_ssl_env = os.environ.get('SGX_SSL', '/opt/intel/sgxssl')
sgx_mode_env = os.environ.get('SGX_MODE', 'SIM')
if not sgx_mode_env or (sgx_mode_env != "SIM" and sgx_mode_env != "HW"):
    print("error: SGX_MODE value must be HW or SIM, current value is: ", sgx_mode_env)
    sys.exit(2)


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
    module_src_path,
    os.path.join(tcf_root_dir, 'tc/sgx/common'),
    os.path.join(tcf_root_dir, 'tc/sgx/common/crypto'),
    os.path.join(module_src_path, 'build'),
    os.path.join(sgx_sdk_env,  'include'),
    os.path.join(tcf_root_dir, 'tc/sgx/common/packages/db_store'),
    os.path.join(tcf_root_dir, 'tc/sgx/common/packages/base64')
]

library_dirs = [
    os.path.join(tcf_root_dir, "tc/sgx/common/build"),
    os.path.join(os.environ['SGX_SDK'], 'lib64'),
    os.path.join(sgx_ssl_env, 'lib64'),
    os.path.join(sgx_ssl_env, 'lib64', 'release')
]

libraries = [
    'utcf-common',
    'utcf-lmdb-store',
    'lmdb'
]

if sgx_mode_env == "HW":
    libraries.append('sgx_urts')
    libraries.append('sgx_uae_service')
    SGX_SIMULATOR_value = '0'
if sgx_mode_env == "SIM":
    libraries.append('sgx_urts_sim')
    libraries.append('sgx_uae_service_sim')
    SGX_SIMULATOR_value = '1'

# This library is needed as it's used by enclave_u.c
libraries.append('sgx_usgxssl')

module_files = [
    "tcf_enclave_manager/tcf_enclave.i",
    os.path.join(module_src_path, 'swig_utils.cpp'),
    os.path.join(module_src_path, 'ocall.cpp'),
    os.path.join(module_src_path, 'base.cpp'),
    os.path.join(module_src_path, 'enclave_u.c'),
    os.path.join(module_src_path, 'log.cpp'),
    os.path.join(module_src_path, 'work_order.cpp'),
    os.path.join(module_src_path, 'work_order_wrap.cpp'),
    os.path.join(module_src_path, 'signup.cpp'),
    os.path.join(module_src_path, 'enclave_queue.cpp'),
    os.path.join(module_src_path, 'enclave.cpp'),
    os.path.join(module_src_path, 'enclave_info.cpp'),
    os.path.join(module_src_path, 'signup_info.cpp'),
    os.path.join(module_src_path, 'db_store.cpp'),
    os.path.join(module_src_path, 'file_io_handler.cpp'),
    os.path.join(module_src_path, 'file_io_processor.cpp'),
    os.path.join(module_src_path, 'io_handler.cpp')
]

enclave_module = Extension(
    'tcf_enclave_manager._tcf_enclave',
    module_files,
    swig_opts = ['-c++', '-threads'] + ['-I%s' % i for i in include_dirs],
    extra_compile_args = compile_args,
    libraries = libraries,
    include_dirs = include_dirs,
    library_dirs = library_dirs,
    define_macros = [
                        ('_UNTRUSTED_', 1),
                        ('TCF_DEBUG_BUILD', debug_flag),
                        ('SGX_SIMULATOR', SGX_SIMULATOR_value)
                    ],
    undef_macros = ['NDEBUG', 'EDEBUG']
    )

## -----------------------------------------------------------------
version = subprocess.check_output(
    os.path.join(tcf_root_dir, 'bin/get_version')).decode('ascii').strip()

setup(name='tcf_enclave_manager',
      version = version,
      description = 'Trusted Compute Framework SGX Enclave Manager',
      author = 'Intel',
      url = 'http://www.intel.com',
      packages = find_packages(),
      #namespace_packages=[''],
      install_requires = [
          'colorlog',
          'requests',
          'toml',
          'twisted'
          ],
      ext_modules = [
          enclave_module
      ],
      data_files = [],
      entry_points = {}
)
