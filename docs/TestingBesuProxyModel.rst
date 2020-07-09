..
   Licensed under Creative Commons Attribution 4.0 International License.

Testing Hyperledger Avalon Proxy model with Hyperledger Besu
============================================================

Hyperledger Besu is an Ethereum client that can run on the public
or private permissioned blockchain network.
To run Besu with Hyperledger Avalon, follow these steps:

1. Set the environment variable ``TCF_HOME`` to the Avalon root directory.

   .. code:: sh

       cd /path/to/your/avalon
       export TCF_HOME=$PWD

2. Install ``docker`` and ``docker-compose``.
   See `PREREQUISITES <../PREREQUISITES.md#docker>`_
   for instructions for Docker.

3. Proxy configuration (optional).
   If the host machine is behind any network firewall/proxy, you need to
   define the following parameters in your ``/etc/environment`` file:

   .. code:: none

       http_proxy=<http-proxy-url>:<port>
       https_proxy=<https-proxy-url>:<port>

   These are hostnames used in the default Besu network
   defined in the corresponding
   `docker-compose file <./dev-environments/ethereum/besu/docker-compose.yaml>`_
   The ``no_proxy`` for this setup is as follows (all on one line):

   .. code:: none

       no_proxy=localhost,127.0.0.1,node1.avalon.local,rpc.node1.avalon.local,
                node2.avalon.local, rpc.node2.avalon.local

   If you modify the number of nodes, please update the ``no_proxy`` list
   accordingly.

4. Start the Hyperledger Besu based Ethereum network and deploy contracts.
   To do so, you need to run the following

   .. code:: sh

       cd $TCF_HOME/docs/dev-environments/ethereum/besu
       ./startup.sh

   This will start the Ethereum network locally and deploy the required
   contracts over it.

5. The previous step, if successful, would leave behind logs having content
   similar to this:

   .. code:: none

       2_deploy_contracts.js
       =====================

       Deploying 'WorkOrderRegistry'
       -----------------------------
       > transaction hash:    0x137cb74744324c653d50ef52c7576ef7cb211597f623cc301c737567551c87d7
       > Blocks: 0            Seconds: 4
       > contract address:    0xf873133fae1d1f80642c551a6edd5A14f37129c2
       > block number:        19
       > block timestamp:     1582739325
       > account:             0x7085d4d4C6eFea785edfba5880Bb62574E115626
       > balance:             1000000000
       > gas used:            667475
       > ...

   Only partial output is seen here. The actual output has more data.

6. Update configuration fields in
   ``$TCF_HOME/sdk/avalon_sdk/tcf_connector.toml``

   ``worker_registry_contract_address``
       Read field ``contract address`` from Step 3 under
       ``Deploying 'WorkerRegistry'``

   ``work_order_contract_address``
       Read field ``contract address`` from Step 3 under
       ``Deploying 'WorkOrderRegistry'``

   ``eth_account``
       Read field ``account`` from Step 3

7. Start the Avalon containers

   .. code:: sh

       cd $TCF_HOME
       docker-compose -f docker-compose.yaml -f docker/compose/avalon-eth-besu.yaml up -d --build

   To start a worker pool (with one Key Management Enclave and one Work order Processing Enclave):

   .. code:: sh

       docker-compose -f docker-compose.yaml -f docker/compose/avalon-pool.yaml -f docker/compose/avalon-eth-besu.yaml up -d --build

   To run in Intel SGX hardware mode, use the corresponding docker compose file for singleton or worker pool mode (as specified in `BUILD.md <../BUILD.md>`_).

8. Go to the ``avalon-shell`` container to run ``generic_client.py``:

   .. code:: sh

       docker exec -it avalon-shell bash
       cd examples/apps/generic_client/
       ./generic_client.py -b ethereum --workload_id "echo-result" -o --in_data "Hello" \
           --worker_id "singleton-worker-1"

   NOTE: ``worker_id`` should match with worker id of singleton enclave manager or target worker pool.
   This ``worker_id`` can either be the command line argument passed in to the enclave manager (Singleton or KME)
   or in the absence of it, ``worker_id`` in the corresponding config file in `config <../config>`_ directory.

Cleanup
-------

One thing to note with the default Besu setup being used is that it retains
the on-chain data across docker restarts. To clean this up,
follow these steps:

.. code:: sh

    cd $TCF_HOME/docs/dev-environments/ethereum/besu
    ./cleanup.sh
