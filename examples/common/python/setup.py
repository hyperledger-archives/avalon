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
# ------------------------------------------------------------------------------

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

tcf_root_dir = os.environ.get('TCF_HOME', '../../..')

version = subprocess.check_output(
    os.path.join(tcf_root_dir, 'bin/get_version')).decode('ascii').strip()

openssl_cflags = subprocess.check_output(['pkg-config', 'openssl', '--cflags']).decode('ascii').strip().split()
openssl_include_dirs = list(
    filter(None, re.split('\s*-I', subprocess.check_output(['pkg-config', 'openssl', '--cflags-only-I']).decode('ascii').strip())))
openssl_libs = list(
    filter(None, re.split('\s*-l', subprocess.check_output(['pkg-config', 'openssl', '--libs-only-l']).decode('ascii').strip())))
openssl_lib_dirs = list(
    filter(None, re.split('\s*-L', subprocess.check_output(['pkg-config', 'openssl', '--libs-only-L']).decode('ascii').strip())))

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
    os.path.join(tcf_root_dir, 'tc/sgx/common/crypto'),
    os.path.join(tcf_root_dir, 'tc/sgx/common'),
    os.path.join(os.environ['SGX_SDK'],"include"),
] + openssl_include_dirs

library_dirs = [
    os.path.join(tcf_root_dir, "tc/sgx/common/build"),
    os.path.join(os.environ['SGX_SDK'], 'lib64'),
    os.path.join(os.environ['SGX_SSL'], 'lib64'),
    os.path.join(os.environ['SGX_SSL'], 'lib64', 'release')
] + openssl_lib_dirs

libraries = [
    'utcf-common'
] + openssl_libs


libraries.append('sgx_usgxssl')
libraries = libraries + openssl_libs

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

## -----------------------------------------------------------------
setup(
    name = 'tcf_examples_common',
    version = version,
    description = 'Common library',
    author = 'Intel',
    url = 'http://www.intel.com',
    packages = find_packages(),
    install_requires = [],
    ext_modules=[crypto_module],
    data_files=[],
    entry_points = {})

