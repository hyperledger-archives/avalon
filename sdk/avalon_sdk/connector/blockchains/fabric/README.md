<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Fabric Connector Chaincode

These Fabric Chaincode functions, written in Go,
maintain various registries on the Fabric blockchain for Hyperledger Avalon.
Avalon updates or queries the Fabric-implemented registeries
from the Avalon blockchain connector written for Fabric.

**[chaincode/order/go/main.go](chaincode/order/go/main.go)**
- Implements Avalon  Work Order (WO) Registry
- Functions: get WO, get caller ID, init, submit WO, WO complete, WO get,
  get MSPID (membership service providers ID),
- Internal Fabric functions: invoke, process attributes, and main

**[chaincode/receipt/go/main.go](chaincode/receipt/go/main.go)**
- Implements Avalon Work Order Receipt Registry
- Functions: get, add, update, retrieve, update retrieve, query,
  lookup, lookup next
- Internal Fabric functions: invoke, process attributes, and main

**[chaincode/registry/go/main.go](chaincode/registry/go/main.go)**
- Implements Avalon Registry
- Functions are: get, add, update, set status, lookup, lookup next, retrieve,
  query
- Internal Fabric functions: invoke, process attributes, and main

**[chaincode/worker/go/main.go](chaincode/worker/go/main.go)**
- Implements Avalon Worker Registry
- Functions: worker register, update, set status, retrieve, query,
  lookup, lookup next
- Internal Fabric functions: invoke, process attributes, and main
