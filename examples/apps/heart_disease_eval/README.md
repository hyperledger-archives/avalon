<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Running the Heart Disease Evaluation Hyperledger Avalon Demo

This demo performs a heart disease evaluation based on input parameters.
Three clients are available: batch command line client,
interactive command line client, and GUI client.

[![Heart disease evaluation demo video
](../../../images/screenshot-introduction-to-hyperledger-avalon.jpg)
<br />*Heart Disease evaluation demo video
(10:26)*](https://youtu.be/6L_UOhi7Rxs)


## Using the Heart Disease Evaluation Batch Command Line Client

The command line client, `Demo.py`, runs a set of pre-built JSON requests.
To run, follow the instructions in the "Testing" section of the
[build document](../../../BUILD.md#testing).
You may run the CLI demo in standalone mode or in a Docker container.
Heart disease workload is designed to compute average heart disease risk, 
even when invalid data is passed at the in_data parameter via the
command prompt.


## Using the Heart Disease Evaluation Interactive Command Line Client

The command line client `generic_client.py` allows you to submit
requests on the command line.

1.  If needed, update the Ethereum account and direct registry contract
    information in `sdk/avalon_sdk/tcf_connector.toml`
2.  Follow instructions in the "Docker-based Build and Execution" section of
    the [build document](../../../BUILD.md#dockerbuild).

    As an alternative, you can run this in Standalone mode without Docker.
    In that case, follow instructions in the "Standalone Build" section of
    the [build document](../../../BUILD.md#standalonebuild)
3.  Terminal 1 is running the Avalon Enclave Manager and Listener.
    Terminal 2 is running either the Docker container shell (recommended) or
    (for Standalone Builds) the Python virtual environment
4.  In Terminal 2 run `cd $TCF_HOME/examples/apps/generic_client`
5.  If you are running with Docker, then run this in Terminal 2:
    ``` bash
    ./generic_client.py --workload_id "heart-disease-eval" \
        --in_data "Data: 25 10 1 67 102 125 1 95 5 10 1 11 36 1" -o
    ```

     If you are running standalone, then run this in Terminal 2:
    ``` bash
    ./generic_client.py --workload_id "heart-disease-eval" \
         --uri "http://localhost:1947/" \
        --in_data "Data: 25 10 1 67 102 125 1 95 5 10 1 11 36 1" -o
    ```

6.  The data will be submitted to the worker and the results will appear
    shortly:
    ```
    [04:31:55 INFO    utility.utility] Decryption result at client -
    You have a 46% risk of heart disease.
    ```
7.  Optionally submit another request.

    Use the `--help` option to see other available options
8.  In Terminal 1, press Ctrl-c to stop the Avalon Enclave Manager and Listener

## Using the Heart Disease Evaluation GUI Client

The GUI client, `heart_gui.py` opens a X window on your display.
You must run this on your graphical console or a terminal emulator that
supports X Windows.

1.  If needed, in file `docker/Dockerfile` change `ENV DISPLAY`
    to the X Windows `$DISPLAY` value. By default, it is the console, `:0`
2.  If needed, also update the Ethereum account and direct registry contract
    information in `sdk/avalon_sdk/tcf_connector.toml`
3.  Follow instructions in the "Docker-based Build and Execution" section of
    the [build document](../../../BUILD.md#dockerbuild).

    As an alternative, you can run this in Standalone mode without Docker.
    In that case, follow instructions in the "Standalone Build" section of
    the [build document](../../../BUILD.md#standalonebuild)
4.  Terminal 1 is running the Avalon Enclave Manager and Listener.
    Terminal 2 is running either the Docker container shell (recommended) or
    (for Standalone Builds) the Python virtual environment
5.  In Terminal 2 run `cd $TCF_HOME/examples/apps/heart_disease_eval/client`
6.  In Terminal 2 install Python3's TKInter GUI library and the
    Pillow Imaging Library (PIL):
    ```bash
    sudo apt update; sudo apt -y install python3-tk python3-pil.imagetk
    pip3 install --upgrade pillow
    ```
7.  In Terminal 2 install the Solidity compiler:
    ```bash
    pip3 install --upgrade py-solc-x
    python3 -m solcx.install v0.5.15
    ```
8.  If your DISPLAY is not the local console, `:0`, you need to give access to
    your display from the GUI.
    Open a new terminal, Terminal 3, and run `xhost +`
9.  If you are running with Docker, then run in Terminal 2 `./heart_gui.py` .

    If you are running standalone, then run in Terminal 2
    `./heart_gui.py --service-uri "http://localhost:1947/"` .
    Use the `--help` option to see other available options
10. A new window will pop up with the GUI. See the screenshot below for an
    example.
11. Input all the heart disease evaluation values.
    Alternatively, check the "Input variables as string" box to input the
    values as a string of 14 integers separated by spaces. For example,
    `25 10 1 67 102 125 1 95 5 10 1 11 36 1` or
    `32 1 1 156 132 125 1 95 1 0 1 1 3 1`
12. Click the "Evaluate" button and a new window will appear with the
    heart disease evaluation result.
    The "View Request", "View Result", and "View Receipt" buttons will pop up
    windows displaying the raw JSON RPC files
13. Close the GUI windows when done
14. If you ran `xhost +` above, close access to your display with
    `xhost -` in Terminal 3
15. In Terminal 1, press Ctrl-c to stop the Avalon Enclave Manager and Listener

![Screenshot of heart_gui.py]( images/heart_gui_screenshot.jpg
  "Screenshot of heart_gui.py")
<br /> *Screenshot of heart_gui.py*
