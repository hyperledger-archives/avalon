<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# OpenVino based object detection sample application

## Introduction
* This is an example C++ application based on OpenVino SSD (Single Shot Detector) object detection.
* This application can be built and executed inside a docker container (without Intel SGX) and also in Graphene-SGX environment.

## Building and Running the application without Intel SGX

- To build the application execute the following command from [cppopenvino](https://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/cppopenvino) directory:

  `docker-compose build`

  Building docker image for the first time will take a long time to generate OpenVino libraries and application executable. Subsequent builds will be quicker (using multi stage docker build) in case application has to be rebuild after making any modification to the source files.

- To run the object detection application and to use a test script to send work order requests,  execute the following command from [cppopenvino](http://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/cppopenvino) directory.

  `docker-compose up`

  Above command will run object detection on sample images present in [*images*](http://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_worker/cppopenvino/images) directory.

## Building and Running the application in Graphene SGX

- Before building and running application for Graphene-SGX, we need to install Intel SGX driver and Graphene SGX driver.

  - To install Intel SGX driver please refer https://github.com/hyperledger/avalon/blob/master/PREREQUISITES.md#intel-sgx-in-hardware-mode
  - To install Graphene SGX driver please refer https://graphene.readthedocs.io/en/latest/building.html#install-the-graphene-sgx-driver-not-for-production

- To build docker image for Graphene-SGX we need to use [Graphene Shielded Container](https://github.com/oscarlab/graphene/tree/master/Tools/gsc) (GSC) tool. Please refer to [GSC tool documentation](https://github.com/oscarlab/graphene/blob/master/Documentation/manpages/gsc.rst) for detailed instructions to create graphene based docker image from application docker image.

- To build graphene based docker image, we need the non-SGX docker image built earlier and an application specific [Graphene manifest file]( https://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/cppopenvino/graphene/openvinowl.manifest).

- Run the following command from Graphene git repository root directory:

  1. Create GSC build configuration file using following commands :

     `cd Tools/gsc`

     `cp config.yaml.template config.yaml`

     *# Adopt config.yaml to the installed Intel SGX driver and desired Graphene repository.*

     *#Openvino application was tested using below configuration*.

     *Distro: "ubuntu18.04"*
     *Graphene:*
     ​    *Repository:* *"https://github.com/oscarlab/graphene.git"*
     ​    *Branch: "master"*
     *SGXDriver:*
     ​    *Repository: "https://github.com/01org/linux-sgx-driver.git"*
     ​    *Branch: "sgx_driver_2.6"*

  2. Copy the Graphene python worker GSC build script file *build_gsc_openvinowl.sh* from this [location](https://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/cppopenvino/graphene) to <graphene_repo>/Tools/gsc using following command :

     `cp <path of build_gsc_openvinowl.sh> Tools/gsc`

  3. Set *TCF_HOME* to the top level directory of your avalon source repository.

     `export TCF_HOME = <path of avalon repo top level directory>`

  4. Graphenize Avalon python worker docker image using following command :

     `./build_gsc_openvinowl.sh`

  Above command if run successfully will generate a Graphene based docker image.


- To run the application as a docker container in Graphene-SGX environment and to use a test script to send work order requests, execute the following command from [cppopenvino](https://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/cppopenvino) directory.

  `docker-compose -f docker-compose.yaml -f docker-compose-sgx.yaml up`

## Testing OpenVino Object detection with Python worker

### Testing OpenVino (without Avalon)

- For non SGX mode, execute below steps from [cppopenvino](http://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/cppopenvino) directory

  - Build Openvino python workload image
    `docker-compose -f compose/python-worker-graphene.yaml build`
  - Run Openvino inference workloads with python worker
    `docker-compose -f docker-compose.yaml -f compose/python-worker-graphene.yaml -f compose/ov-subnet.yaml up`

- For SGX mode, execute below steps

  - Build Openvino python workload image
    `docker-compose -f compose/python-worker-graphene.yaml build`
  - Run Openvino inference workloads with graphene python worker
    `docker-compose -f docker-compose.yaml -f docker-compose-sgx.yaml -f compose/python-worker-graphene.yaml -f compose/python-worker-gsgx.yaml -f compose/ov-subnet.yaml up`

### Testing OpenVino (with Avalon)

- If Intel SGX is not used, execute following commands from Avalon repository top-level directory

  1. Combine the docker compose files to create `openvino.yaml`

     `docker-compose -f docker-compose.yaml -f docker/compose/avalon-ov-graphene.yaml -f docker/compose/avalon-ov-subnet.yaml config > openvino.yaml`

  2. Start Avalon containers. This will also start Avalon openvino python workload and openvino containers in detached mode.

     `docker-compose -f openvino.yaml up -d`

- For Intel SGX, execute the following commands:

  1. Combine the docker compose files to create `openvino-sgx.yaml`

     `docker-compose -f docker-compose.yaml -f docker/compose/avalon-ov-graphene.yaml -f docker/compose/avalon-ov-gsgx.yaml -f docker/compose/avalon-ov-subnet.yaml config > openvino-sgx.yaml`

  2. Start Avalon containers. This will also start Avalon python openvino workload and openvino containers running inside Graphene-SGX in detached mode.

     `docker-compose -f openvino-sgx.yaml up -d`

- In case of Intel SGX, Graphene-SGX openvino python workload and openvino containers will take around 3 minutes to get ready. To view the logs of python worker and openvino containers, execute the following command:

  `docker-compose -f openvino-sgx.yaml logs -f graphene-python-workload ov-work-order`

- To send openvino work orders to python worker, we can use [generic client](https://github.com/hyperledger/avalon/tree/master/examples/apps/generic_client) application. Execute the following commands:

  1. Get into Avalon Shell container : `sudo docker exec -it avalon-shell bash`

  2. cd `/project/avalon/examples/apps/generic_client/`

  3. Send openvino work order request with *"ov-inference"* workload id to Graphene worker *"graphene-worker-1"*

    `./generic_client.py --uri "http://avalon-listener:1947" -w "graphene-worker-1" --workload_id "ov-inference" --in_data "street.jpg" -o`

    If everything goes fine, then you should see the following output in stdout:

    *Decryption result at client - Openvino Success: Generated output file: street.bmp*

    output file *street.bmp* will be present in *output* folder in Avalon repository top level directory.

- To restart the openvino python workload we have to first bring all the containers down before bringing it up again. This is to ensure that python worker generates new worker signing and encryption keys and Avalon Graphene Enclave Manager gets the updated signup information from python worker.

  - If Intel SGX is not used, execute the command: `docker-compose -f openvino.yaml down`

  - For Intel SGX, execute the command: `docker-compose -f openvino-sgx.yaml down`

## Known issues

- Graphene Production blockers: [oscarlab/graphene#1544](https://github.com/oscarlab/graphene/issues/1544)

## Reference
* [Graphene Library OS](
  https://github.com/oscarlab/graphene#graphene-library-os-with-intel-sgx-support)
  Graphene Library OS GitHub.

* [Docker integration via Graphene Shielded Containers](
  https://github.com/oscarlab/graphene/blob/master/Documentation/manpages/gsc.rst)
  Graphene Shielded Containers documentation.

* [OpenVino object detection sample application](https://github.com/openvinotoolkit/openvino/tree/master/inference-engine/samples/object_detection_sample_ssd)
  C++ based OpenVino Object Detection sample application using Single Shot Detector (SSD) inference model.

* [Graphene OpenVino Demo](https://wiki.hyperledger.org/pages/viewpage.action?pageId=36734054)
  Graphene OpenVino demo by Manoj Gopalakrishnan (2020).
