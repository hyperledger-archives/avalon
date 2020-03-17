
**Testing Avalon Proxy model with Hyperledger Besu**
1.  Set the environment variable ``TCF_HOME`` to the Avalon root directory. Update ``no_proxy`` environment variable if you are behind a proxy
    server. Add these private IP - ``172.13.0.2, 172.13.0.3, 172.13.0.4, 172.13.0.5``. These are the IP addresses used in the default Besu 
    network defined in the corresponding [docker-compose file](dev-environments/besu/docker-compose.yaml)

2. Start the Hyperledger Besu based Ethereum network and deploy contracts. To do so, you need to run the following
    ```
    cd $TCF_HOME/docs/dev-environments/besu
    ./startup.sh
    ```
    This will start the Ethereum network locally and deploy the required contracts over it.

3. The previous step, if successful would leave behind logs having content similar to  
	```
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
	```
   Only partial output is seen here. The actual output has more data.
4. Update configuration fields in ``$TCF_HOME/sdk/avalon_sdk/tcf_connector.toml ``
	- **proxy_worker_registry_contract_address** - Read the field ``contract address`` from Step 3 under ``Deploying 'WorkerRegistry'``
	- **work_order_contract_address** - Read the field ``contract address`` from Step 3 under ``Deploying 'WorkerOrderRegistry'``
	- **eth_account** - Read the field account from Step 3

5. Start the Avalon containers
    ```
	cd $TCF_HOME
	docker-compose -f docker-compose-eth-besu.yaml up --build
	```

6. Go to the ``avalon-shell`` container to run ``eth_generic_client.py``:
    ```
    docker exec -it avalon-shell bash
    cd examples/apps/generic_client/
    ./eth_generic_client.py -b ethereum --workload_id "echo-result" -o --in_data "Hello"
    ```

One thing to note with the default Besu setup being used is that it retains the on-chain data across docker restarts. To clean this up,
use these steps 
```
cd $TCF_HOME/docs/dev-environments/besu
./cleanup.sh
```
