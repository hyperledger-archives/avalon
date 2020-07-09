<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Generic Hyperledger Avalon Workload Client

This is a generic command line client intended to work with any
workload application. The intention is to get up to speed quickly
in application development by providing a generic client that works
with any worker.

The client application accepts only strings as input parameters and assumes
that all outputs returned from the workload application are also provided
as strings. If other data types are needed (such as numbers or binaries),
then create a custom test application
(potentially by modifying this application)

The command line client, `generic_client.py`, sends a message to the worker.
For command line options, type `./generic_client.py -h` from this directory.

```
usage: generic_client.py [-h] [-c CONFIG] [-u URI | -a ADDRESS]
                         [-m {listing,registry}]
                         [-w WORKER_ID | -wx WORKER_ID_HEX] [-l WORKLOAD_ID]
                         [-i IN_DATA [IN_DATA ...]] [-p] [-r] [-o] [-rs]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        The config file containing the Ethereum contract
                        information
  -u URI, --uri URI     Direct API listener endpoint, default is
                        http://localhost:1947
  -a ADDRESS, --address ADDRESS
                        an address (hex string) of the smart contract (e.g.
                        Worker registry listing)
  -b {ethereum,fabric}, --blockchain {ethereum,fabric}
                        Blockchain type to use in proxy model
  -m {listing,registry}, --mode {listing,registry}
                        should be one of listing or registry (default)
  -w WORKER_ID, --worker_id WORKER_ID
                        worker id in plain text to use to submit a work order
  -wx WORKER_ID_HEX, --worker_id_hex WORKER_ID_HEX
                        worker id as hex string to use to submit a work order
  -l WORKLOAD_ID, --workload_id WORKLOAD_ID
                        workload id (hex string) for a given worker
  -i IN_DATA [IN_DATA ...], --in_data IN_DATA [IN_DATA ...]
                        Input data
  -p, --in_data_plain   If present, send input data as unencrypted plain text
  -r, --receipt         If present, retrieve and display work order receipt
  -o, --decrypted_output
                        If present, display decrypted output as JSON
  -rs, --requester_signature
                        Enable requester signature for work order requests
```

The `--mode` option is used only with an Ethereum smart contract address.
Currently only "listing" mode is supported.
This will fetch the URI from the Ethereum blockchain, do a worker lookup to fetch
worker details of first worker in the list, and submit the work order.

If `--uri` is passed, `--mode` is not used. It will fetch the worker details
from the LMDB database and submit work order to the first available worker.
The Avalon Listener uses TCP port 1947, so the default URI is
`http://localhost:1947` .
If you are using Docker, add `--uri "http://avalon-listener:1947"`
to the command line.

## Using the Generic Client

Running `generic_client.py` allows you to submit
worker requests on the command line.

1. If needed, update the Ethereum account and direct registry contract
   information in `$TCF_HOME/sdk/avalon_sdk/tcf_connector.toml`
2. Follow the build instructions in the
   [build document](../../../BUILD.md)
3. Install the Solidity compiler:
    ```bash
    pip3 install --upgrade py-solc-x
    python3 -m solcx.install v0.5.15
    ```
4. Change to the Generic Client directory
   ```bash
   cd $TCF_HOME/examples/apps/generic_client
   ```
5. Run `./generic_client.py` using the appropriate command line options
   documented here. For a list of options, type `./generic_client.py -h`

## Examples

### Echo workload using a URI
```bash
./generic_client.py -o --uri "http://localhost:1947" \
    --workload_id "echo-result" --in_data "Hello" --worker_id "singleton-worker-1"
```

NOTE: `worker_id` should match with worker id of singleton enclave manager.  
This worker_id can either be command line argument passed to enclave manager or  
in the absence of command line argument, worker_id in
`$TCF_HOME/config/singleton_enclave_config.toml` should be used.

Add or change the `--uri` parameter if using Docker:
```bash
./generic_client.py -o --uri "http://avalon-listener:1947" \
    --workload_id "echo-result" --in_data "Hello" --worker_id "singleton-worker-1"
```

Or omit the URI if you use the default URI (standalone mode) :
```bash
./generic_client.py -o --workload_id "echo-result" --in_data "Hello" \
    --worker_id "singleton-worker-1"
```

### Heart disease eval workload using a URI
Standalone mode (no Docker):
```bash
./generic_client.py -o --uri "http://localhost:1947" \
    --workload_id "heart-disease-eval" \
    --in_data "Data: 25 10 1 67  102 125 1 95 5 10 1 11 36 1" \
    --worker_id "singleton-worker-1"
```

With Docker:
```bash
./generic_client.py -o --uri "http://avalon-listener:1947" \
    --workload_id "heart-disease-eval" \
    --in_data "Data: 25 10 1 67  102 125 1 95 5 10 1 11 36 1" \
    --worker_id "singleton-worker-1"
```

### Echo workload using registry listing smart contract address
```bash
./generic_client.py -o \
    --address "0x9Be28B132aeE1b2c5A1C50529a636cEd807842cd" --mode "listing" \
    --workload_id "echo-result" --in_data "Hello" \
    --worker_id "singleton-worker-1"
```

### Echo workload with input data as unencrypted plain text
```bash
./generic_client.py -o --uri "http://localhost:1947" \
    --workload_id "echo-result" --in_data "Hello" -p \
    --worker_id "singleton-worker-1"
```

