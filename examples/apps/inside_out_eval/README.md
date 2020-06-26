<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Inside Out File I/O Demo Hyperledger Avalon Application

This simple demo application executes file I/O operations, such as read and write, from inside the Intel SGX enclave,
based on the input from the user.
This allows access inside the enclave to files outside the enclave, so is sometimes called Inside/Out I/O.

## Using the Generic Command Line Client to execute file I/O

The generic command line client, `generic_client.py`, sends an input request
with file operation, filepath, content to be written, etc. to the worker
which access the inside-out api and calls appropriate file i/o
implementation provided outside trusted boundary.
For command line options, type `./generic_client.py -h` from the
`client` directory.

To use:

1.  If needed, update the Ethereum account and direct registry contract
    information in `sdk/avalon_sdk/tcf_connector.toml`
2.  Follow instructions in the "Docker-based Build and Execution" section of
    the [build document](../../../BUILD.md#dockerbuild) through step 4
3.  Terminal 1 is running the Avalon Enclave Manager and Listener with
    `docker-compose` and Terminal 2 is running the Docker container.
4.  In Terminal 2 run `cd $TCF_HOME/examples/apps/generic_client`

To read a file:

5.  In Terminal 2, run
    `./generic_client.py --workload_id "inside-out-eval" --in_data "read <file>" -o` .
    The file parameter should point to an absolute path which can be accessed by
    the enclave manager.
    For example, if the enclave manager is running in a Docker container, the
    file path could be `/project/trusted-compute-framework/tests/read.txt` .
    Use the `-h` option to see other available options

To write a file:

5. In Terminal 2, run
   `./generic_client.py --workload_id "inside-out-eval" --in_data "write <file> <content-to-be-written>" -o` .
   The file parameter should point to an absolute path which can be accessed by
   the enclave manager.
   For example, if the enclave manager is running in a Docker container, the
   file path could be `/project/trusted-compute-framework/tests/write.txt` .
   Use the `-h` option to see other available options

6.  You will see output showing:
    1. The client searches the registry for an "inside-out-eval" worker
    2. Sends a request to the worker
    3. Waits for and receives a response.
    4. The messages sent and received are encrypted with the key specified
       in the JSON packet, then encoded in Base64.
    5. On success, you can expect below message on the console.
       If file operation is read
       `Decryption result at client - RESULT: <content of the file>`
       If file operation is write
       `Decryption result at client - RESULT: FILE WRITE SUCCESS`
       and the file should be written with the content passed in the input.
7.  In Terminal 1, press Ctrl-c to stop the Avalon Enclave Manager and Listener
