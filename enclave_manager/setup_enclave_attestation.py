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
swig_file_path = os.path.join(tcf_root_dir,
         'enclave_manager/avalon_enclave_manager/attestation')

# If enclave_type is not set then default to singleton
enclave_type =  os.environ.get('ENCLAVE_TYPE', 'singleton').lower()

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
    enclave_bridge_path,
    swig_file_path,
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

libraries = []

if enclave_type == "kme":
    module_name = 'enclave_info_kme'
    libraries.append('avalon-kme-enclave-bridge')
elif enclave_type == "wpe":
    module_name = 'enclave_info_wpe'
    libraries.append('avalon-wpe-enclave-bridge')
elif enclave_type == "singleton":
    module_name = 'enclave_info_singleton'
    libraries.append('avalon-singleton-enclave-bridge')
else:
    print('Unsupported enclave type passed in the config %s', enclave_type)
    sys.exit(1)

lib_name = 'avalon_enclave_manager.attestation._' + module_name
swig_file_name = os.path.join(tcf_root_dir,
        'enclave_manager/avalon_enclave_manager/attestation/' \
        + module_name + '.i')

# Target wheel package name
whl_package_name = enclave_type + '_enclave_manager_attestation'

enclave_info_module_files = [
    swig_file_name,
    os.path.join(enclave_bridge_wrapper_path, 'swig_utils.cpp'),
    os.path.join(enclave_bridge_wrapper_path, 'enclave_info.cpp'),
]

enclave_info_module = Extension(
    lib_name,
    enclave_info_module_files,
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

setup(name = whl_package_name,
      version = version,
      description = 'Avalon Enclave Attestation Package',
      author = 'Hyperledger Avalon',
      url = 'https://github.com/hyperledger/avalon',
      packages = find_packages(),
      install_requires = [
          'requests'
          ],
      ext_modules = [
          enclave_info_module
      ],
      data_files = [],
      entry_points = {
          }
)
