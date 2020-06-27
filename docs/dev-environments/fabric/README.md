<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Testing Hyperledger Avalon with a Hyperledger Fabric blockchain

This is a self-contained environment based on Docker to test Avalon components
with a Hyperledger Fabric blockchain.
The set up supports Avalon's proxy model.

For a demonstration that runs Fabric and Avalon, see
[TestingFabricProxyModel.rst](../../TestingFabricProxyModel.rst)

## Setup and Launch

### Prerequisites

* [Docker](https://docs.docker.com/engine/install/ubuntu/) (18.03 or newer)
* git

### Stand up a Fabric network

The following process will stand up a fully functional
Fabric 2.0 network with 2 CA nodes, 4 peer nodes, and 3 orderer nodes:
```bash
curl -o minifab -sL https://tinyurl.com/twrt8zv && chmod +x minifab
./minifab up

```

The Fabric connection profile is at `vars/mychannel_connection.json`
which is needed for the application to connect to the Fabric network.


### Extract Avalon [chaincode](https://github.com/hyperledger/avalon/tree/master/sdk/avalon_sdk/connector/blockchains/fabric/chaincode) and deploy them on the Fabric network

```bash
./getandinstall.sh
```

### Run your tests

Once you have all the chaincode installed and connection profile available,
you can use
[Avalon Python connector library](https://github.com/hyperledger/avalon/tree/master/sdk/avalon_sdk/connector/blockchains/fabric)
to make Avalon API 1.1 calls.

Watch the
[demo](https://wiki.hyperledger.org/display/avalon/2020-02-11+Fabric+integration)
to learn more.
