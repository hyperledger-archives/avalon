# Avalon Worker Application Development Tutorial

This tutorial describes how to build a trusted workload application.
We begin by copying template files to a new directory.
Then we show how to modify the files to create a workload application.

The example we create will be a workload application that takes a name as
input and echos back "Hello *name*".

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
    * [logic.h](hello_world/stage_1/logic.h) Modified with worker definitions
      added
    * [logic.cpp](hello_world/stage_1/logic.cpp) Modified with worker code added
    * [plug-in.cpp](hello_world/stage_1/plug-in.cpp) Modified to call worker

## Prerequisites

Before beginning this tutorial, review the following items:

* Review the base class `WorkloadProcessor`,
  which any workload class inherits, at
  [$TCF_HOME/common/sgx_workload/workload_processor.h](../../common/sgx_workload/workload_processor.h)

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

## Tutorial

This tutorial creates a workload application in two phases:
1. [Create generic plug-in logic](#phase1)
2. [Incrementally add workload-specific logic](#phase2)

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

* Change placeholder `$WORKLOAD_STATIC_NAME$` in file `CMakeLists.txt`
  to an appropriate name, `hello_world` (note the underscore, `_`)

* To include the new workload into the build,
  add this line to the end of
  [$TCF_HOME/examples/apps/CMakeLists.txt](../../examples/apps/CMakeLists.txt) :

  ```
  ADD_SUBDIRECTORY(hello_world/workload)
  ```

* To link the new workload library into the build, add these lines to
  the end of
  [$TCF_HOME/tc/sgx/trusted_worker_manager/enclave/CMakeLists.txt](../../tc/sgx/trusted_worker_manager/enclave/CMakeLists.txt) :
  ```bash
  # Add $WORKLOAD_STATIC_NAME$ workload
  SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-L,${TCF_TOP_DIR}/examples/apps/build/$WORKLOAD_STATIC_NAME$/workload")
  TARGET_LINK_LIBRARIES(${PROJECT_NAME} -Wl,--whole-archive -l$WORKLOAD_STATIC_NAME$ -Wl,--no-whole-archive)
  ```
  Replace `$WORKLOAD_STATIC_NAME$` with `hello_world` so it becomes:
  ```bash
  # Add hello_world workload
  SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-L,${TCF_TOP_DIR}/examples/apps/build/hello_world/workload")
  TARGET_LINK_LIBRARIES(${PROJECT_NAME} -Wl,--whole-archive -lhello_world -Wl,--no-whole-archive)
  ```

* Change to the top-level Avalon source repository directory, `$TCF_HOME`,
  and rebuild the framework (see [$TCF_HOME/BUILD.md](../../BUILD.md)).
  It should now include the new workload

* From the `$TCF_HOME` directory, load the framework and use the
  generic command line utility to test the newly-added workload:
  ```bash
  examples/apps/generic_client/generic_client.py \
      --workload_id "hello-world" --in_data "Jane" "Dan"
  ```

  > **_NOTE:_** If you are running Avalon in a container you can shell into the container like this:
  ```bash
  docker exec -it tcf bash
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
  to call `ProcessHelloWorld()`.  That is, change:

  ```cpp
  // Replace the dummy implementation below with invocation of
  // actual logic defined in logic.h and implemented in logic.cpp.
  std::string result_str("Error: under construction");
  ByteArray ba(result_str.begin(), result_str.end());
  AddOutput(0, out_work_order_data, ba);
  ```
  to

  ```cpp
  for (auto wo_data : in_work_order_data) {
     // Process the input data
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
  examples/apps/generic_client/generic_client.py
      --uri "http://localhost:1947" --workload_id "hello-world" --in_data "Dan"
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

