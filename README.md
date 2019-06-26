<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

# Trusted Compute Framework 
The Trusted Compute Framework (TCF) enables privacy in blockchain transactions, moving intensive processing from a main blockchain to improve scalability and latency, and to support attested Oracles.

The Trusted Compute Specification was designed to help developers gain the benefits of computational trust and mitigate its drawbacks. In case of the Trusted Compute Framework a blockchain is used to enforce execution policies and ensure transaction auditability, while associated off-chain trusted compute resources execute transactions. By using trusted off-chain compute resources, a developer can accelerate throughput and improve data privacy.  

Preservation of the integrity of execution and the enforcement
of confidentiality guarantees come through the use of a Trusted Compute (TC) option, e.g. ZKP (Zero Knowledge Proof), MPC (Multi Party Compute), or HW based TEE (Trusted Execution Environment). While the approach will work with any TC option that guarantees integrity and confidentiality for code and data, our initial implementation uses Intel<sup>@</sup> Software Guard Extensions (SGX).

TCF leverages the existence of a distributed ledger to
 * Maintain a registry of the trusted workers (including their attestation info) 
 * Provide a mechanism for submitting work orders from a client(s) to a worker
 * Preserve a log of work order receipts and acknowledgments 

TCF uses Off-Chain Trusted Compute Specification defined by Enterprise Ethereum Alliance (EEA) Task Force as a starting point to apply a consistant and compatible approach to all supported blockchains.   

# Initial Committers
 * danintel (daniel.anderson@intel.com)
 * EugeneYYY (yevgeniy.y.yarmosh@intel.com)
 * Karthika (Karthika.murthy@intel.com)
 * manju956 (manjunath.a.c@intel.com)
 * manojgop (manoj.gopalakrishnan@intel.com)
 * ram-srini (Ramakrishna.srinivasamurthy@intel.com)
 * srinathduraisamy (srinath.duraisamy@intel.com)
 * TomBarnes (thomas.j.barnes@intel.com)


# Sponsor
Mic Bowman (mic.bowman@intel.com) - a TSC member


# License
Hyperledger Private Data Objects software is released under the Apache License
Version 2.0 software license. See the [license file](LICENSE) for more details.

Hyperledger Private Data Objects documentation is licensed under the Creative
Commons Attribution 4.0 International License. You may obtain a copy of the
license at: http://creativecommons.org/licenses/by/4.0/.
