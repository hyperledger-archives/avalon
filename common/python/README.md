<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

Purpose of Common Python Hyperledger Avalon Code
=============================================

The common/python directory contains Python source code shared by
untrusted and trusted (Intel SGX Enclave) Hyperledger Avalon code.

Source Directories
------------------

* `./` <br />
  Makefile and Python package module setup
* `config/` <br />
  Parses Avalon .toml configuration files
* `database/` <br />
  Connector code to a local or remote LMDB database
* `error_code/` <br />
  Avalon error code constants
* `listener/` <br />
  Avalon JRPC listener
* `utility/` <br />
  Avalon Utilities
  (hex conversion, JSON file I/O, JRPC error response, logger)
