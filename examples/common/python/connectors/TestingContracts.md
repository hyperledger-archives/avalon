# Test Process

1. Installing Python 3.6.8

    ```bash
    wget https://www.python.org/ftp/python/3.6.8/Python-3.6.8.tgz
    tar -xvf Python-3.6.8.tgz
    cd Python-3.6.8
    ./configure
    make
    sudo make install
    make sure
    ```

2. Install web3.py an Ethereum python client interact with Ethereum network(About web3.py - https://web3py.readthedocs.io/en/stable/quickstart.html)

    ```bash
    sudo pip install web3
    ```

3. Install solc to compile solidity contract from python

    ```bash
    python3 -m solc.install v0.4.25
    ```

4. Set the solidity compiler binary path, so that it is accessible in python program

    ```bash
    export SOLC_BINARY=~/.py-solc/solc-v0.4.25/bin/solc
    ```

5. Running smart contract using ropsten network account
Install meta mask chrome plugin and create account in ropsten network.
After creating account make sure to add fake ether to account using

    - https://faucet.metamask.io/
    - https://blog.bankex.org/how-to-buy-ethereum-using-metamask-ccea0703daec

    Expose your private key:

    ```bash
    export WALLET_PRIVATE_KEY=<private_key>
    ```

    Deploy contracts:

    ```bash
    python3 connectors/ethereum/eth_cli.py
    ```

    Fill in your own ropsten address `eth_account` and contract addresses `direct_registry_contract_address`,`worker_registry_contract_address` in `tcf_connector.toml`

    Then, test DirectRegistry and WorkerRegistry contract:

    ```bash
    cd connectors/ethereum/unit_tests
    python3 test_ethereum_worker_registry_impl.py
    python3 test_ethereum_worker_registry_list_impl.py
    ```
