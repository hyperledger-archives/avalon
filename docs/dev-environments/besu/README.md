# Local Environment for Testing Avalon with a Hyperledger Besu blockchain
This is a self-contained environment based on docker and deployed with docker-compose, to test Avalon components with a Hyperledger Besu target blockchain. The set up can be used with both direct mode and proxy mode, with both HTTP and Websocket endpoints enabled.

## Setup and Launch

### Pre-requisites
To set up the local environment in order to run Avalon tests, you need the following:
* docker
* node.js and npm
* [Truffle](https://www.trufflesuite.com/docs/truffle/getting-started/installation)

### Docker images
Pull down the docker images:

```
cd local
docker-compose pull
```

### Besu Blockchain
The Besu blockchain is ready to be launched:

```
docker-compose up -d
```

The Ethereum RPC endpoints and websocket endpoints for the two Besu nodes are:
* http://localhost:22001
  * signing account: 0x7085d4d4c6efea785edfba5880bb62574e115626
* ws://localhost:22002
* http://localhost:23001
  * signing account: 0xb36b1934004385bfa5c51eaecb8ec348ec733ca8
* ws://localhost:23002

