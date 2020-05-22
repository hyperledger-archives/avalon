<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Ethereum Connector Smart Contracts

These Ethereum Smart Contract methods, written in Solidity,
maintain various registries on the Ethereum blockchain for Hyperledger Avalon.
Avalon updates or queries the Ethereum-implemented registeries
from the Avalon blockchain connector written for Ethereum.

**[contracts/LibSet.bytes32.sol](contracts/LibSet.bytes32.sol)**
- Implements low-level methods to get and set values from the
  Ethereum world state

**[contracts/WorkOrderReceiptRegistry.sol](contracts/WorkOrderReceiptRegistry.sol)**
- Implements Avalon Work Order Receipt Registry
- Methods: WO receipt create, update, retrieve, update and retrieve,
  lookup, lookup next
- Events: created, updated

**[contracts/WorkOrderRegistry.sol](contracts/WorkOrderRegistry.sol)**
- Implements Avalon Work Order (WO) Registry.
- Methods: WO create, update, retrieve, update and retrieve,
  lookup, lookup next
- Events: WO receipt created, updated

**[contracts/WorkerRegistry.sol](contracts/WorkerRegistry.sol)**
- Implements Avalon Worker Registry.
- Methods: worker register, update, set status, retrieve,
  lookup, lookup next

**[contracts/WorkerRegistryList.sol](contracts/WorkerRegistryList.sol)**
- Implements Avalon Registry of Registries. Methods:
  registry add, update, set status, retrieve, lookup, lookup next
- Events: registry add, update, set status
