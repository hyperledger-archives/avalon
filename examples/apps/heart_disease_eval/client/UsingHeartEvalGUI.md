# Using the Heart Evaluation GUI Client

1. In `docker/Dockerfile.tcf-dev` set `ENV DISPLAY` to be `[IP Address of host]:0`

   If needed, also update the ethereum account and direct registry contract information in `docker/Dockerfile.tcf-dev`  and `examples/common/python/connectors/tcf_connector.toml`   
2. Follow instructions in the "Testing" section of the [build document](../../BUILD.md) up to step 2
3. In Terminal 2, run `cd $TCF_HOME/tests/clients`
4. Open a new terminal, Terminal 3.
5. In Terminal 3 run `xhost +`

   This will give access of your display to the virtual environment.
6. In Terminal 2, run `python3 heart_gui.py` (use the `--help` option to see other available options)
7. A new window will pop up, input all the heart evaluation values.
   
   Alternatively, check the "Input variables as string" box to input the values as a string of integers separated by spaces.
8. Click the "Evaluate" button, a new window will appear and the heart evaluation result will be displayed.
   
   The "View Request", "View Result", and "View Receipt" buttons will pop up windows dsiplaying the raw JSON RPC files.
9. Close the GUI windows when done and on Terminal 3 run `xhost -` to close access to your display.

