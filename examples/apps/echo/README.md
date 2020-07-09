<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Echo Demo Hyperledger Avalon Application

This simple demo application echos back the same message sent from
the client to the worker.

## Using the Echo Command Line Client

The command line client, `echo_client.py` sends a message to the worker,
which echos back the same message back to the client.
For command line options, type `./echo_client.py -h` from the
`client` directory.

```
usage: echo_client.py [-h] [-c CONFIG]
                      [-r REGISTRY_LIST | -s SERVICE_URI | -o] [-w WORKER_ID]
                      [-m MESSAGE] [-rs] [-dh]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        the config file containing the Ethereum contract
                        information
  -r REGISTRY_LIST, --registry-list REGISTRY_LIST
                        the Ethereum address of the registry list
  -s SERVICE_URI, --service-uri SERVICE_URI
                        skip URI lookup and send to specified URI
  -o, --off-chain       skip URI lookup and use the registry in the config
                        file
  -w WORKER_ID, --worker-id WORKER_ID
                        skip worker lookup and retrieve specified worker
  -m MESSAGE, --message MESSAGE
                        text message to be included in the JSON request
                        payload
  -rs, --requester-signature
                        Enable requester signature for work order requests
  -dh, --data-hash      Enable input data hash for work order requests
```

The Avalon Listener uses TCP port 1947, so the default URI is
`http://localhost:1947` .
If you are using Docker, add `-s "http://avalon-listener:1947"`
to the command line.

## Using the Echo Client

The echo client client `echo_client.py` allows you to submit
echo requests to the echo worker on the command line.

1.  If needed, update the Ethereum account and direct registry contract
    information in `sdk/avalon_sdk/tcf_connector.toml`
2.  Follow instructions in the "Docker-based Build and Execution" section of
    the [build document](../../../BUILD.md#dockerbuild) through step 5
    (activating a virtual environment)
3.  Terminal 1 is running the Avalon Enclave Manager and Listener with
    `docker-compose` . Terminal 2 is running the Docker container shell
4.  In Terminal 2 change to the echo client directory
    ```bash
    cd $TCF_HOME/examples/apps/echo/client
    ```
5.  In Terminal 2, run
    ```bash
    ./echo_client.py -s "http://avalon-listener:1947" -m "Hello world" -w "singleton-worker-1"
    ```
    NOTE: `worker_id` should match with worker id of singleton enclave manager.  
    This worker_id can either be command line argument passed to enclave manager or  
    in the absence of command line argument, worker_id in
    `$TCF_HOME/config/singleton_enclave_config.toml` should be used.

    If running in Standalone mode (without Docker), omit the `-s` option,
    so the client uses the default listener at `http://localhost:1947`
6.  You will see output showing the following:
    1. The client searches the registry for an "echo" worker
    2. The client sends a request to the worker
    3. The client waits for and receives a response in JSON format
    4. The decrypted response from the worker:
       ```
       [13:27:37 INFO    utility.utility]
       Decryption result at client - RESULT: Hello World
       ```
    5. The worker receipt in JSON format
    6. Messages sent and received are encrypted with the key specified
       in the JSON packet, then encoded in Base64.
7.  In Terminal 1, press Ctrl-c to stop the Avalon Enclave Manager and Listener
