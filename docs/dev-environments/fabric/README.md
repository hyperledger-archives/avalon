# Testing Avalon with a Hyperledger Fabric blockchain
This is a self-contained environment based on docker to test Avalon components with
Hyperledger Fabric blockchain. The set up supports Avalon proxy mode.

## Setup and Launch

### Pre-requisites
* [docker](https://www.docker.com/) (18.03 or newer)
* git

### Stand up a Fabric network

The following process will stand up a full functional fabric 2.0 network with 2 ca nodes, 4 peer nodes and 3 orderer nodes
```
curl -o minifab -sL https://tinyurl.com/twrt8zv && chmod +x minifab
./minifab up

```

The Fabric connection profile is vars/mychannel_connection.json which is needed for application to connect to Fabric network


### Extract Avalon [chaincode](https://github.com/hyperledger/avalon/tree/master/sdk/avalon_sdk/fabric/chaincode) and deploy them on the Fabirc network

```
./getandinstall.sh
```


### Run your tests
Once you have all the chaincode installed and connection profile available, you can use [Avalon python connector libary](https://github.com/hyperledger/avalon/tree/master/sdk/avalon_sdk/fabric) to make Avalon API 1.1 calls.

Watch the [demo](https://wiki.hyperledger.org/display/avalon/2020-02-11+Fabric+integration) to learn more.

<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->