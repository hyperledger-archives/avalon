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
import re

# this should only be run with python3
import sys
if sys.version_info[0] < 3:
    print('ERROR: must run with python3')
    sys.exit(1)

from setuptools import setup, find_packages, Extension

tcf_root_dir = os.environ.get('TCF_HOME', '../../../../')
script_dir = os.path.dirname(os.path.realpath(__file__))
enclave_dir = os.path.realpath(os.path.join(tcf_root_dir, 'tcs/core/tcs_trusted_worker_manager/enclave'))

log_dir = os.path.join(tcf_root_dir, "logs")

openssl_cflags = subprocess.check_output(['pkg-config', 'openssl', '--cflags']).decode('ascii').strip().split()
openssl_include_dirs = list(
    filter(None, re.split('\s*-I', subprocess.check_output(['pkg-config', 'openssl', '--cflags-only-I']).decode('ascii').strip())))
openssl_libs = list(
    filter(None, re.split('\s*-l', subprocess.check_output(['pkg-config', 'openssl', '--libs-only-l']).decode('ascii').strip())))
openssl_lib_dirs = list(
    filter(None, re.split('\s*-L', subprocess.check_output(['pkg-config', 'openssl', '--libs-only-L']).decode('ascii').strip())))

module_path = 'tcs/core/tcs_trusted_worker_manager/enclave_wrapper'
module_src_path = os.path.join(tcf_root_dir, module_path)

sgx_mode_env = os.environ.get('SGX_MODE', None)
if not sgx_mode_env or (sgx_mode_env != "SIM" and sgx_mode_env != "HW"):
    print("error: SGX_MODE value must be HW or SIM, current value is: ", sgx_mode_env)
    sys.exit(2)

data_files = [
    (log_dir, []),
    ("tcs/core/tcs_trusted_worker_manager/enclave_wrapper", [module_src_path + "/tcf_enclave_internal.py"]),
    ('lib', [ os.path.join(enclave_dir, 'deps/bin/libtcf-enclave.signed.so')]),
]

ext_deps = [
     ('lib', [ os.path.join(script_dir, '../../core/enclave/deps/bin/libtcf-enclave.signed.so')])
]

## -----------------------------------------------------------------
## set up the enclave
## -----------------------------------------------------------------
debug_flag = os.environ.get('TCF_DEBUG_BUILD',0)

compile_args = [
    '-std=c++11',
    '-Wno-switch',
    '-Wno-unused-function',
    '-Wno-unused-variable',
]


# by default the extension class adds '-O2' to the compile
# flags, this lets us override since these are appended to
# the compilation switches
if debug_flag :
    compile_args += ['-g']

include_dirs = [
    module_src_path,
    os.path.join(tcf_root_dir, 'tcs/core/common/crypto'),
    os.path.join(tcf_root_dir, 'tcs/core/common'),
    os.path.join(module_src_path, 'build'),
    os.path.join(os.environ['SGX_SDK'],"include"),
    os.path.join(tcf_root_dir, 'tcs/core/common/packages/db_store'),
    os.path.join(tcf_root_dir, 'tcs/core/common/packages/base64')
] + openssl_include_dirs

library_dirs = [
    os.path.join(tcf_root_dir, "tcs/core/tcs_trusted_worker_manager/enclave/build/lib"),
    os.path.join(tcf_root_dir, "tcs/core/common/build"),
    os.path.join(os.environ['SGX_SDK'], 'lib64'),
    os.path.join(os.environ['SGX_SSL'], 'lib64'),
    os.path.join(os.environ['SGX_SSL'], 'lib64', 'release')
] + openssl_lib_dirs

libraries = [
    'utcf-common',
    'tcf-enclave',
    'utcf-lmdb-store',
    'lmdb'
] + openssl_libs

if sgx_mode_env == "HW":
    libraries.append('sgx_urts')
    libraries.append('sgx_uae_service')
    SGX_SIMULATOR_value = '0'
if sgx_mode_env == "SIM":
    libraries.append('sgx_urts_sim')
    libraries.append('sgx_uae_service_sim')
    SGX_SIMULATOR_value = '1'

libraries.append('sgx_usgxssl')
libraries = libraries + openssl_libs

module_files = [
    os.path.join(module_src_path, 'tcf_enclave_internal.i'),
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
    os.path.join(tcf_root_dir, 'tcs/core/common/packages/db_store/lmdb_store.cpp')
]

crypto_modulefiles = [
    "crypto/crypto.i"
]

crypto_module = Extension(
    'crypto._crypto',
    crypto_modulefiles,
    swig_opts=['-c++'] + openssl_cflags + ['-I%s' % i for i in include_dirs],
    extra_compile_args=compile_args,
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=libraries)


enclave_module = Extension(
    'tcs.core.tcs_trusted_worker_manager.enclave_wrapper._tcf_enclave_internal',
    module_files,
    swig_opts = ['-c++', '-threads'],
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
## -----------------------------------------------------------------
version = subprocess.check_output(
    os.path.join(tcf_root_dir, 'bin/get_version')).decode('ascii').strip()

setup(name='tcf_crypto_library',
      version=version,
      description='Common library for private objects',
      author='Intel Labs',
      packages=find_packages(),
      install_requires=[],
      data_files=[],
      #namespace_packages=[''],
      ext_modules=[crypto_module],
      entry_points={}
      )

setup(name='tcf_eservice',
      version = version,
      description = 'Trusted Compute Framework SGX Worker',
      author = 'Hyperledger',
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
      data_files = data_files,
      entry_points = {}
)
