<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Hyperledger Avalon Connector

These directories contain Hyperledger Avalon connector code, either
for blockchains (Avalon Proxy Model) or for working directly
with Avalon via JSON RPC (Avalon Direct Model).


**Directory [blockchains](./blockchains/)**

Blockchain implementations for the Avalon Connector.
- [Hyperledger Fabric](blockchains/fabric)
  is implemented in Python and Go Chaincode
- [Ethereum](blockchains/ethereum)
  is implemented in Python and Solidity Smart Contracts

**Directory [direct](./direct/)**

Avalon Direct Model implementation using JSON RPC, which communicates to
the Avalon Connector over the network using JSON RPC.

**Directory [interfaces](./interfaces/)**

Abstract base class to read and write the Avalon registries.
This class implemented for each supported blockchain (Proxy Model)
and directly with the Direct Model.

