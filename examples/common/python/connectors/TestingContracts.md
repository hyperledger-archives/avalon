# Solidity Connector Test Process

1.  You have two choices for building TCF: Docker-based build (recommended) or
    standalone build.

    - For standalone builds, follow instructions in the
      "Standalone based Build" section of the
      the [build document](../../../../BUILD.md#standalonebuild).
      Then continue with the next step, step 2.

    - For Docker-based builds, follow instructions in the
      "Docker-based Build and Execution" section of the
      the [build document](../../../../BUILD.md#dockerbuild) through step 4
      (activating a virtual environment).
      Then continue with step 8, below.

2.  (standalone builds only) If needed, update the Ethereum account and
    direct registry contract information in `docker/Dockerfile.tcf-dev` and
    `examples/common/python/connectors/tcf_connector.toml`

3. (standalone builds only) Install Python 3.6.8 if not currently installed.
   Determine your Python version with `python3 --version` .
   If it is not installed, install it as follows:

    ```bash
    wget https://www.python.org/ftp/python/3.6.8/Python-3.6.8.tgz
    tar -xvf Python-3.6.8.tgz
    cd Python-3.6.8
    ./configure
    make
    sudo make install
    make sure
    ```

4. (standalone builds only) Install solc 0.4.25 to compile Solidity contracts
   from Python:
    ```bash
    python3 -m solc.install v0.4.25
    ```
    Set the Solidity compiler binary path, to make it accessible from Python:

    ```bash
    export SOLC_BINARY=~/.py-solc/solc-v0.4.25/bin/solc
    ```

5. (standalone builds only) To run smart contracts using a
   Ropsten network account, first install the MetaMask Chrome plugin
   to your Chrome web browser and create an account in the Ropsten network

6. (standalone builds only) After creating an account, make sure to add
   fake ether to the account using:

   - https://faucet.metamask.io/
   - https://blog.bankex.org/how-to-buy-ethereum-using-metamask-ccea0703daec

7. (standalone builds only) Export your private key:

   ```bash
   export WALLET_PRIVATE_KEY=<private_key>
   ```

8. Install web3.py, which is an Ethereum Python client that interacts
   with the Ethereum network. For more information about web3.py, see
   https://web3py.readthedocs.io/en/stable/quickstart.html

    ```bash
    sudo pip install web3
    ```

9.  Run `cd $TCF_HOME/examples/common/python/`

10. Deploy contracts with `python3 connectors/ethereum/eth_cli.py`

    - Fill in your Ropsten address in `eth_account`.
    - Fill in your your contract addresses
      `direct_registry_contract_address` and `worker_registry_contract_address`
      in `examples/common/python/connectors/tcf_connector.toml`

11. Test the DirectRegistry and WorkerRegistry contracts with:
   ```bash
   cd connectors/ethereum/unit_tests
   python3 test_ethereum_worker_registry_impl.py
   python3 test_ethereum_worker_registry_list_impl.py
   ```

