
**Testing Avalon Proxy model with Hyperledger Besu**
1.  Install ``truffle`` using the command
    ```
    sudo npm install -g truffle
    ```
    This requires Requires ``NodeJS v8.9.4 or later`` preinstalled.

2.  Set the environment variable ``TCF_HOME`` to the Avalon root directory

3.  Start the Ethereum network with 2 nodes and 2 eth-signers. To bring up the network, do the following
       ```
    cd $TCF_HOME/docs/dev-environments/besu
    docker-compose up -d
    ```
       This will start the Ethereum network locally.

4.  Now you need to create a truffle project and deploy contracts onto the Ethereum network
       ```
        mkdir ./my_project
        cd my_project
        truffle init
        cp $TCF_HOME/sdk/avalon_sdk/ethereum/contracts/proxy-model/*.sol ./contracts/
        cp $TCF_HOME/sdk/avalon_sdk/ethereum/truffle_artifacts/truffle-config.js ./
        cp $TCF_HOME/sdk/avalon_sdk/ethereum/truffle_artifacts/2_deploy_contracts.js ./migrations/
        truffle migrate --network avalon
        ```
5. The ``truffle migrate`` command would deploy contracts to the Ethereum network. If the command is successful, you should see something like 

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
6. Update configuration fields in ``$TCF_HOME/sdk/avalon_sdk/tcf_connector.toml ``
	- **proxy_worker_registry_contract_address** - Read the field ``contract address`` from Step 4 under ``Deploying 'WorkerRegistry'``
	- **work_order_contract_address** - Read the field ``contract address`` from Step 4 under ``Deploying 'WorkerOrderRegistry'``
	- **eth_account** - Read the field account from Step 4
	- **provider** - Replace the placeholder IP(only IP and not the port) with the IP address of your host machine
	- **event_provider** - Replace the placeholder IP with the IP address of your host machine

7. Start the Avalon containers

    ``docker-compose -f docker-compose-eth-besu.yaml up --build``

8. Go to the ``avalon-shell`` container to run ``eth_generic_client.py``:
      ```
       docker exec -it avalon-shell bash
       cd examples/apps/generic_client/
       ./eth_generic_client.py -b ethereum --workload_id "echo-result" -o --in_data "Hello"

One thing to note with the default Besu setup being used is that it retains the on-chain data across docker restarts. To clean this up,
use these steps 
```
cd $TCF_HOME/docs/dev-environments/besu
docker-compose down
./cleanup.sh
```
