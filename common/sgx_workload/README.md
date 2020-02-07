<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

Purpose of Common
-----------------
The common directory contains source code shared by trusted(SGX Enclave) code and different workloads(Example workloads).

Dependencies:
-------------
1. SGX SDK
https://software.intel.com/en-us/sgx-sdk/download

2. SGX OpenSSL library built from OpenSSL 1.1
https://github.com/intel/intel-sgx-ssl

Source Directories
------------------

Dir                     Content
---------------------   ------------------------------------------------------
`sgx/iohandler/`         \*.cpp,\*.h files are custom iohandlers which help workloads to
                        execute IO operations from SGX enclave

`sgx/workload/`         work_order_data.cpp,work_order_data.h files are wrapper files
                        for work order data   
                        workload_processor.cpp, workload_processor.h are workload processor
                        which overrides function exposed by work order interface and also facilitates
                        auto registration of workloads
