<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->
# Trusted Compute Framework

The Trusted Compute Framework (TCF) enables privacy in blockchain transactions,
moving intensive processing from a main blockchain to improve scalability and
latency, and to support attested Oracles.

The Trusted Compute Specification was designed to help developers gain the
benefits of computational trust and to mitigate its drawbacks. In the case of
the Trusted Compute Framework, a blockchain is used to enforce execution
policies and ensure transaction auditability, while associated off-chain
trusted compute resources execute transactions. By using trusted off-chain
compute resources, a developer can accelerate throughput and improve data
privacy.

Preservation of the integrity of execution and the enforcement
of confidentiality guarantees come through the use of a Trusted Compute (TC)
option, e.g. ZKP (Zero Knowledge Proof), MPC (Multi Party Compute),
or a hardware-based TEE (Trusted Execution Environment).
While the approach will work with any TC option that guarantees integrity and
confidentiality for code and data, our initial implementation uses
Intel® Software Guard Extensions (SGX).

TCF leverages the existence of a distributed ledger to
 * Maintain a registry of the trusted workers (including their attestation info)
 * Provide a mechanism for submitting work orders from a client(s) to a worker
 * Preserve a log of work order receipts and acknowledgments

TCF uses the
[ _Off-Chain Trusted Compute Specification_](https://entethalliance.github.io/trusted-computing/spec.html)
defined by Enterprise Ethereum Alliance (EEA) Task Force as a starting point to
apply a consistant and compatible approach to all supported blockchains.

## Initial Committers
* Manjunath A C (manju956)
* Daniel Anderson (danintel)
* Thomas J Barnes (TomBarnes)
* Srinath Duraisamy (srinathduraisamy)
* Manoj Gopalakrishnan (manojgop)
* Karthika Murthy (Karthika)
* Ramakrishna Srinivasamurthy (ram-srini)
* Yevgeniy Y. Yarmosh (EugeneYYY)

## Sponsor
* Mic Bowman (cmickeyb) - TSC member

## Building

To build TCF, follow instructions in the [build document](BUILD.md).

## Contributing

See the [contributing document](CONTRIBUTING.md)
for information on how to contribute and the guidelines for contributions.

## License
Hyperledger Trusted Compute Framework is released under the Apache License
Version 2.0 software license. See the [license file](LICENSE) for more details.

Hyperledger Trusted Compute Framework documentation is licensed under the
Creative Commons Attribution 4.0 International License. You may obtain a copy
of the license at: http://creativecommons.org/licenses/by/4.0/.

© Copyright 2019, Intel Corporation.
