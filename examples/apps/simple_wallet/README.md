# Simple Wallet Demo Application

This application demonstrates basic wallet transactions like deposit, withdraw and transfer
by accessing encrypted wallet ledger file using inside-out API and applying crypto operations
on the ledger data.

## Using the Generic Command Line Client to execute Simple Wallet operations

Generic command line client, `generic_client.py` sends an input request
with transaction type, account identifier(s), and amount to the worker
which stores stores wallet details in encrypted ledger using inside-out API.
The encrypted ledger data is then decrypted by the workload by making use of crypto functions.
Once the balance is updated, the result is encrypted and written to ledger using file i/o.  
Both encryption and decryption of the ledger data is achieved using symmetric encryption key generated 
at the time of workload registration to the enclave.

Below is the syntax of in_data for the work order request for supported wallet transactions. 
This in_data of the work order request is encrypted using session key.  
 
```
1. deposit <account_identifier> <amount>
2. withdraw <account_identifier> <amount>
3. transfer <debitor_identifier> <creditor_identifier> <amount>
```

For command line options, type `./generic_client.py -h` from the
`$TCF_HOME/examples/apps/generic_client/client` directory.

To use:

1.  If needed, update the Ethereum account and direct registry contract
    information in `docker/Dockerfile.tcf-dev` and
    `examples/common/python/connectors/tcf_connector.toml`
2.  Follow instructions in the "Docker-based Build and Execution" section of
    the [build document](../../../BUILD.md#dockerbuild) through step 4
3.  Terminal 1 is running the TCF Enclave Manager and Listener with
    `docker-compose` and Terminal 2 is running the Docker container.
4.  In Terminal 2 run `cd $TCF_HOME/examples/apps/generic_client` 

5. Execute wallet transactions.

Deposit transaction:  

In Terminal 2, Create wallets for Alice and bob  

```
./generic_client.py --workload_id "simple-wallet" --in_data "deposit alice 100"  

/generic_client.py --workload_id "simple-wallet" --in_data "deposit bob 100"  
```

Withdraw transaction:  

``` 
./generic_client.py --workload_id "simple-wallet" --in_data "withdraw alice 100"    
```

Transfer transaction:  

``` 
./generic_client.py --workload_id "simple-wallet" --in_data "transfer alice bob 50"  
```

6.  You will see output showing:
    1. The client searches the registry for an "inside-out-eval" worker
    2. Sends a request to the worker
    3. Waits for and receives a response.
    4. The messages sent and received are encrypted with the key specified
       in the JSON packet, then encoded in Base64.
    5. On success, you can expect below message on the console.  
       For deposit transaction  
       `WALLET RESULT: <account_identifier>::<wallet_balance>`  
       For withdraw transaction  
       `WALLET RESULT: <account_identifier>::<wallet_balance>`  
       For transfer transaction  
       `WALLET RESULT: <debitor>::<debitor_balance>,<creditor>::<creditor_balance>`  
7.  In Terminal 1, press Ctrl-c to stop the TCF Enclave Manager and Listener
