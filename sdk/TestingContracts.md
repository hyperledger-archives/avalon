# Solidity Connector Test Process

1.  You have two choices for building Avalon: Docker-based build (recommended)
    or standalone build.

    - For standalone builds, follow instructions in the
      "Standalone based Build" section of the
      the [build document](../BUILD.md#standalonebuild).
      Then continue with the next step, step 2.

    - For Docker-based builds, follow instructions in the
      "Docker-based Build and Execution" section of the
      the [build document](../BUILD.md#dockerbuild) through step 4
      (Docker container shell).
      Then continue with step 8, below.

2.  (Standalone builds only) If needed, update the Ethereum account and
    direct registry contract information in `sdk/avalon_sdk/tcf_connector.toml`

3.  (Standalone builds only) Install Python 3.6.8 if not currently installed.
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

4.  (Standalone builds only) Install the Solidity compiler to compile
    Solidity contracts from Python:
    ```bash
    pip3 install --upgrade py-solc-x
    python3 -m solcx.install v0.5.15
    ```

5.  (Standalone builds only) To run smart contracts using a
    Ropsten network account, first install the MetaMask Chrome plugin
    to your Chrome web browser and create an account in the Ropsten network

6.  (Standalone builds only) After creating an account, make sure to add
    fake ether to the account using:

    - https://faucet.metamask.io/
    - https://blog.bankex.org/how-to-buy-ethereum-using-metamask-ccea0703daec

7.  Install web3.py, which is an Ethereum Python client that interacts
    with the Ethereum network. For more information about web3.py, see
    https://web3py.readthedocs.io/en/stable/quickstart.html

    ```bash
    pip install web3
    ```

8.  Run `cd $TCF_HOME/examples/common/python/connectors/ethereum`

9.  Fill in your Ropsten testnet address in `eth_account` in
    `sdk/avalon_sdk/tcf_connector.toml`

10. Deploy solidity contracts to Ropsten network using `eth_cli.py`

    ```bash
    ./eth_cli.py
    ```

    The above command will display the contract instance address for
    `direct_registry_contract_address` and `worker_registry_contract_address`

11. Fill in your your contract addresses
      `direct_registry_contract_address` and `worker_registry_contract_address`
      in `sdk/avalon_sdk/tcf_connector.toml`

12. Test the DirectRegistry and WorkerRegistry contracts with:
    ```bash
    cd $TCF_HOME/examples/common/python/connectors/ethereum/unit_tests
    python3 test_ethereum_worker_registry_impl.py
    python3 test_ethereum_worker_registry_list_impl.py
    ```

13. Test echo workload using generic client with direct mode using Ropsten test network.
    ```bash
    cd $TCF_HOME/examples/apps/generic_client/
    ./generic_client.py -o --uri "http://localhost:1947" \
    --workload_id "echo-result" --in_data "Hello" --worker_id "singleton-worker-1"
    ```
