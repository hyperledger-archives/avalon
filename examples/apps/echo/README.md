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
    the [build document](../../../BUILD.md#dockerbuild) through step 4
    (activating a virtual environment)
3.  Terminal 1 is running the TCF Enclave Manager and Listener with
    `docker-compose` . Terminal 2 is running the Docker container shell
    with the `(_dev)` prompt
4.  In Terminal 2 run `cd $TCF_HOME/examples/apps/echo/client`
5.  In Terminal 2 install the Solidity compiler as follows:
    ```bash
    mkdir -p $HOME/.py-solc/solc-v0.4.25/bin \
    && curl -LsS https://github.com/ethereum/solidity/releases/download/v0.4.25/solc-static-linux \
            -o /root/.py-solc/solc-v0.4.25/bin/solc \
    && chmod 0755 /root/.py-solc/solc-v0.4.25/bin/solc &&
    export SOLC_BINARY=/root/.py-solc/solc-v0.4.25/bin/solc
    ```
6. In Terminal 2, set environment variable `WALLET_PRIVATE_KEY` if not set.
    This should match the value in file `docker/Dockerfile.tcf-dev`
    from step 3 above:
    ```bash
    export WALLET_PRIVATE_KEY="B413189C95B48737AE2D9AF4CAE97EB03F4DE40599DF8E6C89DCE4C2E2CBA8DE"
    ```
7.  In Terminal 2, run `./echo_client.py -m "Hello world"` .
    Use the `-h` option to see other available options

8.  You will see output showing:
    1. The client searches the registry for an "echo" worker
    2. Sends a request to the worker
    3. Waits for and receives a response.
    4. The messages sent and received are encrypted with the key specified
       in the JSON packet, then encoded in Base64.
9.  In Terminal 1, press Ctrl-c to stop the TCF Enclave Manager and Listener

