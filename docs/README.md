# Hyperledger Avalon Documentation

## Introduction
* [README](../README.md). Overview of Avalon and its source code
* [FAQ](./FAQ.rst). Frequently-asked questions with answers about Avalon
* [Proposal](
  https://wiki.hyperledger.org/pages/viewpage.action?pageId=16324764).
  Proposal of the project, members, motivation, proposed solutions, and FAQ
  (2019)
* ["Ecosystem Support for EEA Trusted Compute Specification v1.0 Improves
  Blockchain Privacy and Scalability"](
  https://software.intel.com/en-us/articles/ecosystem-support-for-eea-trusted-compute-specification-v10-improves-blockchain-privacy-and).
  Introductory blog by Michael Reed (2019)

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
* [_Hyperleder Avalon Architecture Overview_](
  https://github.com/hyperledger/avalon/blob/master/docs//avalon-arch.pdf).
  Overview of Avalon architecture by Eugene Yarmosh (2020)
* [ _Off-Chain Trusted Compute Specification_](
  https://entethalliance.github.io/trusted-computing/spec.html)
  defined by Enterprise Ethereum Alliance (EEA) Task Force
* [Cryptography](../common/cpp/crypto/README.md). Cryptographic primitives
  used, libraries used, and implementation
