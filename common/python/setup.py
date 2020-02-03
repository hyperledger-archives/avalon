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

from setuptools import setup, find_packages, Extension

# this should only be run with python3
import sys
if sys.version_info[0] < 3:
    print('ERROR: must run with python3')
    sys.exit(1)


tcf_root_dir = os.environ.get('TCF_HOME', '../..')

version = subprocess.check_output(
    os.path.join(tcf_root_dir, 'bin/get_version')).decode('ascii').strip()

openssl_cflags = subprocess.check_output(
    ['pkg-config', 'openssl', '--cflags']).decode('ascii').strip().split()
openssl_include_dirs = list(
    filter(None, re.split('\s*-I',
           subprocess.check_output(
               ['pkg-config', 'openssl', '--cflags-only-I'])
               .decode('ascii').strip())))
openssl_libs = list(
    filter(None, re.split('\s*-l',
           subprocess.check_output(['pkg-config', 'openssl', '--libs-only-l'])
           .decode('ascii').strip())))
openssl_lib_dirs = list(
    filter(None, re.split('\s*-L',
           subprocess.check_output(['pkg-config', 'openssl', '--libs-only-L'])
           .decode('ascii').strip())))

compile_args = [
    '-std=c++11',
    '-Wno-switch',
    '-Wno-unused-function',
    '-Wno-unused-variable',
]


crypto_include_dirs = [
    os.path.join(tcf_root_dir, 'common/cpp'),
    os.path.join(tcf_root_dir, 'common/cpp/crypto'),
] + openssl_include_dirs

verify_report_include_dirs = [
    os.path.join(tcf_root_dir, 'common/cpp'),
    os.path.join(tcf_root_dir, 'common/cpp/verify_ias_report'),
]

library_dirs = [
    os.path.join(tcf_root_dir, "common/cpp/build"),
] + openssl_lib_dirs

libraries = [
    'uavalon-common',
    'uavalon-base64',
    'uavalon-parson',
    'uavalon-crypto',
    'uavalon-verify-ias-report'
] + openssl_libs

libraries = libraries + openssl_libs

crypto_modulefiles = [
    "crypto_utils/crypto/crypto.i"
]

crypto_module = Extension(
    'crypto_utils.crypto._crypto',
    crypto_modulefiles,
    swig_opts=['-c++'] + openssl_cflags +
    ['-I%s' % i for i in crypto_include_dirs],
    extra_compile_args=compile_args,
    include_dirs=crypto_include_dirs,
    library_dirs=library_dirs,
    libraries=libraries)

verify_report_modulefiles = [
    "crypto_utils/verify_report/verify_report.i"
]

verify_report_module = Extension(
    'crypto_utils.verify_report._verify_report',
    verify_report_modulefiles,
    swig_opts=['-c++'] + ['-I%s' % i for i in verify_report_include_dirs],
    extra_compile_args=compile_args,
    include_dirs=verify_report_include_dirs,
    library_dirs=library_dirs,
    libraries=libraries)

# -----------------------------------------------------------------
setup(
    name='avalon_common',
    version=version,
    description='Common library',
    author='Hyperledger Avalon',
    url='https://github.com/hyperledger/avalon',
    packages=find_packages(),
    install_requires=[],
    ext_modules=[crypto_module, verify_report_module],
    data_files=[],
    entry_points={})
