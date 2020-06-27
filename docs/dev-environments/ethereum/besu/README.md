<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Local Environment for Testing Hyperledger Avalon with Hyperledger Besu

This is a self-contained environment based on Docker and deployed with
docker-compose to test Avalon components with a Hyperledger Besu target
blockchain.
The set up can be used with both direct mode and proxy mode,
with both HTTP and Websocket endpoints enabled.

For a demonstration that runs Besu and Avalon, see
[TestingBesuProxyModel.rst](../../../TestingBesuProxyModel.rst)

## Setup and Launch

### Prerequisites

To set up the local environment in order to run Avalon tests,
you need the following:

* [Docker](https://docs.docker.com/engine/install/ubuntu/) and
  [docker-compose](https://docs.docker.com/compose/install/#install-compose)
* node.js and npm
* [Truffle](https://www.trufflesuite.com/docs/truffle/getting-started/installation)

### Docker Images
Pull down the Docker images:

```bash
docker-compose pull
```

### Besu Blockchain
The Besu blockchain is now ready to be launched:

```bash
docker-compose up -d
```

The Ethereum RPC endpoints and websocket endpoints for the two Besu nodes are:

* `http://localhost:22001`
  * signing account: 0x7085d4d4c6efea785edfba5880bb62574e115626
* `ws://localhost:22002`
* `http://localhost:23001`
  * signing account: 0xb36b1934004385bfa5c51eaecb8ec348ec733ca8
* `ws://localhost:23002`
