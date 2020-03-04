**Testing Avalon Proxy model with Hyperledger Fabric**
1.  Install ``curl``, ``docker`` and ``docker-compose``.
    See [PREREQUISITES](PREREQUISITES.md#docker) for instructions for Docker.

2.  Set the environment variable ``TCF_HOME`` to the Avalon root directory

3.  Start the Fabric network with 2 organizations, 4 peers and 3 orderers
    using the ``start_fabric.sh`` script.
    ```
    cd $TCF_HOME
    ./scripts/start_fabric.sh
    ```
    Starting Fabric Docker containers will take some time.
    Once it is up and running check for Fabric containers named
    ``peer-*``, ``orderer-*``, and ``dev-*`` using ``docker ps``

4.  Start the Avalon containers

    ``docker-compose -f docker-compose-fabric.yaml up --build``

    Once the Fabric containers are up and running we can start and stop Avalon
    containers any number of time without restarting the Fabric containers.
    To save time, omit the ``--build`` parameter after running the first time
    so it will not rebuilt Avalon.

5.  Go to the ``avalon-shell`` container to run ``fabric_generic_client.py``:
    ````
    docker exec -it  avalon-shell bash

    cd examples/apps/generic_client/
    ./fabric_generic_client.py -b fabric --workload_id "echo-result" --in_data "Hello"
    ````

