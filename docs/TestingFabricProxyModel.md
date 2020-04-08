**Testing Avalon Proxy model with Hyperledger Fabric**
1.  Install ``curl``, ``docker`` and ``docker-compose``.
    See [PREREQUISITES](PREREQUISITES.md#docker) for instructions for Docker.

2.  If the host machine is behind any firewall/proxy, you need to define the
    following parameters in /etc/environment file:
    http_proxy=<http-proxy-url>:<port>
    https_proxy=<https-proxy-url>:<port>
    
    By default minifab creates 3 orderers, 2 peers with 2 organisations. The
    no_proxy for this setup is as follows:
    no_proxy=localhost,127.0.0.1,orderer3.example.com,orderer2.example.com,
             orderer1.example.com,peer2.org1.example.com,peer1.org1.example.com,
             peer2.org0.example.com,peer1.org0.example.com
    
    If, you modify the number of orderers, peers or organisations, please update
    the no_proxy accordingly.

3.  Start the Fabric network with 2 organizations, 4 peers and 3 orderers
    using the ``start_fabric.sh`` script.
    ```
    cd $TCF_HOME
    ./scripts/start_fabric.sh -u
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
6. To stop fabric network run below command
    ```
    ./scripts/start_fabric.sh -d
    ```

