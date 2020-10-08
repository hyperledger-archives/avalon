<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Hyperledger Avalon Python Worker for Graphene SGX

## Introduction
* Avalon python worker implementation is based on [EEA Trusted Compute Specification](https://entethalliance.github.io/trusted-computing/spec.html).
* [Graphene Library OS](https://graphene.readthedocs.io/en/latest/index.html) supports running unmodified Linux applications on Intel SGX. A Library OS (or "LibOS") provides an Operating System environment in a user space library to execute an application.
* Avalon python worker supports execution of python workloads inside a docker container (without Intel SGX) and also in Graphene-SGX environment.
* Avalon python worker uses [pycryptodomex](https://pypi.org/project/pycryptodomex/) package for encryption and [ecdsa](https://pypi.org/project/ecdsa/) package for signing and verification.

## Design Assumptions

- Avalon python worker can run as a standalone docker based application and is not dependent on core Avalon framework for building and running the application.
- Avalon python worker consists of generic classes for work order processing , worker encryption, signing and hash calculation. These classes support work order execution based on EEA Trusted Compute Specification v1.1. These functionalities will eventually be part of Avalon Python SDK and once a formal Avalon Python SDK is released, Avalon python based workers can directly use this SDK.
- Avalon python worker and workloads can be run unmodified in Intel SGX using Graphene Library OS.
- Avalon python worker can be easily extended to support additional python workloads.
- Avalon Graphene Enclave Manager and python worker communicates using JSON-RPC via TCP socket. This implementation uses ZMQ socket to send and receive JSON-RPC messages.
- Avalon python worker docker image can be transformed to graphene based docker image using [Graphene Shielded Containers](https://github.com/oscarlab/graphene/blob/master/Documentation/manpages/gsc.rst) (GSC) tool. GSC tool includes the Graphene Library OS, Intel SGX related information, and executes the application inside an Intel SGX enclave.

## Building and Running the worker without Intel SGX

- To build Avalon Python worker run the following command from [python_worker](https://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_worker) directory:

  `docker-compose build`

  This will create docker image *avalon-python-worker-dev*. This image contains Avalon python worker, sample workloads and a test application to send work order to python worker.

### Test python worker using test client (without Avalon)

- To run python worker as a docker container and to use a test application to send work order requests,  execute the following command from [python_worker](http://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_worker) directory.

  `docker-compose up` 

  Above command will run test work orders listed in file [*test_work_orders.json*](http://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_worker/tests/test_work_orders.json).

### Test python worker using Avalon

- To run python worker with Avalon Graphene Enclave Manager, go to Avalon repository top level directory and execute the following command:

  `docker-compose -f docker-compose.yaml -f docker/compose/avalon-graphene.yaml up`

- To send work orders to python worker we can use [generic client](https://github.com/hyperledger/avalon/tree/master/examples/apps/generic_client) application. Execute following commands:

  1. Get into Avalon Shell container : `sudo docker exec -it avalon-shell bash`

  2. `cd /project/avalon/examples/apps/generic_client/`

  3. Send work order request with *"python-hello"* workload id to Graphene worker *"graphene-worker-1"*

     `./generic_client.py --uri "http://avalon-listener:1947" -w "graphene-worker-1" --workload_id "python-hello" --in_data "Krsna" -o`

     If everything goes fine, then you should see following output in stdout:

     *Decryption result at client - Hello Krsna*

## Building and Running the worker in Graphene SGX

- Before building and running application for Graphene-SGX, we need to install Intel SGX driver and Graphene SGX driver.

  - To install Intel SGX driver please refer https://github.com/hyperledger/avalon/blob/master/PREREQUISITES.md#intel-sgx-in-hardware-mode
  - Clone the Graphene codebase from [here](https://github.com/oscarlab/graphene.git) if not done already. Then, to install Graphene SGX driver please refer https://graphene.readthedocs.io/en/latest/building.html#install-the-graphene-sgx-driver-not-for-production.

- To build Avalon Python worker docker image for Graphene-SGX we need to use [Graphene Shielded Container](https://github.com/oscarlab/graphene/tree/master/Tools/gsc) (GSC) tool. Please refer to [GSC tool documentation](https://github.com/oscarlab/graphene/blob/master/Documentation/manpages/gsc.rst) for detailed instructions to create graphene based docker image from application docker image.

- To build graphene based docker image, we need the non-SGX docker image *avalon-python-worker-dev* built earlier and [Graphene manifest files]( https://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_worker/graphene) for python worker.

- To retrieve a valid quote from Graphene-GSX enclave, update the manifest file by providing correct SPID and linkable value in *sgx.ra_client_spid* and *sgx.ra_client_linkable*. You can subscribe SPID from https://api.portal.trustedservices.intel.com/EPID-attestation

- Run the following command from Graphene git repository root directory:

  1. Create GSC build configuration file using following commands :

     `cd Tools/gsc`

     `cp config.yaml.template config.yaml`

     *# Adopt config.yaml to the installed Intel SGX driver and desired Graphene repository.*

     *# Avalon Python worker uses below configuration*.

     ```
     Distro: "ubuntu18.04"
     Graphene:
         Repository: "https://github.com/oscarlab/graphene.git"
         Branch: "master"
     SGXDriver:
         Repository: "https://github.com/01org/linux-sgx-driver.git"
         Branch: "sgx_driver_2.6"
     ```

  2. Copy the Graphene python worker GSC build script file *build_gsc_python_worker.sh* from [here](https://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_worker/graphene) to <graphene_repo>/Tools/gsc using following command :

     `cp <path of build_gsc_python_worker.sh> Tools/gsc`

  3. Set *TCF_HOME* to the top level directory of your avalon source repository.

     `export TCF_HOME=<path of avalon repo top level directory>`

  4. Graphenize Avalon python worker docker image using following command :

     `./build_gsc_python_worker.sh`

  Above command if run successfully will generate a Graphene based docker image *gsc-avalon-python-worker-dev*.

### Test python worker using test client (without Avalon)

- To run python worker as a docker container in Graphene-SGX environment and to use a test application to send work order requests, execute the following command from [python_worker](http://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_worker) directory.

  `docker-compose -f docker-compose.yaml -f compose/graphene-sgx.yaml up`

  Above command will run test work orders listed in file [*test_work_orders.json*](http://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_worker/tests/test_work_orders.json).

### Test python worker using Avalon

- To run python worker in Graphene-SGX with Avalon Graphene Enclave Manager, go to Avalon repository  top level directory and execute the following commands :

  1. Start all the required containers in detached mode.

     `docker-compose -f docker-compose.yaml -f docker/compose/avalon-graphene.yaml -f docker/compose/avalon-graphene-sgx.yaml up -d`

  2. Graphene-SGX Python worker will take around 3 minutes to get ready. Check the logs of graphene python worker using below command

     `docker-compose -f docker-compose.yaml -f docker/compose/avalon-graphene.yaml -f docker/compose/avalon-graphene-sgx.yaml logs -f graphene-python-worker`

     If everything goes fine you should see following log in stdout

     *graphene-python-worker    | Generate worker signing and encryption keys*
     *graphene-python-worker    | Start listening to ZMQ for work orders*
     *graphene-python-worker    | Bind to zmq port*
     *graphene-python-worker    | waiting for next request*

  3. To send work orders to python worker we can use Avalon generic client application as shown [above](https://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_worker#test-python-worker-using-avalon).

  4. To restart the python worker you have to first bring all the containers down before bringing it up again. This is to ensure that python worker generate new keys and Avalon Graphene Enclave Manager gets the updated sign up information from python worker.

     `docker-compose -f docker-compose.yaml -f docker/compose/avalon-graphene.yaml -f docker/compose/avalon-graphene-sgx.yaml down`

## Adding a new Python Workload

- Avalon Python worker supports two sample workloads: "python-hello" and "python-fib".

- List of sample workloads are listed in *workloads.json* file kept in [python_worker](http://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_worker) directory.

  *{*
      *"python-hello": {*
          *"module": "sample_workloads.workload.hello",*
          *"class": "HelloWorkLoad"*
      *},*
      *"python-fib": {*
          *"module": "sample_workloads.workload.fibonacci",*
          *"class": "FibonacciWorkLoad"*
      *}*
  *}*

- Python sample workloads are is kept in [sample_workloads](http://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_worker/sample_workloads) directory.

- To add a new python workload, keep the python workload implementation class in sample workloads directory and also edit the *workloads.json* file to add new workload. The format of workload in *workloads.json* file is as shown below :

  *"workload-id": {*
          *"module": "<workload python module>",*
          *"class": "<workload implementation class name>"*
      *}*

## Testing OpenVino Object detection with Python worker

- First build OpenVino docker image and GSC docker image using the steps mentioned in cppopenvino [ReadMe](https://github.com/hyperledger/avalon/blob/master/examples/graphene_apps/cppopenvino/README.md)

- Below steps will run sample openvino inference test cases in [test_ov_work_orders.json](http://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_worker/tests/test_ov_work_orders.json)

  ### Testing OpenVino (without Avalon)

  - For non SGX mode, execute below command

    `docker-compose -f docker-compose.yaml -f compose/ov.yaml -f compose/ov-subnet.yaml up`

  - For SGX mode, execute below command

    `docker-compose -f docker-compose.yaml -f compose/graphene-sgx.yaml -f compose/ov.yaml -f compose/ov-sgx.yaml -f compose/ov-subnet.yaml up`

  ### Testing OpenVino (with Avalon)

  - If Intel SGX is not used , execute following commands from Avalon repository top-level directory

    1. Combine the docker compose files to create `openvino.yaml`

       `docker-compose -f docker-compose.yaml -f docker/compose/avalon-graphene.yaml -f docker/compose/avalon-graphene-ov.yaml -f docker/compose/avalon-ov-subnet.yaml config > openvino.yaml`

    2. Start Avalon containers. This will also start Avalon python worker and openvino containers in detached mode.

       `docker-compose -f openvino.yaml up -d`

  - For Intel SGX, execute the following commands:

    1. Combine the docker compose files to create `openvino-sgx.yaml`

       `docker-compose -f docker-compose.yaml -f docker/compose/avalon-graphene.yaml -f docker/compose/avalon-graphene-sgx.yaml -f docker/compose/avalon-graphene-ov.yaml -f docker/compose/avalon-graphene-ov-sgx.yaml -f docker/compose/avalon-ov-subnet.yaml config > openvino-sgx.yaml`

    2. Start Avalon containers. This will also start Avalon python worker and openvino containers running inside Graphene-SGX in detached mode.

       `docker-compose -f openvino-sgx.yaml up -d`

  - In case of Intel SGX, Graphene-SGX python worker and openvino containers will take around 3 minutes to get ready. To view the logs of python worker and openvino containers, execute the following command:

    `docker-compose -f openvino-sgx.yaml logs -f graphene-python-worker ov-work-order`

  - To send openvino work orders to python worker, we can use [generic client](https://github.com/hyperledger/avalon/tree/master/examples/apps/generic_client) application. Execute the following commands:

    1. Get into Avalon Shell container : `sudo docker exec -it avalon-shell bash`

    2. cd `/project/avalon/examples/apps/generic_client/`

    3. Send openvino work order request with *"ov-inference"* workload id to Graphene worker *"graphene-worker-1"*

       `./generic_client.py --uri "http://avalon-listener:1947" -w "graphene-worker-1" --workload_id "ov-inference" --in_data "street.jpg" -o`

       If everything goes fine, then you should see the following output in stdout:

       *Decryption result at client - Openvino Success: Generated output file: street.bmp*

       output file *street.bmp* will be present in *output* folder in Avalon repository top level directory.

  - To restart the python worker we have to first bring all the containers down before bringing it up again. This is to ensure that python worker generates new worker signing and encryption keys and Avalon Graphene Enclave Manager gets the updated signup information from python worker.

    If Intel SGX is not used, execute the command: `docker-compose -f openvino.yaml down`

    For Intel SGX, execute the command: `docker-compose -f openvino-sgx.yaml down`

## Known issues

- Knows issues are captured in GitHub : https://github.com/hyperledger/avalon/issues/621

## Reference
* [Graphene Library OS](
  https://github.com/oscarlab/graphene#graphene-library-os-with-intel-sgx-support)
  Graphene Library OS GitHub.
* [Docker integration via Graphene Shielded Containers](
  https://github.com/oscarlab/graphene/blob/master/Documentation/manpages/gsc.rst)
  Graphene Shielded Containers documentation.
* [Graphene Avalon Integration Tech Talk](
  https://wiki.hyperledger.org/display/avalon/2020-06-30+LibOS%2C+Graphene+in+Avalon)
  Graphene Avalon Integration tech talk by Manoj Gopalakrishnan (2020).
