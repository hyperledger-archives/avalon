# Running the Heart Disease Evaluation Demo

This demo performs a heart disease evaluation based on input parameters.
Three clients are available: batch command line client,
interactive command line client, and GUI client.


## Using the Heart Disease Evaluation Batch Command Line Client

The command line client, `Demo.py`, runs a set of pre-built JSON requests.
To run, follow the instructions in the "Testing" section of the
[build document](../../../BUILD.md#testing).
You may run the CLI demo in standalone mode or in a Docker container.


## Using the Heart Disease Evaluation Interactive Command Line Client

The command line client `generic_client.py` allows you to submit
requests on the command line.

1.  If needed, update the Ethereum account and direct registry contract
    information in `docker/Dockerfile.tcf-dev` and
    `examples/common/python/connectors/tcf_connector.toml`
2.  Follow instructions in the "Docker-based Build and Execution" section of
    the [build document](../../../BUILD.md#dockerbuild) through step 5
    (activating a virtual environment)
3.  Terminal 1 is running the Avalon Enclave Manager and Listener with
    `docker-compose` . Terminal 2 is running the Docker container shell
4.  In Terminal 2, set environment variable `WALLET_PRIVATE_KEY` if not set.
    This should match the value in file `docker/Dockerfile.tcf-dev`
    from step 3 above:
    ```bash
    export WALLET_PRIVATE_KEY="B413189C95B48737AE2D9AF4CAE97EB03F4DE40599DF8E6C89DCE4C2E2CBA8DE"
    ```
5.  In Terminal 2 run `cd $TCF_HOME/examples/apps/generic_client`
6.  In Terminal 2, run
    ``` bash
    ./generic_client.py --workload_id "heart-disease-eval" \
        --in_data "Data: 25 10 1 67 102 125 1 95 5 10 1 11 36 1"
    ```
7.  The data will be submitted to the worker and the results will appear shortly:
    ```
    [04:31:55 INFO    utility.utility] Decryption result at client -
    You have a 46% risk of heart disease.
    ```
8.  Optionally submit another request.
    Use the `--help` option to see other available options
9.  In Terminal 1, press Ctrl-c to stop the Avalon Enclave Manager and Listener

## Using the Heart Disease Evaluation GUI Client

The GUI client, `heart_gui.py` opens a X window on your display.
You must run this on your graphical console or a terminal emulator that
supports X Windows.
The Avalon Enclave Manager and Avalon Listener run in a Docker container.

1.  If needed, in file `docker/Dockerfile.tcf-dev` change `ENV DISPLAY`
    to the X Windows `$DISPLAY` value. By default, it is the console, `:0`
2.  If needed, also update the Ethereum account and direct registry contract
    information in `docker/Dockerfile.tcf-dev` and
    `examples/common/python/connectors/tcf_connector.toml`
3.  Follow instructions in the "Docker-based Build and Execution" section of
    the [build document](../../../BUILD.md#dockerbuild) through step 4
    (activating a virtual environment)
4.  Terminal 1 is running the Avalon Enclave Manager and Listener with
    `docker-compose` . Terminal 2 is running the Docker container shell
5.  In Terminal 2 run `cd $TCF_HOME/examples/apps/heart_disease_eval/client`
6.  In Terminal 2 install Python3's TKInter GUI library with
    ```bash
    apt update; apt -y install python3-tk python3-pil.imagetk
    ```
7.  In Terminal 2 install the Solidity compiler as follows:
    ```bash
    mkdir -p $HOME/.py-solc/solc-v0.4.25/bin \
    && curl -LsS https://github.com/ethereum/solidity/releases/download/v0.4.25/solc-static-linux \
            -o $HOME/.py-solc/solc-v0.4.25/bin/solc \
    && chmod 0755 $HOME/.py-solc/solc-v0.4.25/bin/solc &&
    export SOLC_BINARY=$HOME/.py-solc/solc-v0.4.25/bin/solc
    ```
8.  In Terminal 2, set environment variable `WALLET_PRIVATE_KEY` if not set.
    This should match the value in file `docker/Dockerfile.tcf-dev`
    from step 3 above:
    ```bash
    export WALLET_PRIVATE_KEY="B413189C95B48737AE2D9AF4CAE97EB03F4DE40599DF8E6C89DCE4C2E2CBA8DE"
    ```
9.  If your DISPLAY is not the local console, `:0`, you need to give access to
    your display from the GUI.
    Open a new terminal, Terminal 3, and run `xhost +`
10.  In Terminal 2, run `./heart_gui.py` .
    Use the `--help` option to see other available options
11. A new window will pop up with the GUI. See the screenshot below for an
    example.
12. Input all the heart disease evaluation values.
    Alternatively, check the "Input variables as string" box to input the
    values as a string of 14 integers separated by spaces. For example,
    `25 10 1 67 102 125 1 95 5 10 1 11 36 1` or
    `32 1 1 156 132 125 1 95 1 0 1 1 3 1`
13. Click the "Evaluate" button and a new window will appear with the
    heart disease evaluation result.
    The "View Request", "View Result", and "View Receipt" buttons will pop up
    windows displaying the raw JSON RPC files
14. Close the GUI windows when done
15. If you ran `xhost +` above, close access to your display with
    `xhost -` in Terminal 3
16. In Terminal 1, press Ctrl-c to stop the Avalon Enclave Manager and Listener

![Screenshot of heart_gui.py]( images/heart_gui_screenshot.jpg
  "Screenshot of heart_gui.py")
<br /> *Screenshot of heart_gui.py*
