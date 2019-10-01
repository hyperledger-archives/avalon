<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->
# Building Trusted Compute Framework

In order to build, install, and run Hyperledger Trusted Compute Framework
(TCF), a number of additional components must be installed and configured.
The following instructions will guide you through the installation and build
process for Hyperledger Trusted Compute Framework.

You have a choice of [Docker-based build](#dockerbuild)
or a [Standalone-based build](#standalonebuild).
The Docker-based build is recommended.

## Table of Contents

- [Docker-based Build and Execution](#dockerbuild)
- [Standalone Build](#standalonebuild)
    - [Prerequisites](#prerequisites)
    - [Installing TCF Using Scripts](#installtcf)
- [Testing](#testing)
    - [Troubleshooting](#troubleshooting)
    - [Troubleshooting: Standalone Build](#troubleshootingstandalone)

# <a name="dockerbuild"></a>Docker-based Build and Execution
Follow the instructions below to execute a Docker-based build and execution.

1. Install Docker Engine and Docker Compose, if not already installed.
   See [PREREQUISITES](PREREQUISITES.md#docker) for instructions
2. Build and run the Docker image from the top-level directory of your
   `trusted-compute-framework` source repository.

   **Intel SGX Simulator mode (for hosts without Intel SGX)**:
   1. Run `sudo docker-compose up --build`
   2. For the subsequent builds on the same workspace, build time can be
      reduced by executing this command:
      `MAKECLEAN=0 sudo -E docker-compose up`

   **SGX Hardware mode (for hosts with Intel SGX)**:
   1. Refer to Intel SGX in Hardware-mode section in
      [PREREQUISITES document](PREREQUISITES.md) to install SGX pre-requisites
      and to configure IAS keys.
   2. Run `sudo docker-compose -f docker-compose-sgx.yaml up --build`
   3. For the subsequent builds on the same workspace, build time can be
      reduced by executing this command:
      `MAKECLEAN=0 sudo -E docker-compose -f docker-compose-sgx.yaml up`
3. On a successful run, you should see the message `BUILD SUCCESS`
4. Open a Docker container shell using following command
   `sudo docker exec -it tcf bash`
5. Activate a Python virtual environment in the Docker shell using following
   command from the Docker working directory, `$TCF_HOME/tools/build`,
   which is set in the `docker-compose.yaml` file:
   ```
   source _dev/bin/activate
   ```
   If the virtual environment for the current shell session is activated,
   you will the see this prompt: `(_dev)`
7. To execute test cases refer to [Testing](#testing) section below
7. To exit the TCF program, press `Ctrl-c`


# <a name="standalonebuild"></a>Standalone Build
## <a name="prerequisites"></a>Standalone: Prerequisites
Follow the [PREREQUISITES document](PREREQUISITES.md) to install and configure
components on which TCF depends.

## <a name="installtcf"></a>Standalone: Installing TCF Using Scripts
This section describes how to get started with TCF quickly using provided
scripts to compile and install TCF.

First, make sure environment variables are set as described in the
[PREREQUISITES document](PREREQUISITES.md).

The steps below will set up a Python virtual environment to install things
into.  Download the TCF source repository if you have not already done this:
```
git clone https://github.com/hyperledger-labs/trusted-compute-framework
cd trusted-compute-framework
```

 Set `TCF_HOME` to the top level directory of your
`trusted-compute-framework` source repository.
You will need these environment variables set in every shell session
where you interact with TCF.
Append this line (with `pwd` expanded) to your login shell script (`~/.bashrc` or similar):
```
export TCF_HOME=`pwd`
echo "export TCF_HOME=$TCF_HOME" >> ~/.bashrc
```

Change to the quickstart build directory:
```
cd $TCF_HOME/tools/build
```

Check that these variables are set before building the code:
`SGX_DEBUG`, `SGX_MODE`, `SGX_SSL`.
If `SGX_MODE` is `HW`, also check that `TCF_ENCLAVE_CODE_SIGN_PEM` is set.
Refer to the [PREREQUISITES document](PREREQUISITES.md)
for more details on the above variables.

Build the Python virtual environment and install TCF components into it:
```
sudo make clean
make
```

Activate the new Python virtual environment for the current shell session.
You will need to do this in each new shell session (in addition to
exporting environment variables).
```
source _dev/bin/activate
```
If the virtual environment for the current shell session is activated,
you will the see this prompt: `(_dev)`

# <a name="testing"></a>Testing

Once the code is successfully built, run the test suite to check that the
installation is working correctly.
Follow these steps to run the `Demo.py` testcase:

**NOTE**: Skip step 1 in the case of Docker-based builds, since
`docker-compose.yaml` will run the TCS startup script.

1. For standalone builds only:
   1. Open a new terminal, Terminal 1
   2. `cd $TCF_HOME/scripts`
   3.  `source $TCF_HOME/tools/build/_dev/bin/activate`
   4. Run `./tcs_startup.sh`
   5. Wait for the listener to start. You should see the message
      `TCS Listener started on port 1947`
   6. To run the Demo test case, open a new terminal, Terminal 2
   7. In Terminal 2, run `source $TCF_HOME/tools/build/_dev/bin/activate`
2. For Docker-based builds:
   1. Follow the steps above for
      ["Docker-based Build and Execution"](#dockerbuild)
   2. Terminal 1 is running `docker-compose` and Terminal 2 is running the
      "tcf" Docker container shell from the previous build steps
3. In Terminal 2, run `cd $TCF_HOME/tests`
4. In Terminal 2, use this command to run the `Demo.py` test:
   ```
   python3 Demo.py --input_dir ./json_requests/ \
           --connect_uri "http://localhost:1947" work_orders/output.json
   ```
5. The response to the TCF listener and Intel&reg; SGX enclave Manager can be
   seen at Terminal 1
6. The response to the test case request can be seen at Terminal 2
7. If you wish to exit the TCF program, press `y` and `Enter` at Terminal 1
   for standalone builds.
   For Docker-based builds, press `Ctrl-c`

A GUI is also available to run this demo.
See [examples/apps/heart_disease_eval](examples/apps/heart_disease_eval)

## <a name="troubleshooting"></a>Troubleshooting
- If you see the message
  `ModuleNotFoundError: No module named '...'`, you did not run
  `source _dev/bin/activate`

## <a name="troubleshootingstandalone"></a>Troubleshooting: Standalone build
- Verify your [environment variables](PREREQUISITES.md#environment)
  are set correctly and the paths exist
- If the Demo test code breaks due to some error, please perform the following
  steps before re-running:
  1. `sudo rm $TCF_HOME/config/Kv*`
  2. `$TCF_HOME/scripts/tcs_startup.sh -t`
  3. You can re-run the test now

- If you see the message `No package 'openssl' found`, you do not have
  OpenSSL libraries or the correct version of OpenSSL libraries.
  See [PREREQUISITES](PREREQUISITES.md#openssl) for installation instructions

- If you see the message
  `ImportError: ...: cannot open shared object file: No such file or directory`,
  then you need to set `LD_LIBRARY_PATH` with:
  `source /opt/intel/sgxsdk/environment` .
  For details, see [PREREQUISITES](PREREQUISITES.md)

