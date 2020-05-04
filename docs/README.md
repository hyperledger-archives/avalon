# Hyperledger Avalon Documentation

## Introduction
* [README](../README.md). Overview of Avalon and its source code
* [FAQ](./FAQ.rst). Frequently-asked questions with answers about Avalon
  * [Glossary](./FAQ.rst#glossary)
  * [Videos](./FAQ.rst#videos)
* [Avalon Proposal](
  https://wiki.hyperledger.org/pages/viewpage.action?pageId=16324764).
  Avalon Proposal, initial members, motivation, and proposed solutions
  (2019)
* ["Ecosystem Support for EEA Trusted Compute Specification v1.0 Improves
  Blockchain Privacy and Scalability"](
  https://software.intel.com/en-us/articles/ecosystem-support-for-eea-trusted-compute-specification-v10-improves-blockchain-privacy-and).
  Introductory blog by Michael Reed (2019)
* [Introduction to Hyperledger Avalon video (20:24)](
  https://youtu.be/YRXfzHzJVaU)

[![Introduction to Hyperledger Avalon video](../images/screenshot-introduction-to-hyperledger-avalon.jpg)](https://youtu.be/YRXfzHzJVaU)

## Community
* [Project Wiki](https://wiki.hyperledger.org/display/avalon/Hyperledger+Avalon)
* [RocketChat](https://chat.hyperledger.org/channel/avalon)
* [Email list](https://lists.hyperledger.org/g/avalon)
* [JIRA feature & bug tracking](
  https://jira.hyperledger.org/secure/RapidBoard.jspa?rapidView=241&view=planning.nodetail)

## Tutorial
* [Workload Application Tutorial](./workload-tutorial/)
* [Example Applications](../examples/apps/)

## Source Code
* [Avalon source code repository, https://github.com/hyperledger/avalon](
  https://github.com/hyperledger/avalon)
* [Building source code](../BUILD.md)
* [Example Avalon applications](../examples/apps/)
* [Contributing source code](../CONTRIBUTING.md)

## SDK Reference Manual
The [Hyperledger Avalon SDK Reference Manual](https://danintel.github.io/refman.pdf)
(also available as a [PDF](https://danintel.github.io/refman.pdf) file)
documents the SDK used to create worker order requestors (clients) and processors.

The Avalon SDK Reference Manual is generated with Doxygen.
To generate the Reference Manual, type the following:
```
cd $TCF_HOME/docs # this directory
sudo apt-get update
sudo apt-get install -y make doxygen texlive-full graphviz
make
```

Documentation generated will be here:
* ``$TCF_HOME/docs/refman/html/``HTML documentation
* ``$TCF_HOME/docs/refman/man/man3``man page documentation
* ``$TCF_HOME/docs/refman/latex``LaTeX documentation
* ``$TCF_HOME/docs/refman/refman.pdf``PDF documentation (generated from LaTex)



## Reference
* [_Hyperledger Avalon Architecture Overview_](
  https://github.com/hyperledger/avalon/blob/master/docs//avalon-arch.pdf).
  Overview of Avalon architecture by Eugene Yarmosh (2020)
* [ _Off-Chain Trusted Compute Specification_](
  https://entethalliance.github.io/trusted-computing/spec.html)
  defined by Enterprise Ethereum Alliance (EEA) Task Force
* [Cryptography](../common/cpp/crypto/README.md). Cryptographic primitives
  used, libraries used, and implementation
