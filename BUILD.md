<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->
# Building Hyperledger Avalon

In order to build, install, and run Hyperledger Avalon
a number of additional components must be installed and configured.
The following instructions will guide you through the installation and build
process for Hyperledger Avalon.

You have a choice of [Docker-based build](#dockerbuild)
or a [Standalone-based build](#standalonebuild).
The Docker-based build is recommended.

## Table of Contents

- [Docker-based Build and Execution](#dockerbuild)
- [Standalone Build](#standalonebuild)
    - [Prerequisites](#prerequisites)
    - [Installing Avalon Using Scripts](#install)
- [Testing](#testing)
    - [Static Analysis](#staticanalysis)
    - [Troubleshooting](#troubleshooting)
    - [Troubleshooting: Standalone Build](#troubleshootingstandalone)

# <a name="dockerbuild"></a>Docker-based Build and Execution
Follow the instructions below to execute a Docker-based build and execution.

1. Install Docker Engine and Docker Compose, if not already installed.
   See [PREREQUISITES](PREREQUISITES.md#docker) for instructions
2. Build and run the Docker image from the top-level directory of your
   `avalon` source repository.

   **Intel SGX Simulator mode (for hosts without Intel SGX)**:
   1. Run `sudo docker-compose up --build`
   2. For subsequent runs on the same workspace, if you changed a
      source or configuration file, run the above command again
   3. For subsequent runs on the same workspace, if you did not make any
      changes, startup and build time can be reduced by running:
      `MAKECLEAN=0 sudo -E docker-compose up`

   **SGX Hardware mode (for hosts with Intel SGX)**:
   1. Refer to Intel SGX in Hardware-mode section in
      [PREREQUISITES document](PREREQUISITES.md) to install Intel SGX
      pre-requisites and to configure IAS keys.
   2. Run `sudo docker-compose -f docker-compose-sgx.yaml up --build`
   3. For subsequent runs on the same workspace, if you changed a
      source or configuration file, run the above command again
   4. For subsequent runs on the same workspace, if you did not make any
      changes, startup and build time can be reduced by running:
      `MAKECLEAN=0 sudo -E docker-compose -f docker-compose-sgx.yaml up`
3. On a successful run, you should see the message `BUILD SUCCESS`
   followed by a repetitive message `Enclave manager sleeping for 10 secs`
4. Open a Docker container shell using following command
   `sudo docker exec -it avalon-shell bash`
5. To execute test cases refer to [Testing](#testing) section below
6. To exit the Avalon program, press `Ctrl-c`


# <a name="standalonebuild"></a>Standalone Build
## <a name="prerequisites"></a>Standalone: Prerequisites
Follow the [PREREQUISITES document](PREREQUISITES.md) to install and configure
components on which Hyperledger Avalon depends.

## <a name="install"></a>Standalone: Installing Avalon Using Scripts
This section describes how to get started with Avalon quickly using provided
scripts to compile and install Avalon.
The steps below will set up a Python virtual environment to run Avalon.

1. Make sure environment variables are set as described in the
   [PREREQUISITES document](PREREQUISITES.md)

2. Choose whether you want the stable version (recommended) or the most recent
   version

   - To use the current stable branch (recommended), run this command:
     ```bash
     git clone https://github.com/hyperledger/avalon --branch v0.5-pre-release.4
     ```

   - Or, to use the latest branch, run this command:
     ```bash
     git clone https://github.com/hyperledger/avalon
     ```

3. Change to the Avalon source directory
   ```bash
   cd avalon
   ```

4. Set `TCF_HOME` to the top level directory of your
   `avalon` source repository.
   You will need these environment variables set in every shell session
   where you interact with Avalon.
   Append this line (with `pwd` expanded) to your login shell script
   (`~/.bashrc` or similar):
   ```bash
   export TCF_HOME=`pwd`
   echo "export TCF_HOME=$TCF_HOME" >> ~/.bashrc
   ```

5. If you are using Intel SGX hardware, check that `SGX_MODE=HW` before
   building the code.
   If you are not using Intel SGX hardware, check that `SGX_MODE` is not
   set or set to `SGX_MODE=SIM` .
   By default `SGX_MODE=SIM` , indicating use the Intel SGX simulator.

6. If you are not using Intel SGX hardware, go to the next step.
   Check that `TCF_ENCLAVE_CODE_SIGN_PEM` is set.
   Refer to the [PREREQUISITES document](PREREQUISITES.md)
   for more details on these variables.

   You will also need to obtain an Intel IAS subscription key and SPID
   from the portal
   https://api.portal.trustedservices.intel.com/
   Replace the SPID and IAS Subscription key values in file
   `$TCF_HOME/config/tcs_config.toml` with the actual hexadecimal values
   (the IAS key may be either your Primary key or Secondary key):

   ```bash
   spid = '<spid obtained from portal>'
   ias_api_key = '<ias subscription key obtained from portal>'
   ```

7. If you are behind a corporate proxy, then in file
   `$TCF_HOME/config/tcs_config.toml` uncomment and update the
   `https_proxy` line:

   ```bash
   #https_proxy = "http://your-proxy:your-port/"
   ```

   If you are not behind a corporate proxy (the usual case),
   then leave this line commented out.

8. Create a Python virtual environment:

   ```bash
   cd $TCF_HOME/tools/build
   python3 -m venv _dev
   ```

9. Activate the new Python virtual environment for the current shell session.
   You will need to do this in each new shell session (in addition to
   exporting environment variables).
   ```bash
   source _dev/bin/activate
   ```

   If the virtual environment for the current shell session is activated,
   you will the see this prompt: `(_dev)`

10. Install PIP3 packages into your Python virtual environment:

    ```bash
    pip3 install --upgrade setuptools json-rpc py-solc-x web3 colorlog twisted wheel toml
    ```

11. Build and install Avalon components:

    ```bash
    make clean
    make
    ```

12. Build the Avalon SDK Python module:

    ```bash
    cd $TCF_HOME/sdk
    make
    make install
    ```

13. Build the shared key/value storage modules:

    ```bash
    cd $TCF_HOME/shared_kv_storage
    make
    make install
    ```

14. Build the Avalon Listener module:

    ```bash
    cd $TCF_HOME/listener
    make
    make install
    ```

# <a name="testing"></a>Testing

Once the code is successfully built, run the test suite to check that the
installation is working correctly.
Follow these steps to run the `Demo.py` testcase:

**NOTE**: Skip step 1 in the case of Docker-based builds, since
`docker-compose.yaml` will run the TCS startup script.

1. For standalone builds only:
   1. Open a new terminal, Terminal 1
   2. `cd $TCF_HOME/scripts`
   3. Run `source $TCF_HOME/tools/build/_dev/bin/activate` .
      You should see the `(_dev)` prompt
   4. Run `./tcs_startup.sh -s` The `-s` option starts 	`kv_storage` before
      other Avalon components.
   5. Wait for the listener to start. You should see the message
      `TCS Listener started on port 1947`,
      followed by a repetitive message `Enclave manager sleeping for 10 secs`
   6. To run the Demo test case, open a new terminal, Terminal 2
   7. In Terminal 2, run `source $TCF_HOME/tools/build/_dev/bin/activate`.
      You should see the `(_dev)` prompt
   8. In Terminal 2, cd to `$TCF_HOME/tests` and
      type this command to run the `Demo.py` test:
      ```bash
      cd $TCF_HOME/tests
      python3 Demo.py --input_dir ./json_requests/ \
         --connect_uri "http://localhost:1947" work_orders/output.json
      ```
2. For Docker-based builds:
   1. Follow the steps above for
      ["Docker-based Build and Execution"](#dockerbuild)
   2. Terminal 1 is running `docker-compose` and Terminal 2 is running the
      "avalon-shell" Docker container shell from the previous build steps
   3. In Terminal 2, cd to `$TCF_HOME/tests` and
      type this command to run the `Demo.py` test:
      ```bash
      cd $TCF_HOME/tests
      python3 Demo.py --input_dir ./json_requests/ \
         --connect_uri "http://avalon-listener:1947" work_orders/output.json
      ```
3. The response to the Avalon listener and Intel&reg; SGX Enclave Manager
   can be seen at Terminal 1
4. The response to the test case request can be seen at Terminal 2
5. If you wish to exit the Avalon program, press `Ctrl-c`

A GUI is also available to run this demo.
See [examples/apps/heart_disease_eval](examples/apps/heart_disease_eval)

## <a name="staticanalysis"></a>Static Analysis
To run lint checks on codebase, execute the following commands -
```
cd $TCF_HOME
docker-compose -f docker-compose-lint.yaml up
```
Above steps would run lint on all modules by defualt. If you want to run lint on selective modules, you need to pass the modules via `LINT_MODULES`. For example -
```
cd $TCF_HOME
LINT_MODULES={sdk,common} docker-compose -f docker-compose-lint.yaml up
```
Module names can be found [here](bin/run_lint#L205) in the codebase.

## <a name="troubleshooting"></a>Troubleshooting
- If you see the message
  `ModuleNotFoundError: No module named '...'`, you did not run
  `source _dev/bin/activate`
  or you did not successfully build Avalon

- If you see the message `CMake Error: The current CMakeCache.txt
  . . . is different than the directory . . . where CMakeCache.txt
   was created.` then the CMakeCache.txt file is out-of-date.
   Remove the file and rebuild.

## <a name="troubleshootingstandalone"></a>Troubleshooting: Standalone build
- Verify your [environment variables](PREREQUISITES.md#environment)
  are set correctly and the paths exist
- If the Demo test code breaks due to some error, please perform the following
  steps before re-running:
  1. `sudo rm $TCF_HOME/config/Kv*`
  2. `$TCF_HOME/scripts/tcs_startup.sh -t -s`
  3. You can re-run the test now

- If you get build errors rerunning `make`, try `sudo make clean` first

- If you see the message `No package 'openssl' found`, you do not have
  OpenSSL libraries or the correct version of OpenSSL libraries.
  See [PREREQUISITES](PREREQUISITES.md#openssl) for installation instructions

- If you see the message
  `ImportError: ...: cannot open shared object file: No such file or directory`,
  then you need to set `LD_LIBRARY_PATH` with:
  `source /opt/intel/sgxsdk/environment` .
  For details, see [PREREQUISITES](PREREQUISITES.md)
