..
   Licensed under Creative Commons Attribution 4.0 International License.

Testing Hyperledger Avalon Proxy Model with Ganache
===================================================

Ganache is a personal Ethereum blockchain used for application development
and testing.
To run Ganache with Hyperledger Avalon, follow these steps:

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

   This is the hostname used in the default Ganache network
   defined in the corresponding
   `docker-compose file <./dev-environments/ethereum/ganache/docker-compose-truffle.yaml>`_
   The ``no_proxy`` for this setup is as follows:

   .. code:: none

       no_proxy=localhost,127.0.0.1,local-ganache

   This is the local Ganache node hostname.

2. Start the Ganache Ethereum network (single node) and deploy contracts.
   To do so, you need to run the following

   .. code:: sh

       cd $TCF_HOME/docs/dev-environments/ethereum/ganache
       ./startup.sh

   This will start the Ethereum network locally and deploy the
   required contracts over it.

3. The previous step, if successful, would leave behind logs having content
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

4. Update configuration fields in ``$TCF_HOME/sdk/avalon_sdk/tcf_connector.toml ``

   ``worker_registry_contract_address``
       Read field ``contract address`` from Step 3 under
       ``Deploying 'WorkerRegistry'``

   ``work_order_contract_address``
       Read field ``contract address``
       from Step 3 under ``Deploying 'WorkOrderRegistry'``

   ``eth_account``
       Read field ``account`` from Step 3

   ``provider``  and ``event_provider``
       Update both to ``http://local-ganache:8545``

5. Start the Avalon containers

   .. code:: sh

       cd $TCF_HOME
       docker-compose -f docker-compose-eth-ganache.yaml up -d --build

6. Go to the ``avalon-shell`` container to run ``eth_generic_client.py``:

   .. code:: sh

       docker exec -it avalon-shell bash
       cd examples/apps/generic_client/
       ./eth_generic_client.py -b ethereum --workload_id "echo-result" -o --in_data "Hello"

Cleanup
-------

To clean up the Ganache network, follow these steps:

.. code:: sh

    cd $TCF_HOME/docs/dev-environments/ethereum/ganache
    ./cleanup.sh
