<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

Unit Tests
----------
This test directory contains self-contained tests for python crypto files in
`common/crypto_utils/`.


Test Build and Execution
------------------------
1. Create and activate a Python virtual environment:
    ```bash
    python3 -m venv _dev
    source _dev/bin/activate
    ```
   If the virtual environment for the current shell session is activated,
   you will the see this prompt: `(_dev)`

2. To build the tests run `./run_test.sh `.

3. To execute the tests run `./run_test.sh test`.

4. To remove generated binaries run `./run_test.sh clean `.
    To deactivate the virtual environment type `deactivate`

Example
-------
```
$ ./run_test.sh
Collecting setuptools
...
Successfully installed avalon-sdk-0.5.0.dev1
Build complete
$ ./run_test.sh test
*****Running avalon crypto utils tests*****
****Executing unit test for crypto_utility.py****
PASSED: byte_array_to_hex()
PASSED: generate_random_string()
...
****Executing unit tests for signature.py****
PASSED: calculate_datahash
PASSED: generate_signature
...
****Finished executing unit test****
Signature PASSED all tests
$ ./run_test.sh clean
cleaning up binaries
...
find . -iname '__pycache__' -delete
```
