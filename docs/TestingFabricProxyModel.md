<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Testing Hyperledger Avalon Proxy Model with Hyperledger Fabric

1.  Install ``curl``, ``docker`` and ``docker-compose``.
    See [PREREQUISITES](../PREREQUISITES.md#docker) for instructions for Docker.

2.  If the host machine is behind any network firewall/proxy, you need to
    define the following parameters in your `/etc/environment` file:
    ```
    http_proxy=<http-proxy-url>:<port>
    https_proxy=<https-proxy-url>:<port>
    ```
    
    By default minifab creates 3 orderers, 2 peers with 2 organisations. The
    no_proxy for this setup is as follows (all on one line):
    ```
    no_proxy=localhost,127.0.0.1,orderer3.example.com,orderer2.example.com,
             orderer1.example.com,peer2.org1.example.com,peer1.org1.example.com,
             peer2.org0.example.com,peer1.org0.example.com
    ```
    
    If you modify the number of orderers, peers, or organisations, please update
    the `no_proxy` list accordingly.

3.  Start the Fabric network with 2 organizations, 4 peers and 3 orderers
    using the `start_fabric.sh` script.
    ```bash
    cd $TCF_HOME
    ./scripts/start_fabric.sh -u
    ```
    Starting Fabric Docker containers will take some time.
    Once it is up and running, type
    `docker ps`
    and check for Fabric Docker containers named
    `peer-*`, `orderer-*`, and `dev-*`

4.  Start the Avalon Docker containers

    ```bash
    docker-compose -f docker-compose-fabric.yaml up --build
    ```

    Once the Fabric containers are up and running we can start and stop Avalon
    containers any number of times without restarting the Fabric containers.
    To save time, omit the ``--build`` parameter after running the first time
    so it will not rebuild Avalon.

5.  Go to the `avalon-shell` container to run `fabric_generic_client.py`:
    ```bash
    docker exec -it  avalon-shell bash

    cd examples/apps/generic_client/
    ./fabric_generic_client.py -b fabric --workload_id "echo-result" --in_data "Hello"
    ```

6. To stop the Fabric network run this command:
    ```bash
    ./scripts/start_fabric.sh -d
    ```

## <a name="troubleshooting"></a>Troubleshooting
- If you see the message

  ```
  Got permission denied while trying to connect to the Docker daemon socket at
  unix:///var/run/docker.sock
  ```

  You need to add group `docker` to your login account.
  Type the following:

  ```bash
  sudo groupadd docker
  sudo usermod -aG docker $USER
   ```

  Then logout and login again to update your group membership.
  After logging in again, verify that you are a member of group `docker`
  and that you can run `docker` with:

  ```bash
  groups
  docker run hello-world
  ```

  Group `docker` should appear in the output.
  The Docker `hello-world` container should download and run without error.
