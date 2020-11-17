..
   Licensed under Creative Commons Attribution 4.0 International License.

Testing Hyperledger Avalon Proxy Model with Hyperledger Fabric
==============================================================

Hyperledger Fabric is an enterprise, private, permissioned blockchain network.
To run Fabric with Hyperledger Avalon on a single machine (both Avalon and Fabric network running on same machine),
follow these steps:

1. Set the environment variable ``TCF_HOME`` to the Avalon root directory.

   .. code:: sh

       cd /path/to/your/avalon
       export TCF_HOME=$PWD

2. Install ``curl``, ``docker`` and ``docker-compose``.
   See `PREREQUISITES <../PREREQUISITES.md#docker>`_
   for instructions on Docker.

3. Proxy configuration (optional).
   If the host machine is behind any network firewall/proxy, you need to
   define the following parameters in your ``/etc/environment`` file:

   .. code:: sh

       http_proxy=<http-proxy-url>:<port>
       https_proxy=<https-proxy-url>:<port>

   By default minifab creates 3 orderers, 2 peers with 2 organizations.
   The ``no_proxy`` for this setup is as follows (all on one line):

   .. code:: sh

       export no_proxy=localhost,127.0.0.1,orderer3.example.com,orderer2.example.com,
                orderer1.example.com,peer2.org1.example.com,peer1.org1.example.com,
                peer2.org0.example.com,peer1.org0.example.com
       export NO_PROXY=$no_proxy

   If you modify the number of orderers, peers, or organizations,
   please update the ``no_proxy`` list accordingly.

4. Start the Fabric network with 2 organizations, 4 peers and 3 orderers
   using the ``start_fabric.sh`` script.

   .. code:: sh

       cd $TCF_HOME
       ./scripts/start_fabric.sh -u

   Starting Fabric docker containers will take some time.
   Once it is up and running, type
   ``docker ps``
   and check for Fabric Docker containers named
   ``peer-*``, ``orderer-*``, and ``dev-*``

5. Start the Avalon docker containers

   .. code:: sh

       sudo docker-compose -f docker-compose.yaml -f docker/compose/avalon-fabric.yaml up -d --build

   To start a worker pool (with one Key Management Enclave and one Work order Processing Enclave):

   .. code:: sh

       sudo docker-compose -f docker-compose.yaml -f docker/compose/avalon-pool.yaml -f docker/compose/avalon-fabric.yaml up -d --build

   To run in Intel SGX hardware mode, use the corresponding docker compose file for singleton or worker pool mode (as specified in `BUILD.md <../BUILD.md>`_).

   Once the Fabric containers are up and running, we can start and stop Avalon
   containers any number of times without restarting the Fabric containers.
   To save time, omit the ``--build`` parameter after running the first time
   so you do not rebuild Avalon.

6. Go to the ``avalon-shell`` container to run ``generic_client.py``:

   .. code:: sh

       docker exec -it  avalon-shell bash
       cd examples/apps/generic_client/
       ./generic_client.py -b fabric --workload_id "echo-result" --in_data "Hello" -o \
           --worker_id "singleton-worker-1"

   NOTE: ``worker_id`` should match with worker id of singleton enclave manager or target worker pool.
   This ``worker_id`` can either be the command line argument passed in to the enclave manager (Singleton or KME)
   or in the absence of it, ``worker_id`` in the corresponding config file in `config <../config>`_ directory.

7. To stop the Fabric network run this command:

   .. code:: sh

       ./scripts/start_fabric.sh -d

Setup Hyperledger Avalon Fabric Proxy Model on multiple machines
----------------------------------------------------------------
Multinode Hyperledger Avalon Fabric proxy model setup requires certain modifications to the existing
docker files. For example to setup the Fabric blockchain network on a separate machine and Avalon on a separate machine
requires below changes.

1. On machine1(with ip address IP1), you need to run the minifab if you choose to setup fabric on single machine.
   Otherwise if you choose any customized way other than minifab to setup a fabric network on multiple nodes, then it is mandatory to deploy
   the Avalon chaincodes which are located at https://github.com/hyperledger/avalon/tree/master/sdk/avalon_sdk/connector/blockchains/fabric/chaincode.

   .. code:: sh

        cd $TCF_HOME
        ./scripts/start_fabric.sh -e

   start_fabric.sh with option -e exposes the ports to host machine and it generates the network profile with host ip in the network config file.

2. On machine2 (with ip address IP2) where Avalon is going to be setup, copy the crypto materials used to setup the Fabric network to home directory.
   Avalon shell and Avalon Fabric connector need these crypto materials to interact with the blockchain.

   .. code:: sh

        scp -r $TCF_HOME/mywork <user_name>@<IP1>:~/

3. If you choose a customized setup other than start_fabric.sh (minifab) then create the network.json as in https://github.com/hyperledger/avalon/blob/master/sdk/avalon_sdk/connector/blockchains/fabric/network.json

4. If these 2 machines are in corporate network, please update environment variables `no_proxy` and `NO_PROXY`
   with the IP1 on machine2 as mentioned above.

5. Remove the network tag from the Docker compose file - https://github.com/hyperledger/avalon/blob/master/docker/compose/avalon-fabric.yaml#L62

6. Start the Avalon components.

   .. code:: sh

        docker-compose -f docker-compose.yaml -f docker/compose/avalon-fabric.yaml up -d --build

   To start a worker pool (with one Key Management Enclave and one Work order Processing Enclave):

   .. code:: sh

        docker-compose -f docker-compose.yaml -f docker/compose/avalon-pool.yaml -f docker/compose/avalon-fabric.yaml up -d --build

   To run in Intel SGX hardware mode, use the corresponding Docker compose file for singleton or worker pool mode (as specified in BUILD.md).

7. To test using Fabric generic client.
   Go to the avalon-shell container to run generic_client.py

   .. code:: sh

        docker exec -it  avalon-shell bash
        cd examples/apps/generic_client/
        ./generic_client.py -b fabric --workload_id "echo-result" --in_data "Hello" -o \
    --worker_id "singleton-worker-1"


Troubleshooting
---------------

- To cleanup and start over (after a mistake or to try another version),
  follow these steps:

  1. Cleanup Docker Fabric service containers and the work directory

     .. code:: sh

         ./scripts/start_fabric.sh -c

     This runs ``$TCF_HOME/mywork/minifab cleanup`` and
     removes directory ``$TCF_HOME/mywork/vars``
  2. Verify Fabric Docker service containers are down with ``docker ps -a``
  3. To remove containers that exited but are not removed, type:

     .. code:: sh

         docker rm $(docker ps -aq -f status=exited)

  4. Remove the Fabric work directory and minifab:
     ``rm -rf $TCF_HOME/mywork``
  5. Optional. To remove the Avalon directory type:
     ``cd; rm -rf $TCF_HOME``

- If you see the message

  .. code:: none

      Got permission denied while trying to connect to the Docker daemon socket at
      unix:///var/run/docker.sock

  You need to add group ``docker`` to your login account.
  Type the following:

  .. code:: sh

      sudo groupadd docker
      sudo usermod -aG docker $USER

  Then logout and login again to update your group membership.
  After logging in again, verify that you are a member of group ``docker``
  and that you can run ``docker`` with:

  .. code:: sh

      groups
      docker run hello-world

  Group ``docker`` should appear in the output.
  The Docker ``hello-world`` container should download, run without error,
  and print the message ``Hello from Docker!``.
