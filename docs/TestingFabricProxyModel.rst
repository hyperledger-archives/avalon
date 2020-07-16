..
   Licensed under Creative Commons Attribution 4.0 International License.

Testing Hyperledger Avalon Proxy Model with Hyperledger Fabric
==============================================================

Hyperledger Fabric is an enterprise, private, permissioned blockchain network.
To run Fabric with Hyperledger Avalon, follow these steps:

1. Set the environment variable ``TCF_HOME`` to the Avalon root directory.

   .. code:: sh

       cd /path/to/your/avalon
       export TCF_HOME=$PWD

2. Install ``curl``, ``docker`` and ``docker-compose``.
   See `PREREQUISITES <../PREREQUISITES.md#docker>`_
   for instructions for Docker.

3. Proxy configuration (optional).
   If the host machine is behind any network firewall/proxy, you need to
   define the following parameters in your ``/etc/environment`` file:

   .. code:: none

       http_proxy=<http-proxy-url>:<port>
       https_proxy=<https-proxy-url>:<port>

   By default minifab creates 3 orderers, 2 peers with 2 organisations.
   The ``no_proxy`` for this setup is as follows (all on one line):

   .. code:: none

       no_proxy=localhost,127.0.0.1,orderer3.example.com,orderer2.example.com,
                orderer1.example.com,peer2.org1.example.com,peer1.org1.example.com,
                peer2.org0.example.com,peer1.org0.example.com

   If you modify the number of orderers, peers, or organisations,
   please update the ``no_proxy`` list accordingly.

4. Start the Fabric network with 2 organizations, 4 peers and 3 orderers
   using the ``start_fabric.sh`` script.

   .. code:: sh

       cd $TCF_HOME
       ./scripts/start_fabric.sh -u

   Starting Fabric Docker containers will take some time.
   Once it is up and running, type
   ``docker ps``
   and check for Fabric Docker containers named
   ``peer-*``, ``orderer-*``, and ``dev-*``

5. Start the Avalon Docker containers

   .. code:: sh

       docker-compose -f docker-compose.yaml -f docker/compose/avalon-fabric.yaml up -d --build

   To start a worker pool (with one Key Management Enclave and one Work order Processing Enclave):

   .. code:: sh

       docker-compose -f docker-compose.yaml -f docker/compose/avalon-pool.yaml -f docker/compose/avalon-fabric.yaml up -d --build

   To run in Intel SGX hardware mode, use the corresponding docker compose file for singleton or worker pool mode (as specified in `BUILD.md <../BUILD.md>`_).

   Once the Fabric containers are up and running we can start and stop Avalon
   containers any number of times without restarting the Fabric containers.
   To save time, omit the ``--build`` parameter after running the first time
   so it will not rebuild Avalon.

6. Go to the ``avalon-shell`` container to run ``fabric_generic_client.py``:

   .. code:: sh

       docker exec -it  avalon-shell bash

       cd examples/apps/generic_client/
       ./fabric_generic_client.py -b fabric --workload_id "echo-result" --in_data "Hello" -o \
           --worker_id "singleton-worker-1"

   NOTE: ``worker_id`` should match with worker id of singleton enclave manager or target worker pool.
   This ``worker_id`` can either be the command line argument passed in to the enclave manager (Singleton or KME)
   or in the absence of it, ``worker_id`` in the corresponding config file in `config <../config>`_ directory.

7. To stop the Fabric network run this command:

   .. code:: sh

       ./scripts/start_fabric.sh -d

Troubleshooting
---------------

- To cleanup and start over (after a mistake or to try another version),
  follow these steps:

  1. Cleanup Docker Fabric service containers and the work directory

     .. code:: sh

         ./scripts/start_fabric.sh -c

     This runs ``~/mywork/minifab cleanup`` and
     removes directory ``~/mywork/vars``
  2. Verify Fabric Docker service containers are down with ``docker ps -a``
  3. To remove containers that exited but are not removed, type:

     .. code:: sh

         docker rm $(docker ps -aq -f status=exited)

  4. Remove the Fabric work directory and minifab:
     ``rm -rf ~/mywork``
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
  and print the message ``Hello from Docker!``
