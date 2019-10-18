# Echo Demo Application

This simple demo application echos back the same message sent from
the client to the worker.

## Using the Echo Command Line Client

The command line client, `echo_client.py` sends a message to the worker,
which echos back the same message back to the client.
For command line options, type `./echo_client.py -h` from the
`client` directory.

To use:

1.  If needed, update the Ethereum account and direct registry contract
    information in `docker/Dockerfile.tcf-dev` and
    `examples/common/python/connectors/tcf_connector.toml`
2.  Follow instructions in the "Docker-based Build and Execution" section of
    the [build document](../../../BUILD.md#dockerbuild) through step 5
    (activating a virtual environment)
3.  Terminal 1 is running the Avalon Enclave Manager and Listener with
    `docker-compose` . Terminal 2 is running the Docker container shell
4.  In Terminal 2 run `cd $TCF_HOME/examples/apps/echo/client`
5.  In Terminal 2, run `./echo_client.py -m "Hello world"` .
    Use the `-h` option to see other available options

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

