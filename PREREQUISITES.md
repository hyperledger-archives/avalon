<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->
# Trusted Compute Framework Prerequisites
Trusted Compute Framework (TCF) depends on several freely available
software components. These must be installed and configured before
compiling TCF.
This document describes how to get and compile these required components.


# Table of Contents
- [Required Packages](#packages)
- [Environment Variables](#environment)
- [Intel&reg; Software Guard Extensions (Intel SGX)](#sgx)
- [OpenSSL](#openssl)
- [Intel SGX OpenSSL](#sgxssl)
- [Troubleshooting Intel SGX OpenSSL Installation](#troubleshooting)


# Recommended host system
The recommended host-system configuration for Trusted Compute Framework is to
separate the Trusted Compute Framework components from the Sawtooth components.
This means (at least) two different physical systems if using
Intel&reg; SGX-enabled hardware.
If running in Intel SGX simulation mode, this could be two virtual machines or
containers.

Sawtooth (and the TCF transaction processors for Sawtooth) should be run on
Ubuntu 18.04.
Trusted Compute Framework services (specifically the enclave service, provisioning
service, and the client) should be run on Ubuntu 18.04. TCF has been tested on
Ubuntu 18.04.

Sawtooth and TCF may run on other Linux distributions, but the installation
process is likely to be more complicated, and the use of other distributions is
not supported by their respective communities at this time.


# <a name="environment"></a>Environment Variables
Summary of all environment variables required to build Trusted Compute Framework.
Follow the instructions in the remainder of this document to install
and configure these components.

- `SGX_SDK`, `PATH`, `PKG_CONFIG_PATH`, and `LD_LIBRARY_PATH`
These are used to find the Intel Software Guard Extensions (SGX) Software
Development Kit (SDK). They are normally set by sourcing the SGX SDK activation
script (e.g. `source /opt/intel/sgxsdk/environment`)

- `PKG_CONFIG_PATH` and `LD_LIBRARY_PATH` also contain the the path to
  [OpenSSL](#openssl) package config files and libraries, respectively,
  if you build your own OpenSSL. You need to do this when OpenSSL version 1.1.0h
  or later is not available

- `SGX_MODE`
This variable is used to switch between SGX simulator and hardware mode.
Set `SGX_MODE` to either `HW` or `SIM`.

- `SGX_SSL`
Used to locate an SGX-compatible version of OpenSSL

- `TCF_ENCLAVE_CODE_SIGN_PEM`
This needs to be set to a valid enclave signing key. You can generate one
yourself using OpenSSL, then export the path to it:
  ```
  openssl genrsa -3 -out private_rsa_key.pem 3072
  export TCF_ENCLAVE_CODE_SIGN_PEM=$PWD/private_rsa_key.pem
  ```

- `TCF_HOME`
Used to locate the top level build directory.
It is described in the [BUILD document](BUILD.md#buildtcf).


# <a name="packages"></a>Required Packages
On a minimal Ubuntu system, the following packages are required. Other
distributions will require similar packages.
```
sudo apt-get update
sudo apt-get install -y cmake swig pkg-config python3-dev python3-venv python \
     software-properties-common virtualenv curl xxd git unzip dh-autoreconf \
     ocaml ocamlbuild liblmdb-dev
```


# <a name="protobuf"></a>Protobuf Compiler
Many components of the project use Google's Protocol Buffers (including SGX),
so installing support for them early is recommended. Protobuf v3 or later
support is required - check your package manager first to see what is
available.
On Ubuntu 18 or greater, install package `protobuf-compiler`
and verify it supports Protobuf v3 or later:

```
sudo apt-get update
sudo apt-get install -y protobuf-compiler
protoc --version
```

If a Protobuf v3 package is not available, follow these steps to compile and
install protobuf tools manually to `/usr/local`:

```
wget https://github.com/google/protobuf/releases/download/v3.5.1/protobuf-python-3.5.1.tar.gz
tar -xzf protobuf-python-3.5.1.tar.gz
cd protobuf-3.5.1
./configure
make
make check
sudo make install
sudo ldconfig
```

# <a name="sgx"></a>Intel&reg; Software Guard Extensions (Intel SGX)
Hyperledger Trusted Compute Framework is intended to be run on
Intel&reg; SGX-enabled platforms. However, it can also be run in "simulator mode"
on platforms that do not have hardware support for Intel SGX.


## Intel SGX SDK
The Intel SGX SDK is required for both Intel SGX platforms and
Intel SGX simulator mode.
Download the Intel SGX SDK 2.3.1 from
[here](https://01.org/intel-software-guard-extensions/downloads)
for your distribution.
It is recommended to install Intel SGX SDK in `/opt/intel/sgxsdk/`
because the Intel SGX OpenSSL library expects the Intel SGX SDK in this location
by default. Type the following to install Intel SGX SDK
(replace `/var/tmp` with your download directory):
```
sudo mkdir -p /opt/intel
cd /opt/intel
sudo bash /var/tmp/sgx_linux_x64_sdk_*.bin
```

This will install the Intel SGX SDK in the recommended location, `/opt/intel/sgxsdk` .
Source the SGX SDK activation script to set
`$SGX_SDK`, `$PATH`, `$PKG_CONFIG_PATH`, and `$LD_LIBRARY_PATH`:
```
source /opt/intel/sgxsdk/environment
```

To learn more about Intel SGX read the
[Intel SGX SDK documentation](https://software.intel.com/en-us/sgx-sdk/documentation) or
visit the [Intel SGX homepage](https://software.intel.com/en-us/sgx).


## Intel SGX in Hardware Mode
If you plan to run this on Intel SGX-enabled hardware, you will need
to install packages `libsgx-enclave-common` and `libelf-dev` and
install the Intel SGX driver for both standalone and docker builds.
Additionally for standalone builds, we need to install Intel SGX SDK manually.

Steps to install above packages are as follows.

### Remove Old `/dev/sgx` SGX Driver
If device file `/dev/sgx` is present, remove the old driver:
```
sudo /opt/intel/sgxdriver/uninstall.sh
```

If the `uninstall.sh` script is missing, uninstall as follows:
```
sudo service aesmd stop
sudo rm -f $(find /lib/modules -name intel_sgx.ko)
sudo /sbin/depmod
sudo sed -i '/^intel_sgx$/d' /etc/modules
sudo rm -f /etc/sysconfig/modules/intel_sgx.modules
sudo rm -f /etc/modules-load.d/intel_sgx.conf
```

After uninstalling, reboot with `sudo shutdown -r 0`

### Install New `/dev/isgx` SGX Driver
Install `SGX driver` 2.3.1 version
```
wget https://download.01.org/intel-sgx/linux-2.3.1/ubuntu18.04/sgx_linux_x64_driver_4d69b9c.bin
chmod +x sgx_linux_x64_driver_4d69b9c.bin
sudo ./sgx_linux_x64_driver_4d69b9c.bin
```

If installation of driver fails due to absence of `libelf-dev` package on the host system,
install it using below command.
```
sudo apt-get install libelf-dev
```

Install `libsgx-enclave-common` 2.3.1 version
```
wget https://download.01.org/intel-sgx/linux-2.3.1/ubuntu18.04/libsgx-enclave-common_2.3.101.46683-1_amd64.deb
sudo dpkg -i libsgx-enclave-common_2.3.101.46683-1_amd64.deb
```

You will need to obtain Intel IAS subscription key and SPID from the portal
https://api.portal.trustedservices.intel.com/

Replace the SPID and IAS Subscription key values in file
`$TCF_HOME/config/tcs_config.toml` with the actual hexadecimal values
(the IAS key may be either your or Primary key or Secondary key).

Also, either update the `https_proxy` line, if you are behind a
corporate proxy, otherwise comment out the `https_proxy` line:
```
spid = '<spid obtained from portal>'
ias_api_key = '<ias subscription key obtained from portal>'

#https_proxy = "http://your-proxy:your-port/"

```

**The following steps apply only to standalone builds.**

Finally, make sure you have the `SGX_SDK` and `LD_LIBRARY_PATH` environment variables
active for your current shell session before continuing. They are normally set
by sourcing the Intel SGX SDK activation script
(e.g. `source /opt/intel/sgxsdk/environment`).

Set `SGX_MODE` as follows:

```
export SGX_MODE=HW
```


## Intel SGX in Simulator-mode
If running only in simulator mode (no hardware support), you only
need the Intel SGX SDK.

Set `SGX_MODE` as follows:

```
export SGX_MODE=SIM
```

# <a name="openssl"></a>OpenSSL

**The OpenSSL steps apply only to standalone builds.**

OpenSSL is a popular cryptography library. This project requires OpenSSL
version 1.1.0h or later.

Many Linux distributions have an older version of OpenSSL installed by default.
If your version of OpenSSL is too old, follow these steps to compile a newer
version from source. If you already have a newer version, 1.1.0h or later,
you can skip this.

If using a Debian-based Linux distribution (Ubuntu, Mint, etc.) the recommended
path is to download and install pre-build OpenSSL packages for your system. Check
for available versions [here](http://http.us.debian.org/debian/pool/main/o/openssl/).
For example, to install OpenSSL v1.1.0h on an Ubuntu system:
```
wget 'http://http.us.debian.org/debian/pool/main/o/openssl/libssl1.1_1.1.0h-4_amd64.deb'
wget 'http://http.us.debian.org/debian/pool/main/o/openssl/libssl-dev_1.1.0h-4_amd64.deb'
sudo dpkg -i libssl1.1_1.1.0h-4_amd64.deb
sudo dpkg -i libssl-dev_1.1.0h-4_amd64.deb
sudo apt-get install -f
dpkg -l libssl1.1 libssl-dev
```

If you are unable to locate a suitable precompiled package for your system you
can build OpenSSL from source using the following commands. If you installed
the package directly as described above you do *not* need to do this. These
steps detail installing OpenSSL to the `install` directory under your current
working directory.
```
wget https://www.openssl.org/source/openssl-1.1.0h.tar.gz
tar -xzf openssl-1.1.0h.tar.gz
cd openssl-1.1.0h/
mkdir ../install
./Configure --prefix=$PWD/../install
./config --prefix=$PWD/../install
THREADS=8
make -j$THREADS
make test
make install -j$THREADS
cd ..
```

If the above succeeds, define/extend the `PKG_CONFIG_PATH` environment variable
accordingly, e.g.,
```
export PKG_CONFIG_PATH="$PWD/install/lib/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
```
If you installed in a standard location (e.g., default `/usr/local/lib`), run `ldconfig` .
If you installed in a non-standard location, extend `LD_LIBRARY_PATH`, e.g.,
```
export LD_LIBRARY_PATH="$PWD/install/lib/${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
```

# <a name="sgxssl"></a>Intel SGX OpenSSL

**The Intel SGX OpenSSL steps apply only to standalone builds.**

Intel SGX OpenSSL is a compilation of OpenSSL specifically for use with
Intel SGX secure enclaves.
This project specifically requires Intel SGX OpenSSL based on OpenSSL version 1.1.0h
or later. It should match the version installed on your host system or set up
in the previous step.

Follow these steps to compile and install Intel SGX SSL. Note that if you run into
trouble there is a [troubleshooting](#troubleshooting) section specifically for
Intel SGX OpenSSL with fixes for commonly encountered problems.
- Ensure you have the Intel SGX SDK environment variables activated for the
  current shell session
  ```
  source /opt/intel/sgxsdk/environment
  ```

- Create a new directory to build the sgxssl components
  ```
  mkdir ~/sgxssl
  cd ~/sgxssl
  ```

- Download the latest SGX SSL git repository for your version of OpenSSL:

  If you are using OpenSSL 1.1.0 (the usual case):
  ```
  git clone -b openssl_1.1.0 'https://github.com/intel/intel-sgx-ssl.git'
  ```

  If you are using the newer OpenSSL 1.1.1:
  ```
  git clone 'https://github.com/intel/intel-sgx-ssl.git'
  ```

- Download the OpenSSL source package for your version of OpenSSL.
  This will form the base of this Intel SGX SSL install:

  If you are using OpenSSL 1.1.0 (the usual case):
  ```
  cd intel-sgx-ssl/openssl_source
  wget 'https://www.openssl.org/source/openssl-1.1.0h.tar.gz'
  cd ..
  ```

  If you are using the newer OpenSSL 1.1.1:
  ```
  cd intel-sgx-ssl/openssl_source
  wget 'https://www.openssl.org/source/openssl-1.1.1b.tar.gz'
  cd ..
  ```

- Compile and install the sgxssl project.
  Environment variable `SGX_MODE` must be set to `SIM` or `HW` .
  ```
  cd Linux
  make DESTDIR=/opt/intel/sgxssl all test
  sudo make install
  cd ../..
  ```

- Export the `SGX_SSL` environment variable to enable the build utilities to
  find and link this library.
  Consider adding this to your login shell script (`~/.bashrc` or similar)
  ```
  export SGX_SSL=/opt/intel/sgxssl
  ```

## <a name="troubleshooting"></a>Troubleshooting Intel SGX OpenSSL Installation
- Verify your [environment variables](#environment) are set correctly and the paths exist
- If you get the error:
  `./test_app/TestApp: error while loading shared libraries: libprotobuf.so.9: cannot open shared object file: No such file or directory`
  you may not have libprotobuf installed. You can install it via:
  ```
  sudo apt-get update
  sudo apt-get install libprotobuf-dev
  ```
- If you still get the above error about libprotobuf.so.9, your distribution
  may not include the .so.9 version of libprotobuf. You can work around this by simply
  creating a symbolic link to the current version like:
  ```
  cd /usr/lib/x86_64-linux-gnu/
  sudo ln -s libprotobuf.so.10 libprotobuf.so.9
  ```
- If you installed libprotobuf in a standard location (e.g., `/usr/local/lib`), run `ldconfig` .
  If you installed libprotobuf elsewhere, add the directory to `LD_LIBRARY_PATH`
- If you get the error:
  `crypto/rand/rand_lib.c:14:10: fatal error: internal/rand_int.h: No such file or directory`
  you are using OpenSSL 1.1.0 and need to clone the `openssl_1.1.0` branch of `intel-sgx-ssl` in the step above

