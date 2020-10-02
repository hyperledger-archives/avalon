<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Avalon Worker Application Development Tutorial

- [Directory Structure](#directory)
- [Prerequisites](#prerequisites)
- [Phase 1: Avalon Plug-in Code](#phase1)
- [Phase 2: Worker-specific Code](#phase2)
- [Phase 3: Worker-specific Code
  to execute I/O operations inside the TEE](#phase3)

This tutorial describes how to build a trusted workload application.
We begin by copying template files to a new directory.
Then we show how to modify the files to create a workload application.

The example we create will be a workload application that takes a name as
input and echos back "Hello *name*".

[![Hyperledger Avalon Application Development video
](../../images/screenshot-hyperledger-avalon-application-development.jpg)
<br />*Video presentation (39:56)*](https://youtu.be/yKDFJH9J3IU)


## <a name="directory"></a>Directory Structure

Under directory `hello_world/` are the desired results of modifying the
template files, `hello_world/stage_1` and, with further modifications,
`hello_world/stage_2`

The directory structure for this tutorial is as follows:

* [README.md](README.md) This file
* [templates/](templates/) Templates to copy to create a workload application
  * [CMakeLists.txt](templates/CMakeLists.txt) CMake file to build this
    application
  * [logic.h](templates/logic.h) Header file defining worker-specific code
  * [logic.cpp](templates/logic.cpp) C file for worker-specific code
  * [plug-in.h](templates/plug-in.h) Header file defining generic plug-in code
  * [plug-in.cpp](templates/plug-in.cpp) C file for generic plug-in code
* [hello_world/](hello_world/) Example workload application
  * [stage_1/](hello_world/stage_1/) Intermediate results from modifying
    template files
    * [CMakeLists.txt](hello_world/stage_1/CMakeLists.txt) Modified to build
      worker
    * [logic.h](hello_world/stage_1/logic.h)
    * [logic.cpp](hello_world/stage_1/logic.cpp)
    * [plug-in.h](hello_world/stage_1/plug-in.h) Modified to define worker
      framework
    * [plug-in.cpp](hello_world/stage_1/plug-in.cpp)
  * [stage_2/](hello_world/stage_2/) Final results from adding worker code
    * [logic.h](hello_world/stage_2/logic.h) Modified with worker definitions
      added
    * [logic.cpp](hello_world/stage_2/logic.cpp) Modified with worker code added
    * [plug-in.cpp](hello_world/stage_2/plug-in.cpp) Modified to call worker

## <a name="prerequisites"></a>Prerequisites

Before beginning this tutorial, review the following items:

* Review the base class `WorkloadProcessor`,
  which any workload class inherits, at
  [$TCF_HOME/common/sgx_workload/workload/workload_processor.h](../../common/sgx_workload/workload/workload_processor.h)

  Observe the following:
  * Each workload must implement method `ProcessWorkOrder()`
    (see file [templates/plug-in.cpp](templates/plug-in.cpp))
  * Each workload class definition must include the macro
    `IMPL_WORKLOAD_PROCESSOR_CLONE()`.
    This macro clones an instance of class `WorkloadProcessor` for a worker
    (see file [templates/plug-in.h](templates/plug-in.h))
  * Each workload class implementation must include the macro
    ` REGISTER_WORKLOAD_PROCESSOR()`.
    This macro registers a workload processor for a specific application.
    It associates a string with a workload.
    This is the same string that is passed in the work order request
    JSON payload
    (see file [templates/plug-in.cpp](templates/plug-in.cpp))

* Review the generic command line client at
  [$TCF_HOME/examples/apps/generic_client/](../../examples/apps/generic_client/)
  * This component is optional, but it can be useful because it allows early
    testing of the workload without first creating a custom requester
    application
  * The client application accepts only strings as input parameters and
    assumes that all outputs are also provided as strings.
    If other data types are needed (numbers, binaries), then create
    a custom test application
    (potentially by modifying this application)
  * The Workload ID (`hello-world`) and input parameters (a name string)
    sent by the client must match the workload requirements for this worker

* Review how to build Avalon at [$TCF_HOME/BUILD.md](../../BUILD.md)

As a best practice, this tutorial separates the actual workload-specific logic
from the Avalon plumbing required to link the workload to the Avalon framework
into separate files.


This tutorial creates a workload application in three phases:
1. [Create generic plug-in logic](#phase1)
2. [Incrementally add workload-specific logic](#phase2)
3. (optional) [Incrementally add I/O operations inside the TEE](#phase3)

### <a name="phase1"></a>Phase 1: Avalon Plug-in Code

For the first phase copy and modify template code to create the plug-in code.
This code contains Avalon framework code to invoke worker-specific logic that
will be created next in [Phase 2](#phase2).

* From the top-level Avalon source repository directory, `$TCF_HOME`,
  create a new workload directory and change into it:
  ```bash
  cd $TCF_HOME
  mkdir -p examples/apps/hello_world/workload
  cd examples/apps/hello_world/workload
  ```

* Copy five template files to the newly-created directory:
  ```bash
  cp ../../../../docs/workload-tutorial/templates/* .
  ```

* Change placeholders `$NameSpace$` (two locations) in file `plug-in.h`
  to an appropriate workload class name, `HelloWorld`

* Change placeholder `$WorkloadId$` (one location) in file `plug-in.h` to an
  appropriate workload ID, `hello-world` (note the dash, `-`)

* Change placeholder `$WORKLOAD_STATIC_NAME$` (one location)
  in file `CMakeLists.txt`
  to an appropriate name, `hello_world` (note the underscore, `_`)

  Make sure the `$WORKLOAD_STATIC_NAME$` is same as workload folder created above using
  `mkdir -p examples/apps/<workload_name>/workload`

* To include the new workload into the build,
  add this line to the end of
  [$TCF_HOME/examples/apps/CMakeLists.txt](../../examples/apps/CMakeLists.txt) :

  ```
  ADD_SUBDIRECTORY(hello_world/workload)
  ```

* To link the new workload library into the build, change below lines in
  [$TCF_HOME/tc/sgx/trusted_worker_manager/enclave/CMakeWorkloads.txt](../../tc/sgx/trusted_worker_manager/enclave/CMakeWorkloads.txt) :

  Add workload to supported workload list
  ```bash
    MACRO(CREATE_SUPPORTED_WORKLOADS_LIST)
        ...
        ...
        # LIST(SUPPORTED_WORKLOADS_LIST "<workload_id>")
    ENDMACRO()
  ```

  Replace `<workload_id>`  with `hello-world` as shown below:
  ```bash
    MACRO(CREATE_SUPPORTED_WORKLOADS_LIST)
        ...
        ...
        LIST(SUPPORTED_WORKLOADS_LIST "hello-world")
    ENDMACRO()
  ```

  Add workload static library to supported workload library list
  ```bash
    MACRO(CREATE_SUPPORTED_WORKLOAD_LIBRARY_LIST)
        ...
        ...
        # LIST(APPEND SUPPORTED_WORKLOAD_LIBRARY_LIST "<workload_lib_name>")
    ENDMACRO()
  ```

  Replace `<workload_lib_name>`  with `hello_world` as shown below:
  ```bash
    MACRO(CREATE_SUPPORTED_WORKLOADS_LIST)
        ...
        ...
        LIST(SUPPORTED_WORKLOADS_LIST "hello_world")
    ENDMACRO()
  ```

* Update the `WORKLOADS` build argument in
  [avalon-pool.yaml](../../docker/compose/avalon-pool.yaml)
  if running a
  worker pool setup using Docker. The work order processing enclave (WPE)
  should be built with workloads the worker pool supports. After updating,
  the argument should look like:
  ```bash
  WORKLOADS=echo-result;heart-disease-eval;inside-out-eval;simple-wallet;hello-world
  ```
  You could have any number (one or more) of workloads in this list. This is
  especially useful when multiple worker pools are running together and there
  is a workload isolation with each pool running different set of workloads.
  Refer to
  [avalon-multi-pool.yaml](../../docker/compose/avalon-multi-pool.yaml)
  for multiple pools.

* Change to the top-level Avalon source repository directory, `$TCF_HOME`,
  and rebuild the framework (see [$TCF_HOME/BUILD.md](../../BUILD.md)).
  It should now include the new workload

* From the `$TCF_HOME` directory, load the framework and use the
  generic command line utility to test the newly-added workload:
  ```bash
  examples/apps/generic_client/generic_client.py -o \
      --workload_id "hello-world" --in_data "Dan" \
      --worker_id "kme-worker-1"

  ```

  If you are running Docker, run the utility from a Docker shell
  specifying the Avalon Listener container:
  ```bash
  docker exec -it avalon-shell bash

  examples/apps/generic_client/generic_client.py -o \
      --uri "http://avalon-listener:1947" \
      --workload_id "hello-world" --in_data "Dan" \
      --worker_id "kme-worker-1"
  ```


* The Hello World worker should return the string `Error: under construction`
  as the result (hard-coded placeholder string in `plug-in.cpp`):
  ```
  [17:35:06 INFO    utility.utility]
  Decryption result at client - Error: under construction
  [17:35:06 INFO    __main__]
  Decrypted response:
   [{'index': 0, 'dataHash':
     '60AEBCFC13614F392352DC5683486C05F5519C927FA35DC254204CA0E5045348',
     'data': 'Error: under construction', 'encryptedDataEncryptionKey': '',
     'iv': ''}]
  ```

To see what the updated source files should look like, refer to the files in
directory
[$TCF_HOME/docs/workload-tutorial/hello_world/stage_1/](hello_world/stage_1/).


### <a name="phase2"></a>Phase 2: Worker-specific Code

Now that we have Avalon plug-in framework code, we incrementally add
worker-specific logic and call it from the plug-in code.
As a best practice, we separate worker-specific logic from the
Avalon framework code that calls it into separate files.
In this example we name the worker-specific function `ProcessHelloWorld()`.

* Change back into the "Hello World" workload directory:
  ```bash
  cd $TCF_HOME/examples/apps/hello_world/workload
  ```

* Add the `ProcessHelloWorld()` function definition to `logic.h`:
  ```cpp
  extern std::string ProcessHelloWorld(std::string in_str);
  ```

* Add the `ProcessHelloWorld()` function implementation to `logic.cpp`
  ```cpp
  std::string ProcessHelloWorld(std::string in_str) {
      return "Hello " + in_str;
  }
  ```

  For this example, the worker-specific logic is trivial. Usually
  the logic is much more complex so it is in a separate file to
  separate it from Avalon-specific plug-in code

* Modify the `ProcessWorkOrder()` method in `plug-in.cpp`
  to call `ProcessHelloWorld()`. That is, change:

  ```cpp
  // Replace the dummy implementation below with invocation of
  // actual logic defined in logic.h and implemented in logic.cpp.
  std::string result_str("Error: under construction");
  ByteArray ba(result_str.begin(), result_str.end());
  AddOutput(0, out_work_order_data, ba);
  ```
  to

  ```cpp
  // For each work order, process the input data
  for (auto wo_data : in_work_order_data) {
      std::string result_str =
          ProcessHelloWorld(ByteArrayToString(wo_data.decrypted_data));

     ByteArray ba(result_str.begin(), result_str.end());
     AddOutput(wo_data.index, out_work_order_data, ba);
  }

  ```
  After these changes, the workload will prepend "Hello " to each input data
  item and will return each resulting string as a separate output data item.


* Change to the top-level Avalon source repository directory, `$TCF_HOME`,
  and rebuild the framework (see [$TCF_HOME/BUILD.md](../../BUILD.md)).
  It should now include the new workload

* Load the framework and use the generic command line utility to test the
  newly-added workload:
  ```bash
  examples/apps/generic_client/generic_client.py -o \
      --workload_id "hello-world" --in_data "Jane" "Dan" \
      --worker_id "kme-worker-1"
  ```

  If you are running Docker, run the utility from a Docker shell
  specifying the Avalon Listener container:
  ```bash
  docker exec -it avalon-shell bash

  examples/apps/generic_client/generic_client.py -o \
      --uri "http://avalon-listener:1947" \
      --workload_id "hello-world" --in_data "Jane" "Dan" \
      --worker_id "kme-worker-1"
  ```

* The Hello World worker should return a string
  `Hello name` where `name` is the string sent in the first
  input parameter
  ```
  [17:47:48 INFO    utility.utility] Decryption result at client - Hello Dan
  [17:47:48 INFO    __main__]
  Decrypted response:
  [{'index': 0, 'dataHash':
    '02D0D64CA3F5BC43B29304DA25AE9D240A48DE0374C3296A564CE55FB63E0B8C',
    'data': 'Hello Dan', 'encryptedDataEncryptionKey': '', 'iv': ''}]
  ```

To see what the updated source files should look like, refer to the files in
directory
[$TCF_HOME/docs/workload-tutorial/hello_world/stage_2/](hello_world/stage_2/).

### <a name="phase3"></a>Phase 3: Worker-specific Code to execute I/O operations inside the TEE
This phase of tutorial extends the helloworld worker
with "inside out file I/O" handling capability.
"Inside out file I/O" refers to reading and writing files outside the
TEE (Trusted Execution Environment) from within the TEE.

For the first input request from the client, the workload echoes the user
name along with the encryption key.
For subsequent requests, the client submits a input request
with an encryption key received in the previous step.
As a response, the client receives an echo of username along with the
workload hit count or number of workload invocations by that user.
The counter value is stored in encrypted format in a file outside the enclave,
with file writes encrypted, and file reads decrypted.

The protocol is as follows:
* For the first request, the client needs to submit the user name as `in_data`.
* As a response, client receives the message
  `Hello <username> <encryption_key_in_hex>`.
* For the subsequent requests from the same user, the client needs to submit
  a username along with the encryption key obtained in the previous step.
* As a response, the client receives the message
  `Hello <username> <workload_hit_count>`.

The directory structure for this tutorial is as follows:

* [hello_world/](hello_world/)
  * [stage_3/](hello_world/stage_3/) Results from adding Inside Out I/O code
    * [logic.h](hello_world/stage_1/logic.h) Modified with worker
      function definition added
    * [CMakeLists.txt](hello_world/stage_3/CMakeLists.txt) CMake file with
      new include directory added to build this application
    * [io_helper.h](hello_world/stage_3/io_helper.h) Header file defining
      Inside Out I/O helper
    * [io_helper.cpp](hello_world/stage_3/io_helper.cpp) C file for
      Inside Out I/O helper code, which invokes the inside out I/O
      functionality
    * [logic.h](hello_world/stage_3/logic.h) Header file with new
      `GetCountOrKey()` definition
    * [logic.cpp](hello_world/stage_3/logic.cpp) C file with new
      `GetCountOrKey()` function and modified `ProcessHelloWorld` function

For this phase, follow these steps to extend the worker functionality:

* Change to the "Hello World" workload directory
  ```bash
  cd $TCF_HOME/examples/apps/hello_world/workload
  ```
* Add a line to `CMakeLists.txt` to add a new include directory
  ```bash
  TARGET_INCLUDE_DIRECTORIES(${WORK_ORDER_STATIC_NAME} PUBLIC $ENV{TCF_HOME}/common/cpp/crypto)
  ```
* Copy the Inside Out I/O source files
  ```bash
  cp ../../../../docs/workload-tutorial/hello_world/stage_3/io_helper.* .
  ```
  Examine file [`io_helper.cpp`](hello_world/stage_3/io_helper.cpp) .
  Notice that it calls the inside out I/O
  functions `Read()`, `Write()`, and `Delete()`, which are defined in file
  [$TCF_HOME/common/sgx_workload/iohandler/file_io_wrapper.h
  ](../../common/sgx_workload/iohandler/file_io_wrapper.h) ,
  and that it performs encryption and decryption of the file contents

* Add the following to the beginning of file `logic.cpp` :
  ```cpp
  #include "io_helper.h"

  #define USER_FILES_PATH "/tmp/tutorial/"
  ```

* Modify the ProcessHelloWorld() function in `logic.cpp`. That is, change:

  ```cpp
  std::string ProcessHelloWorld(std::string in_str) {
      return "Hello " + in_str;
  }
  ```

to

  ```cpp
  std::string ProcessHelloWorld(std::string in_str) {
      std::string name;
      std::string hex_key;

      std::size_t pos = in_str.find(':');
      if (pos == std::string::npos) {
          name = in_str;
      } else { // split name and key
          name = in_str.substr(0, pos);
          hex_key = in_str.substr(pos + 1, in_str.length() - pos - 1);
      }

      return "Hello " + name + ", your result is " +
          GetCountOrKey(name, hex_key);
  } // ProcessHelloWorld
 ```

* Add the `GetCountOrKey()` function implementation to `logic.cpp`
  ```cpp
  std::string GetCountOrKey(std::string name, std::string hex_key) {
      std::string file_path = USER_FILES_PATH + name;
      IoHelper io_helper(file_path);
      std::string ret_str;

      if (hex_key.empty()) {
          io_helper.DeleteFile();
          // Generate symmetric hex key
          ret_str = io_helper.GenerateKey();
          io_helper.SetKey(ret_str);
          io_helper.WriteFile("1");
      } else { // read, increment, and write count
          io_helper.SetKey(hex_key);
          if (io_helper.ReadFile(ret_str) == 0) {
              size_t count = std::stoul(ret_str);
              count++;
              ret_str = std::to_string(count);
              io_helper.WriteFile(ret_str);
          }
      }

      return ret_str;
  } // GetCountOrKey
  ```

* Add the `GetCountOrKey()` function declaration to `logic.h`
  ```cpp
  extern std::string GetCountOrKey(std::string name, std::string hex_key);
  ```

* Change to the top-level Avalon source repository directory,
  `$TCF_HOME`, and rebuild the Avalon framework
  (see [$TCF_HOME/BUILD.md](../../BUILD.md)).
  It should build the updated hello_world workload

* Start the Avalon framework
  (see "Testing" in [$TCF_HOME/BUILD.md](../../BUILD.md#testing))

* Create a directory to store files for persistent storage of
  values outside the TEE
  ```bash
  mkdir /tmp/tutorial
  ```

  If you are running Docker, make the directory inside the
  Avalon Enclave Manager container:
  ```bash
  sudo docker exec -it avalon-enclave-manager bash

  mkdir /tmp/tutorial
  ```

* Submit a work order request with user name `jack`

  ```bash
  examples/apps/generic_client/generic_client.py -o \
      --workload_id "hello-world" --in_data "jack" \
      --worker_id "kme-worker-1"
  ```

  If you are running Docker, run the utility from the Docker shell
  container specifying the Avalon Listener container:
  ```bash
  sudo docker exec -it avalon-shell bash

  examples/apps/generic_client/generic_client.py -o \
      --uri "http://avalon-listener:1947" \
      --workload_id "hello-world" --in_data "jack" \
      --worker_id "kme-worker-1"
  ```

* The Hello World worker should return the string
  `Hello <name> your result is <key>` where `<name>`
  is the string sent in the input parameter and
  `<key>` is the file encryption key.
  This will create an encrypted file named `/tmp/tutorial/<name>`

  ```
  [10:29:35 INFO    crypto_utils.crypto_utility]
  Decryption result at client -
  Hello jack
  [8342EFBE7C379231A4E03C80E5BA1AC9E8ACBC5338976CE6146431D8CBF2318D]
  [10:29:35 INFO    __main__]
  Decrypted response:
    [{'index': 0, 'dataHash':
      '5493B8B39AFE2F7D4F1490D6E04AD410E394958C6BD85324BC28B540EDF0A462',
      'data': 'Hello jack, your result is
      8342EFBE7C379231A4E03C80E5BA1AC9E8ACBC5338976CE6146431D8CBF2318D',
      'encryptedDataEncryptionKey': '', 'iv': ''}]
  ```

* Verify the file `jack` was created outside the TEE and is encrypted and
  hex-encoded:
  ```bash
  ls /tmp/tutorial
  cat /tmp/tutorial/jack
  ```

  For Docker:
  ```bash
  sudo docker exec -it avalon-enclave-manager bash

  ls /tmp/tutorial
  cat /tmp/tutorial/jack
  ```

* Submit a work order request with user name `jack` and the encryption key
  received in the above step separated by a colon `:`. For example,
  with the above key:

  ```bash
  examples/apps/generic_client/generic_client.py -o \
      --workload_id "hello-world" --in_data \
      "jack:8342EFBE7C379231A4E03C80E5BA1AC9E8ACBC5338976CE6146431D8CBF2318D" \
      --worker_id "kme-worker-1"
  ```
  For Docker:
  ```bash
  sudo docker exec -it avalon-shell bash
  examples/apps/generic_client/generic_client.py -o \
      --uri "http://avalon-listener:1947" \
      --workload_id "hello-world" --in_data \
      "jack:8342EFBE7C379231A4E03C80E5BA1AC9E8ACBC5338976CE6146431D8CBF2318D" \
      --worker_id "kme-worker-1"
  ```
* The Hello World worker should return the string
  `Hello <name>, your result is <count>`
  where `<count>` is the number of times
  the workload has been invoked by the user `<name>`.

  ```
  [10:36:46 INFO    crypto_utils.crypto_utility]
  Decryption result at client - Hello jack [2]
  [10:36:46 INFO    __main__]
  Decrypted response:
    [{'index': 0, 'dataHash':
      'D040AFA0D78276BAFD1360A6170D7EB53446731F25E0F77343A07EEE3628731A',
      'data': 'Hello jack, your result is 2',
      'encryptedDataEncryptionKey': '', 'iv': ''}]
  ```

To see what the updated source files should look like,
refer to the files in directory
[$TCF_HOME/docs/workload-tutorial/hello_world/stage_3/](hello_world/stage_3/).
