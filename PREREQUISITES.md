<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Hyperledger Avalon Prerequisites

Hyperledger Avalon depends on several freely available
software components. These must be installed and configured before
compiling Avalon.
This document describes how to get and compile these required components.


# Table of Contents
- [Required Packages](#packages)
- [Environment Variables](#environment)
- [Docker](#docker)
- [Intel&reg; Software Guard Extensions (Intel SGX)](#sgx)
- [OpenSSL](#openssl)
- [Intel SGX OpenSSL](#sgxssl)
- [Troubleshooting Intel SGX OpenSSL Installation](#troubleshooting)


# Recommended host system
Hyperledger Avalon services (specifically the enclave manager and
listener) should be ran on Ubuntu 18.04. Avalon has been tested on Ubuntu 18.04.

Avalon may run on other Linux distributions, but the installation
process is likely to be more complicated, and the use of other distributions is
not supported by their respective communities at this time.


# <a name="environment"></a>Environment Variables
Summary of all environment variables required to build
Hyperledger Avalon.
Follow the instructions in the remainder of this document to install
and configure these components.

- `SGX_SDK`, `PATH`, `PKG_CONFIG_PATH`, and `LD_LIBRARY_PATH`
These are used to find the Intel Software Guard Extensions (SGX) Software
Development Kit (SDK). They are normally set by sourcing the Intel SGX SDK
activation script (e.g. `source /opt/intel/sgxsdk/environment`)

- If you build your own OpenSSL (not the usual case),
  `PKG_CONFIG_PATH` and `LD_LIBRARY_PATH` also contain the the path to
  [OpenSSL](#openssl) package config files and libraries, respectively.
  You need to do this when pre-built OpenSSL version 1.1.1d or later
  packages are not available for your system

- `SGX_MODE`
Optional variable used to switch between the Intel SGX simulator and hardware
mode. Set `SGX_MODE` to `HW` (Intel SGX available) or
`SIM` (use Intel SGX simulator). If not set, the default is `SIM` .

- `SGX_SSL`
Optional variable to locate an Intel SGX-compatible version of OpenSSL.
Default directory is `/opt/intel/sgxssl`

- `TCF_ENCLAVE_CODE_SIGN_PEM`
Use only with `SGX_MODE=HW`.
This needs to be set to a valid enclave signing key. You can generate one
yourself using OpenSSL, then export the path to it:
  ```bash
  openssl genrsa -3 -out $TCF_HOME/enclave.pem 3072
  export TCF_ENCLAVE_CODE_SIGN_PEM=$TCF_HOME/enclave.pem
  ```

- `TCF_HOME`
Used to locate the top level Avalon build directory.
It is described in the [BUILD document](BUILD.md#buildtcf)

- `TCF_DEBUG_BUILD`
Optional variable for enabling Avalon debug output. Set to `1` enable.
For example: `export TCF_DEBUG_BUILD=1` for standalone builds
or`TCF_DEBUG_BUILD=1 docker-compose up` for Docker-based builds


# <a name="packages"></a>Required Packages
On a minimal Ubuntu system, Hyperledger Avalon requires the following packages.
Other distributions will require similar packages.
```bash
sudo apt-get update
sudo apt-get install -y cmake swig pkg-config python3-dev python \
     software-properties-common virtualenv curl xxd git unzip dh-autoreconf \
     ocaml ocamlbuild liblmdb-dev protobuf-compiler python3-pip python3-toml \
     python3-requests python3-colorlog python3-twisted
sudo apt-get install -y python3-venv
```

Also, install the following pip3 packages:
```bash
pip3 install --upgrade setuptools json-rpc py-solc web3 colorlog twisted wheel
```

# <a name="docker"></a>Docker
Docker may be used instead of building Hyperledger Avalon directly
(standalone mode) and is recommended.
If you build using Docker, you need to install Docker Engine
and Docker Compose if it is not already installed.

To install Docker CE Engine:

```bash
sudo apt-get install -y apt-transport-https ca-certificates
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce
```

To verify a correct installation, run `sudo docker run hello-world`

To install Docker Compose:
```bash
sudo curl -L \
   https://github.com/docker/compose/releases/download/1.24.1/docker-compose-`uname -s`-`uname -m` \
   -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

To verify a correct installation, run `docker-compose version`

For details on Docker installation, see
https://docs.docker.com/engine/installation/linux/ubuntu
and
https://docs.docker.com/compose/install/#install-compose


# <a name="sgx"></a>Intel&reg; Software Guard Extensions (Intel SGX)
Hyperledger Avalon is intended to be run on
Intel SGX-enabled platforms. However, it can also be run in "simulator mode"
on platforms that do not have hardware support for Intel SGX.
Support for other hardware-based Trusted Execution Environments (TEEs)
can be added by submitting a Pull Request.


## Intel SGX SDK
The Intel SGX SDK is required for both Intel SGX hardware platform and
Intel SGX simulator mode.
The following instructions download the Intel SGX SDK 2.3 and installs it in
`/opt/intel/sgxsdk/` :

```bash
sudo mkdir -p /opt/intel
cd /opt/intel
sudo wget https://download.01.org/intel-sgx/sgx-linux/2.7.1/distro/ubuntu18.04-server/sgx_linux_x64_sdk_2.7.101.3.bin
echo "yes" | sudo bash ./sgx_linux_x64_sdk_2.7.101.3.bin
```

This installs the Intel SGX SDK in the recommended location,
`/opt/intel/sgxsdk` .
The Intel SGX OpenSSL library expects the SDK to be here by default.

After installing, source the Intel SGX SDK activation script to set
`$SGX_SDK`, `$PATH`, `$PKG_CONFIG_PATH`, and `$LD_LIBRARY_PATH`.
Append this line to your login shell script (`~/.bashrc` or similar):
```bash
source /opt/intel/sgxsdk/environment
echo "source /opt/intel/sgxsdk/environment" >>~/.bashrc
```

To learn more about Intel SGX read the
[Intel SGX SDK documentation](https://software.intel.com/en-us/sgx-sdk/documentation)
or visit the [Intel SGX homepage](https://software.intel.com/en-us/sgx).
Downloads are listed at
[Intel SGX Downloads for Linux](https://01.org/intel-software-guard-extensions/downloads).


## Intel SGX in Hardware Mode

If you plan to run this on Intel SGX-enabled hardware, you will need to
install the Intel SGX driver and install additional packages
for both standalone and docker builds.
You need to install the Intel SGX driver whether you build Avalon standalone
or using Docker.

Before installing Intel SGX software, install these packages:
```bash
sudo apt-get install -y libelf-dev cpuid
````

Verify your processor supports Intel SGX with:
`cpuid | grep SGX:`

Verify Intel SGX is enabled in BIOS.
Enter BIOS by pressing the BIOS key during boot.
The BIOS key varies by manufacturer and could be F10, F2, F12, F1, DEL, or ESC.
Usually Intel SGX is disabled by default.
If disabled, enter BIOS and find the Intel SGX feature
(it is usually under the "Advanced" or "Security" menu),
enable Intel SGX, save your BIOS settings, and exit BIOS.

Download and install libsgx-enclave-common version 2.7.101:
```bash
wget https://download.01.org/intel-sgx/sgx-linux/2.7.1/distro/ubuntu18.04-server/libsgx-enclave-common_2.7.101.3-bionic1_amd64.deb
sudo dpkg -i libsgx-enclave-common_2.7.101.3-bionic1_amd64.deb
```

### Run aesm service on host machine
If you are behind a corporate proxy,
uncomment and update the proxy type and aesm proxy lines in /etc/aesmd.conf:  
```
proxy type = manual
aesm proxy = http://your-proxy:your-port
```

Start aesm service on host machine  
```
sudo source /opt/intel/libsgx-enclave-common/aesm/aesm_service
```

### Remove Old `/dev/sgx` Intel SGX DCAP Driver
If device file `/dev/sgx` is present, remove the old DCAP driver:
```bash
sudo /opt/intel/sgxdriver/uninstall.sh
```

If the `uninstall.sh` script is missing or fails, uninstall as follows:
```bash
if [ -c /dev/sgx ] ; then
    sudo service aesmd stop
    sudo rm -f $(find /lib/modules -name intel_sgx.ko)
    sudo /sbin/depmod
    sudo sed -i '/^intel_sgx$/d' /etc/modules
    sudo rm -f /etc/sysconfig/modules/intel_sgx.modules
    sudo rm -f /etc/modules-load.d/intel_sgx.conf
fi
```

After uninstalling, reboot with `sudo shutdown -r 0`

### Install New `/dev/isgx` Intel SGX IAS Driver
Install the Intel SGX IAS driver:

```bash
cd /var/tmp
wget https://download.01.org/intel-sgx/sgx-linux/2.7.1/distro/ubuntu18.04-server/sgx_linux_x64_driver_2.6.0_4f5bb63.bin
sudo bash ./sgx_linux_x64_driver_2.6.0_4f5bb63.bin
```

If installation of the Intel SGX driver fails due to syntax errors,
you may need to install a newer version of a non-DCAP Intel SGX driver
for your version of Linux. See
https://01.org/intel-software-guard-extensions/downloads

**The following steps apply only to standalone builds.**

Finally, make sure you have the `SGX_SDK` and `LD_LIBRARY_PATH` environment
variables active for your current shell session before continuing.
They are normally set by sourcing the Intel SGX SDK activation script
(e.g. `source /opt/intel/sgxsdk/environment`).

Set `SGX_MODE` as follows.
Append this line to your login shell script (`~/.bashrc` or similar):

```bash
export SGX_MODE=HW
echo "export SGX_MODE=HW" >>~/.bashrc
```


## Intel SGX in Simulator-mode
If running only in simulator mode (no hardware support), you only
need the Intel SGX SDK.

`SGX_MODE` is optional. If set, it must be set to `SIM` (the default).
Verify `SGX_MODE` is not set, or is set to `SIM`, with `echo $SGX_MODE` .

# <a name="openssl"></a>OpenSSL

**The OpenSSL steps apply only to standalone builds.**

OpenSSL is a popular cryptography library. This project requires OpenSSL
version 1.1.1d or later.

Many Linux distributions have an older version of OpenSSL installed by default.
If your version of OpenSSL is too old, follow these steps to compile a newer
version from source. If you already have a newer version, 1.1.1d or later,
you can skip this.

If using a Debian-based Linux distribution (Ubuntu, Mint, etc.) the recommended
path is to download and install pre-built OpenSSL packages for your system.
Check for available versions
[here](http://http.us.debian.org/debian/pool/main/o/openssl/).
For example, to install OpenSSL v1.1.1d on an Ubuntu system:

```bash
cd /var/tmp
wget 'http://http.us.debian.org/debian/pool/main/o/openssl/libssl1.1_1.1.1d-2_amd64.deb'
wget 'http://http.us.debian.org/debian/pool/main/o/openssl/libssl-dev_1.1.1d-2_amd64.deb'
sudo dpkg -i libssl1.1_1.1.1d-2_amd64.deb
sudo dpkg -i libssl-dev_1.1.1d-2_amd64.deb
sudo apt-get install -f
```

To verify installation, type `dpkg -l libssl1.1 libssl-dev` .

## Alternate method: OpenSSL Build
If you are unable to locate a suitable pre-compiled package for your system,
you can build OpenSSL from source using the following commands. If you
installed the package directly as described above you do *not* need to do this.
These steps detail installing OpenSSL to the `~/openssl/install` directory.

```bash
mkdir -p ~/openssl/install
cd ~/openssl
wget https://www.openssl.org/source/openssl-1.1.1d.tar.gz
tar -xzf openssl-1.1.1d.tar.gz
cd openssl-1.1.1d/
./Configure --prefix=$PWD/../install
./config --prefix=$PWD/../install
make
make test
make install
cd ../..
```

If the above succeeds, define/extend the `PKG_CONFIG_PATH` environment variable
accordingly, e.g.,
```bash
export PKG_CONFIG_PATH="$PWD/install/lib/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
```
If you installed in a standard location (e.g., default `/usr/local/lib`),
run `ldconfig` .
If you installed in a non-standard location, extend `LD_LIBRARY_PATH`, e.g.,
```bash
export LD_LIBRARY_PATH="$PWD/install/lib/${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
```

# <a name="sgxssl"></a>Intel SGX OpenSSL

**The Intel SGX OpenSSL steps apply only to standalone builds.**

Intel SGX OpenSSL is a compilation of OpenSSL specifically for use with
Intel SGX secure enclaves.
This project specifically requires Intel SGX OpenSSL based on
OpenSSL version 1.1.1d or later.
It should match the version installed on your host system or set up
in the previous step.

Follow these steps to compile and install Intel SGX SSL. Note that if you run
into trouble there is a [troubleshooting](#troubleshooting) section
specifically for Intel SGX OpenSSL with fixes for commonly encountered
problems.
- Ensure you have the Intel SGX SDK environment variables activated for the
  current shell session
  ```bash
  source /opt/intel/sgxsdk/environment
  ```

- Create a new directory to build the sgxssl components
  ```bash
  mkdir ~/sgxssl
  cd ~/sgxssl
  ```

- Download the latest SGX SSL git repository for your version of OpenSSL:

  ```bash
  git clone 'https://github.com/intel/intel-sgx-ssl.git'
  ```

- Download the OpenSSL source package for your version of OpenSSL.
  This will form the base of this Intel SGX SSL install:

  ```bash
  cd intel-sgx-ssl/openssl_source
  wget 'https://www.openssl.org/source/openssl-1.1.1d.tar.gz'
  cd ..
  ```

- Compile and install the sgxssl project.
  Environment variable `SGX_MODE` must be set to `SIM` or `HW` .
  ```bash
  cd Linux
  export SGX_MODE=${SGX_MODE:-SIM}
  make DESTDIR=/opt/intel/sgxssl all test
  sudo make install
  cd ../../..
  ```

- If SGX SSL is not located at the default directory, `/opt/intel/sgxssl`,
  export the `SGX_SSL` environment variable to enable the build utilities to
  find and link this library.
  Append this line to your login shell script (`~/.bashrc` or similar)
  after changing the directory name:
  ```bash
  export SGX_SSL=/opt/intel/sgxssl
  echo "export SGX_SSL=/opt/intel/sgxssl" >>~/.bashrc
  ```

# <a name="troubleshooting"></a>Troubleshooting Installation
- Verify your [environment variables](#environment) are set correctly and the
  paths exist

- If you get the error:
  `./test_app/TestApp: error while loading shared libraries: libprotobuf.so.9:
   cannot open shared object file: No such file or directory`
  you may not have libprotobuf installed. You can install it via:
  ```bash
  sudo apt-get update
  sudo apt-get install -y libprotobuf-dev
  ```
- If you still get the above error about libprotobuf.so.9, your distribution
  may not include the .so.9 version of libprotobuf. You can work around this
  by simply creating a symbolic link to the current version like:
  ```bash
  cd /usr/lib/x86_64-linux-gnu/
  sudo ln -s libprotobuf.so.10 libprotobuf.so.9
  ```
- If you installed libprotobuf in a standard location (e.g., `/usr/local/lib`),
  run `ldconfig` .
  If you installed libprotobuf elsewhere, add the directory to `LD_LIBRARY_PATH`

- If you get the error:
  `crypto/rand/rand_lib.c:14:10: fatal error: internal/rand_int.h:
   No such file or directory`
  you are using an old version of OpenSSL and need to clone the
  `openssl_1.1.1` branch of `intel-sgx-ssl` in the step above

- If you get the error:
  `rand_lib.c:151:16: error: too many arguments to function 'rand_pool_new'`
  you are using an old version of OpenSSL and need to clone the
  `openssl_1.1.1` branch of `intel-sgx-ssl` in the step above

- If you get the error:
  `threads.h:57:22: error: conflicting types for ‘pthread_key_t’` or
  `threads.h:60:13: error: conflicting types for ‘pthread_once_t’`
  your Intel SGX SDK is too old. Remove or rename `/opt/intel/sgxsdk` and `~/sgxssl`
  then reinstall the Intel SGX SDK and rebuild the Intel SGX OpenSSL
  as instructed under [Intel SGX SDK](#sgx) and [Intel SGX OpenSSL](#sgxssl)

- If the message  `intel_sgx: SGX is not enabled` appears in `/var/log/syslog`
  Intel SGX needs to be enabled in BIOS

- If you get the error
  `failed to initialize enclave; . . . ('Cannot connect to proxy.', . . .)`
  check the `https_proxy` line in `$TCF_HOME/config/tcs_config.toml` .
  It needs to be removed or updated, as instructed in the
  [Intel SGX](#sgx) section

- If you get the error `failed to create enclave signup data`,
  check the `ias_api_key` line in `$TCF_HOME/config/tcs_config.toml` .
  It should be either either the Primary key or Secondary key you received
  from your IAS subscription as instructed in the
  [Intel SGX](#sgx) section

- If you are running in Intel SGX hardware mode, make sure you have device
  `/dev/isgx` (and not `/dev/sgx`). Review the Intel SGX device driver
  installation instructions above. If you have `/dev/sgx` the
  device driver must be removed first

- If you are running in Intel SGX hardware mode, you need to modify
  the `ias_api_key` in `config/tcs_config.toml` with your
  IAS Subscription key obtained in the instructions above

- If you are not running in a corporate proxy environment (and not connected
  directly to Internet), comment out the `https_proxy` line in
  `config/tcs_config.toml`

- If you reinstall the Intel SGX SDK and you modified `/etc/aesmd.conf`
  then save and restore the file before installing the SDK.

